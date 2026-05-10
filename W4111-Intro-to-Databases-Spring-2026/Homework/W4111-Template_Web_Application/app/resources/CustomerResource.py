from __future__ import annotations

import os
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, Field

from .AbstractBaseResource import AbstractBaseResource
from ..services.MySQLDataService import MySQLDataService


class Customer(BaseModel):
    customerNumber: int | None = None
    customerName: str = ""
    contactLastName: str = ""
    contactFirstName: str = ""
    phone: str = ""
    addressLine1: str = ""
    addressLine2: str | None = None
    city: str = ""
    state: str | None = None
    postalCode: str | None = None
    country: str = ""
    salesRepEmployeeNumber: int | None = None
    creditLimit: float | None = None


class CustomerCollection(BaseModel):
    items: list[Customer] = Field(default_factory=list)


def _mysql_connection_config() -> dict[str, Any]:
    return {
        "host": os.getenv("MYSQL_HOST", "127.0.0.1"),
        "port": int(os.getenv("MYSQL_PORT", "3306")),
        "user": os.getenv("MYSQL_USER", "root"),
        "password": os.getenv("MYSQL_PASSWORD", ""),
        "database": os.getenv("MYSQL_DATABASE", "classicmodels"),
    }


class CustomerResource(AbstractBaseResource):
    def __init__(self, config: dict | None = None) -> None:
        cfg = dict(config or {})
        super().__init__(cfg)
        service_config = {
            **_mysql_connection_config(),
            "table": "customers",
            "primary_key_columns": ["customerNumber"],
            "integer_primary_key_columns": ["customerNumber"],
        }
        self._service = MySQLDataService(service_config)

    def get(self, template: dict) -> CustomerCollection:
        rows = self._service.retrieveByTemplate(template)
        return CustomerCollection(items=[Customer.model_validate(r) for r in rows])

    def get_by_id(self, id: str) -> Customer:  # noqa: A002
        row = self._service.retrieveByPrimaryKey(str(id))
        if not row:
            raise ValueError(f"No customer with customerNumber {id!r}")
        return Customer.model_validate(row)

    def post(self, new_data: Customer) -> str:
        data = new_data.model_dump(exclude_none=False)
        for field in (
            "customerName",
            "contactLastName",
            "contactFirstName",
            "phone",
            "addressLine1",
            "city",
            "country",
        ):
            if not str(data.get(field) or "").strip():
                raise ValueError(f"Missing or empty required field: {field}")
        cid = data.get("customerNumber")
        if cid is None:
            data["customerNumber"] = self._service.next_integer_primary_key("customerNumber")
        return self._service.create(self._payload_for_db(data))

    def delete(self, id: str) -> int:  # noqa: A002
        return self._service.deleteByPrimaryKey(str(id))

    def put(self, character_id: str, new_data: Customer) -> int:
        existing = self._service.retrieveByPrimaryKey(str(character_id))
        if not existing:
            raise ValueError(f"No customer with customerNumber {character_id!r}")
        patch = new_data.model_dump(exclude_unset=True)
        patch.pop("customerNumber", None)
        merged = {**existing, **patch}
        merged["customerNumber"] = int(character_id)
        return self._service.updateByPrimaryKey(str(character_id), self._payload_for_db(merged))

    @staticmethod
    def _payload_for_db(data: dict[str, Any]) -> dict[str, Any]:
        out: dict[str, Any] = {}
        for k, v in data.items():
            if v is None and k not in (
                "addressLine2",
                "state",
                "postalCode",
                "salesRepEmployeeNumber",
                "creditLimit",
            ):
                continue
            if k == "creditLimit" and v is not None:
                out[k] = Decimal(str(v))
            else:
                out[k] = v
        return out
