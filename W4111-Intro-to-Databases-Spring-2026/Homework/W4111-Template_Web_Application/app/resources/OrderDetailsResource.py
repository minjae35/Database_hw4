from __future__ import annotations

from decimal import Decimal
from typing import Any

from pydantic import BaseModel, Field

from .AbstractBaseResource import AbstractBaseResource
from .CustomerResource import _mysql_connection_config
from ..services.MySQLDataService import MySQLDataService


class OrderDetail(BaseModel):
    orderNumber: int | None = None
    productCode: str = ""
    quantityOrdered: int | None = None
    priceEach: float | None = None
    orderLineNumber: int | None = None


class OrderDetailCollection(BaseModel):
    items: list[OrderDetail] = Field(default_factory=list)


class OrderDetailsResource(AbstractBaseResource):
    def __init__(self, config: dict | None = None) -> None:
        cfg = dict(config or {})
        super().__init__(cfg)
        service_config = {
            **_mysql_connection_config(),
            "table": "orderdetails",
            "primary_key_columns": ["orderNumber", "productCode"],
            "integer_primary_key_columns": ["orderNumber"],
        }
        self._service = MySQLDataService(service_config)

    @staticmethod
    def composite_key(order_number: int, product_code: str) -> str:
        return f"{int(order_number)}|{product_code.strip()}"

    def get(self, template: dict) -> OrderDetailCollection:
        rows = self._service.retrieveByTemplate(template)
        return OrderDetailCollection(items=[OrderDetail.model_validate(r) for r in rows])

    def get_by_id(self, id: str) -> OrderDetail:  # noqa: A002
        row = self._service.retrieveByPrimaryKey(str(id))
        if not row:
            raise ValueError(f"No order detail with key {id!r}")
        return OrderDetail.model_validate(row)

    def post(self, new_data: OrderDetail) -> str:
        data = new_data.model_dump(exclude_none=False)
        if data.get("orderNumber") is None:
            raise ValueError("orderNumber is required")
        if not str(data.get("productCode", "")).strip():
            raise ValueError("productCode is required")
        if data.get("quantityOrdered") is None:
            raise ValueError("quantityOrdered is required")
        if data.get("priceEach") is None:
            raise ValueError("priceEach is required")
        on = int(data["orderNumber"])
        if data.get("orderLineNumber") is None:
            data["orderLineNumber"] = self._service.next_order_line_number(on)
        return self._service.create(self._payload_for_db(data))

    def delete(self, id: str) -> int:  # noqa: A002
        return self._service.deleteByPrimaryKey(str(id))

    def put(self, character_id: str, new_data: OrderDetail) -> int:
        existing = self._service.retrieveByPrimaryKey(str(character_id))
        if not existing:
            raise ValueError(f"No order detail with key {character_id!r}")
        patch = new_data.model_dump(exclude_unset=True)
        patch.pop("orderNumber", None)
        patch.pop("productCode", None)
        merged = {**existing, **patch}
        merged["orderNumber"] = existing["orderNumber"]
        merged["productCode"] = existing["productCode"]
        return self._service.updateByPrimaryKey(str(character_id), self._payload_for_db(merged))

    @staticmethod
    def _payload_for_db(data: dict[str, Any]) -> dict[str, Any]:
        out: dict[str, Any] = {}
        for k, v in data.items():
            if v is None:
                continue
            if k == "priceEach":
                out[k] = Decimal(str(v))
            else:
                out[k] = v
        return out
