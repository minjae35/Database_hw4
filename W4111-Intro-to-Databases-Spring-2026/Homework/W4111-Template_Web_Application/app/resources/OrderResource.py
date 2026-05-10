from __future__ import annotations

from datetime import date
from typing import Any

from pydantic import BaseModel, Field

from .AbstractBaseResource import AbstractBaseResource
from .CustomerResource import _mysql_connection_config
from ..services.MySQLDataService import MySQLDataService


class Order(BaseModel):
    orderNumber: int | None = None
    orderDate: date | None = None
    requiredDate: date | None = None
    shippedDate: date | None = None
    status: str = ""
    comments: str | None = None
    customerNumber: int | None = None


class OrderCollection(BaseModel):
    items: list[Order] = Field(default_factory=list)


class OrderResource(AbstractBaseResource):
    def __init__(self, config: dict | None = None) -> None:
        cfg = dict(config or {})
        super().__init__(cfg)
        service_config = {
            **_mysql_connection_config(),
            "table": "orders",
            "primary_key_columns": ["orderNumber"],
            "integer_primary_key_columns": ["orderNumber"],
        }
        self._service = MySQLDataService(service_config)

    def get(self, template: dict) -> OrderCollection:
        rows = self._service.retrieveByTemplate(template)
        return OrderCollection(items=[Order.model_validate(r) for r in rows])

    def get_by_id(self, id: str) -> Order:  # noqa: A002
        row = self._service.retrieveByPrimaryKey(str(id))
        if not row:
            raise ValueError(f"No order with orderNumber {id!r}")
        return Order.model_validate(row)

    def post(self, new_data: Order) -> str:
        data = new_data.model_dump(exclude_none=False)
        oid = data.get("orderNumber")
        if oid is None:
            data["orderNumber"] = self._service.next_integer_primary_key("orderNumber")
        for key in ("orderDate", "requiredDate"):
            if data.get(key) is None:
                raise ValueError(f"Missing required field {key}")
        if data.get("customerNumber") is None:
            raise ValueError("Missing required field customerNumber")
        if not str(data.get("status", "")).strip():
            raise ValueError("Missing required field status")
        return self._service.create(self._payload_for_db(data))

    def delete(self, id: str) -> int:  # noqa: A002
        return self._service.deleteByPrimaryKey(str(id))

    def put(self, character_id: str, new_data: Order) -> int:
        existing = self._service.retrieveByPrimaryKey(str(character_id))
        if not existing:
            raise ValueError(f"No order with orderNumber {character_id!r}")
        patch = new_data.model_dump(exclude_unset=True)
        patch.pop("orderNumber", None)
        merged = {**existing, **patch}
        merged["orderNumber"] = int(character_id)
        return self._service.updateByPrimaryKey(str(character_id), self._payload_for_db(merged))

    @staticmethod
    def _payload_for_db(data: dict[str, Any]) -> dict[str, Any]:
        return dict(data)
