from __future__ import annotations

from decimal import Decimal
from typing import Any

import pymysql
from pymysql import Error as PyMySQLError
from pymysql.cursors import DictCursor
from pymysql.err import IntegrityError

from .AbstractBaseDataService import AbstractBaseDataService


class MySQLDataService(AbstractBaseDataService):
    """
    MySQL persistence implementing AbstractBaseDataService.

    Config keys:
      - host, port, user, password, database (connection)
      - table: str
      - primary_key_columns: list[str] (one column or composite, e.g. orderNumber + productCode)
      - integer_primary_key_columns: optional list[str] — columns to coerce to int in PK strings
    """

    def __init__(self, config: dict) -> None:
        super().__init__(config)
        self._table = str(config["table"])
        self._pk_columns: list[str] = list(config["primary_key_columns"])
        self._int_pk_cols: set[str] = set(config.get("integer_primary_key_columns", []))

    def _connect(self) -> pymysql.connections.Connection:
        try:
            return pymysql.connect(
                host=str(self.config.get("host", "127.0.0.1")),
                port=int(self.config.get("port", 3306)),
                user=str(self.config.get("user", "")),
                password=str(self.config.get("password", "")),
                database=str(self.config.get("database", "classicmodels")),
                cursorclass=DictCursor,
                autocommit=False,
            )
        except PyMySQLError as exc:
            raise RuntimeError(f"MySQL connection failed: {exc}") from exc

    @staticmethod
    def _normalize_row(row: dict[str, Any]) -> dict[str, Any]:
        out: dict[str, Any] = {}
        for k, v in row.items():
            if isinstance(v, Decimal):
                out[k] = float(v)
            else:
                out[k] = v
        return out

    def _decode_primary_key(self, primary_key: str) -> dict[str, Any]:
        if len(self._pk_columns) == 1:
            col = self._pk_columns[0]
            raw = primary_key.strip()
            if col in self._int_pk_cols:
                return {col: int(raw)}
            return {col: raw}
        if "|" not in primary_key:
            raise ValueError("Composite primary key must be orderNumber|productCode")
        left, right = primary_key.split("|", 1)
        return {"orderNumber": int(left.strip()), "productCode": right.strip()}

    def retrieveByPrimaryKey(self, primary_key: str) -> dict:
        try:
            conds = self._decode_primary_key(primary_key)
        except ValueError:
            return {}
        where_sql = " AND ".join(f"`{c}` = %s" for c in self._pk_columns)
        values = [conds[c] for c in self._pk_columns]
        sql = f"SELECT * FROM `{self._table}` WHERE {where_sql} LIMIT 1"
        try:
            with self._connect() as conn:
                with conn.cursor() as cur:
                    cur.execute(sql, values)
                    row = cur.fetchone()
                    if not row:
                        return {}
                    return self._normalize_row(dict(row))
        except PyMySQLError as exc:
            raise RuntimeError(f"Database error: {exc}") from exc

    def retrieveByTemplate(self, template: dict) -> list[dict]:
        if not template:
            sql = f"SELECT * FROM `{self._table}`"
            values: list[Any] = []
        else:
            clauses = [f"`{k}` = %s" for k in template]
            sql = f"SELECT * FROM `{self._table}` WHERE " + " AND ".join(clauses)
            values = list(template.values())
        try:
            with self._connect() as conn:
                with conn.cursor() as cur:
                    cur.execute(sql, values)
                    rows = cur.fetchall() or []
                    return [self._normalize_row(dict(r)) for r in rows]
        except PyMySQLError as exc:
            raise RuntimeError(f"Database error: {exc}") from exc

    def create(self, payload: dict) -> str:
        if not payload:
            raise ValueError("Payload cannot be empty")
        cols = list(payload.keys())
        placeholders = ", ".join(["%s"] * len(cols))
        col_sql = ", ".join(f"`{c}`" for c in cols)
        sql = f"INSERT INTO `{self._table}` ({col_sql}) VALUES ({placeholders})"
        values = [payload[c] for c in cols]
        try:
            with self._connect() as conn:
                with conn.cursor() as cur:
                    cur.execute(sql, values)
                    conn.commit()
        except IntegrityError as exc:
            raise ValueError(f"Invalid create: {exc}") from exc
        except PyMySQLError as exc:
            raise RuntimeError(f"Database error: {exc}") from exc

        if len(self._pk_columns) == 1:
            col = self._pk_columns[0]
            if col in payload and payload[col] is not None:
                return str(payload[col])
            raise ValueError("Primary key missing after insert")
        o = payload.get("orderNumber")
        p = payload.get("productCode")
        if o is None or p is None:
            raise ValueError("Composite primary key fields missing after insert")
        return f"{int(o)}|{str(p)}"

    def updateByPrimaryKey(self, primary_key: str, payload: dict) -> int:
        if not payload:
            return 0
        try:
            pk_vals = self._decode_primary_key(primary_key)
        except ValueError:
            return 0
        assignments = [f"`{k}` = %s" for k in payload if k not in pk_vals]
        if not assignments:
            return 0
        set_clause = ", ".join(assignments)
        where_sql = " AND ".join(f"`{c}` = %s" for c in self._pk_columns)
        params: list[Any] = [payload[k] for k in payload if k not in pk_vals]
        params.extend(pk_vals[c] for c in self._pk_columns)
        sql = f"UPDATE `{self._table}` SET {set_clause} WHERE {where_sql}"
        try:
            with self._connect() as conn:
                with conn.cursor() as cur:
                    cur.execute(sql, params)
                    conn.commit()
                    return int(cur.rowcount)
        except PyMySQLError as exc:
            if exc.args and exc.args[0] in (1452, 1264, 1366):
                raise ValueError(f"Invalid update: {exc}") from exc
            raise RuntimeError(f"Database error: {exc}") from exc

    def deleteByPrimaryKey(self, primary_key: str) -> int:
        try:
            pk_vals = self._decode_primary_key(primary_key)
        except ValueError:
            return 0
        where_sql = " AND ".join(f"`{c}` = %s" for c in self._pk_columns)
        params = [pk_vals[c] for c in self._pk_columns]
        sql = f"DELETE FROM `{self._table}` WHERE {where_sql}"
        try:
            with self._connect() as conn:
                with conn.cursor() as cur:
                    cur.execute(sql, params)
                    conn.commit()
                    return int(cur.rowcount)
        except PyMySQLError as exc:
            raise RuntimeError(f"Database error: {exc}") from exc

    def next_integer_primary_key(self, column: str) -> int:
        sql = f"SELECT COALESCE(MAX(`{column}`), 0) + 1 AS n FROM `{self._table}`"
        try:
            with self._connect() as conn:
                with conn.cursor() as cur:
                    cur.execute(sql)
                    row = cur.fetchone()
                    return int(row["n"]) if row else 1
        except PyMySQLError as exc:
            raise RuntimeError(f"Database error: {exc}") from exc

    def next_order_line_number(self, order_number: int) -> int:
        sql = (
            f"SELECT COALESCE(MAX(`orderLineNumber`), 0) + 1 AS n "
            f"FROM `{self._table}` WHERE `orderNumber` = %s"
        )
        try:
            with self._connect() as conn:
                with conn.cursor() as cur:
                    cur.execute(sql, (order_number,))
                    row = cur.fetchone()
                    return int(row["n"]) if row else 1
        except PyMySQLError as exc:
            raise RuntimeError(f"Database error: {exc}") from exc
