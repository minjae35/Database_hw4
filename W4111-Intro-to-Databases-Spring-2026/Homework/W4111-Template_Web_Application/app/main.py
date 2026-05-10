from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

load_dotenv()

if __package__ in (None, ""):
    sys.path.append(str(Path(__file__).resolve().parents[1]))
    from app.resources.CustomerResource import (
        Customer,
        CustomerCollection,
        CustomerResource,
    )
    from app.resources.HarryPotterResource import (
        HarryPotterCharacter,
        HarryPotterCollection,
        HarryPotterResource,
    )
    from app.resources.OrderDetailsResource import (
        OrderDetail,
        OrderDetailCollection,
        OrderDetailsResource,
    )
    from app.resources.OrderResource import Order, OrderCollection, OrderResource
else:
    from .resources.CustomerResource import (
        Customer,
        CustomerCollection,
        CustomerResource,
    )
    from .resources.HarryPotterResource import (
        HarryPotterCharacter,
        HarryPotterCollection,
        HarryPotterResource,
    )
    from .resources.OrderDetailsResource import (
        OrderDetail,
        OrderDetailCollection,
        OrderDetailsResource,
    )
    from .resources.OrderResource import Order, OrderCollection, OrderResource


def _get_app_name() -> str:
    return os.getenv("APP_NAME", "Starter FastAPI App")


app = FastAPI(title=_get_app_name(), version="0.1.0")
harry_potter_resource = HarryPotterResource()
customer_resource = CustomerResource()
order_resource = OrderResource()
order_details_resource = OrderDetailsResource()


class EchoRequest(BaseModel):
    message: str


def _http_exc_from_value_error(exc: ValueError) -> HTTPException:
    """Missing target row -> 404; invalid input / DB constraint (wrapped) -> 400."""
    msg = str(exc)
    if msg.startswith("No ") or msg.startswith("no "):
        return HTTPException(status_code=404, detail=msg)
    return HTTPException(status_code=400, detail=msg)


@app.get("/", tags=["root"])
def read_root() -> dict[str, str]:
    return {"message": "Hello from FastAPI"}


@app.get("/health", tags=["health"])
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/echo", tags=["echo"])
def echo(payload: EchoRequest) -> EchoRequest:
    return payload


# --- Harry Potter (starter sample) ---


@app.get("/harry-potter", tags=["harry-potter"])
def get_harry_potter_characters(
    first_name: str | None = None,
    last_name: str | None = None,
    house_name: str | None = None,
) -> HarryPotterCollection:
    template: dict = {}
    if first_name is not None:
        template["first_name"] = first_name
    if last_name is not None:
        template["last_name"] = last_name
    if house_name is not None:
        template["house_name"] = house_name
    return harry_potter_resource.get(template)


@app.get("/harry-potter/{character_id}", tags=["harry-potter"])
def get_harry_potter_character_by_id(character_id: str) -> HarryPotterCharacter:
    try:
        return harry_potter_resource.get_by_id(character_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/harry-potter", tags=["harry-potter"])
def create_harry_potter_character(new_data: HarryPotterCharacter) -> str:
    new_id = harry_potter_resource.post(new_data)
    return str(new_id)


@app.put("/harry-potter/{character_id}", tags=["harry-potter"])
def update_harry_potter_character(
    character_id: str, new_data: HarryPotterCharacter
) -> dict[str, int]:
    try:
        updated = harry_potter_resource.put(character_id, new_data)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"updated": updated}


@app.delete("/harry-potter/{character_id}", tags=["harry-potter"])
def delete_harry_potter_character(character_id: str) -> dict[str, int]:
    deleted = harry_potter_resource.delete(character_id)
    return {"deleted": deleted}


# --- Customers ---


@app.get("/customers", tags=["customers"])
def list_customers(
    customerNumber: int | None = None,
    customerName: str | None = None,
    contactLastName: str | None = None,
    contactFirstName: str | None = None,
    phone: str | None = None,
    addressLine1: str | None = None,
    city: str | None = None,
    state: str | None = None,
    postalCode: str | None = None,
    country: str | None = None,
    salesRepEmployeeNumber: int | None = None,
    creditLimit: float | None = None,
) -> CustomerCollection:
    template: dict = {}
    if customerNumber is not None:
        template["customerNumber"] = customerNumber
    if customerName is not None:
        template["customerName"] = customerName
    if contactLastName is not None:
        template["contactLastName"] = contactLastName
    if contactFirstName is not None:
        template["contactFirstName"] = contactFirstName
    if phone is not None:
        template["phone"] = phone
    if addressLine1 is not None:
        template["addressLine1"] = addressLine1
    if city is not None:
        template["city"] = city
    if state is not None:
        template["state"] = state
    if postalCode is not None:
        template["postalCode"] = postalCode
    if country is not None:
        template["country"] = country
    if salesRepEmployeeNumber is not None:
        template["salesRepEmployeeNumber"] = salesRepEmployeeNumber
    if creditLimit is not None:
        template["creditLimit"] = creditLimit
    try:
        return customer_resource.get(template)
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/customers", tags=["customers"])
def create_customer(new_data: Customer) -> str:
    try:
        return customer_resource.post(new_data)
    except ValueError as exc:
        raise _http_exc_from_value_error(exc) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/customers/{customerNumber}", tags=["customers"])
def get_customer(customerNumber: int) -> Customer:
    try:
        return customer_resource.get_by_id(str(customerNumber))
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.put("/customers/{customerNumber}", tags=["customers"])
def update_customer(customerNumber: int, new_data: Customer) -> dict[str, int]:
    try:
        updated = customer_resource.put(str(customerNumber), new_data)
    except ValueError as exc:
        raise _http_exc_from_value_error(exc) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return {"updated": updated}


@app.delete("/customers/{customerNumber}", tags=["customers"])
def delete_customer(customerNumber: int) -> dict[str, int]:
    try:
        deleted = customer_resource.delete(str(customerNumber))
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    if deleted == 0:
        raise HTTPException(status_code=404, detail=f"No customer with customerNumber {customerNumber}")
    return {"deleted": deleted}


# --- Orders ---


@app.get("/orders", tags=["orders"])
def list_orders(
    orderNumber: int | None = None,
    customerNumber: int | None = None,
    status: str | None = None,
) -> OrderCollection:
    template: dict = {}
    if orderNumber is not None:
        template["orderNumber"] = orderNumber
    if customerNumber is not None:
        template["customerNumber"] = customerNumber
    if status is not None:
        template["status"] = status
    try:
        return order_resource.get(template)
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/orders", tags=["orders"])
def create_order(new_data: Order) -> str:
    try:
        return order_resource.post(new_data)
    except ValueError as exc:
        raise _http_exc_from_value_error(exc) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/orders/{orderNumber}", tags=["orders"])
def get_order(orderNumber: int) -> Order:
    try:
        return order_resource.get_by_id(str(orderNumber))
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.put("/orders/{orderNumber}", tags=["orders"])
def update_order(orderNumber: int, new_data: Order) -> dict[str, int]:
    try:
        updated = order_resource.put(str(orderNumber), new_data)
    except ValueError as exc:
        raise _http_exc_from_value_error(exc) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return {"updated": updated}


@app.delete("/orders/{orderNumber}", tags=["orders"])
def delete_order(orderNumber: int) -> dict[str, int]:
    try:
        deleted = order_resource.delete(str(orderNumber))
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    if deleted == 0:
        raise HTTPException(status_code=404, detail=f"No order with orderNumber {orderNumber}")
    return {"deleted": deleted}


# --- Order details ---


@app.get("/orderdetails", tags=["orderdetails"])
def list_order_details(
    orderNumber: int | None = None,
    productCode: str | None = None,
    quantityOrdered: int | None = None,
    orderLineNumber: int | None = None,
) -> OrderDetailCollection:
    template: dict = {}
    if orderNumber is not None:
        template["orderNumber"] = orderNumber
    if productCode is not None:
        template["productCode"] = productCode
    if quantityOrdered is not None:
        template["quantityOrdered"] = quantityOrdered
    if orderLineNumber is not None:
        template["orderLineNumber"] = orderLineNumber
    try:
        return order_details_resource.get(template)
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/orderdetails", tags=["orderdetails"])
def create_order_detail(new_data: OrderDetail) -> str:
    try:
        return order_details_resource.post(new_data)
    except ValueError as exc:
        raise _http_exc_from_value_error(exc) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/orders/{orderNumber}/orderdetails", tags=["orderdetails"])
def list_order_details_for_order(orderNumber: int) -> OrderDetailCollection:
    try:
        return order_details_resource.get({"orderNumber": orderNumber})
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get(
    "/orders/{orderNumber}/orderdetails/{productCode}",
    tags=["orderdetails"],
)
def get_order_detail(orderNumber: int, productCode: str) -> OrderDetail:
    key = OrderDetailsResource.composite_key(orderNumber, productCode)
    try:
        return order_details_resource.get_by_id(key)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.put(
    "/orders/{orderNumber}/orderdetails/{productCode}",
    tags=["orderdetails"],
)
def update_order_detail(
    orderNumber: int, productCode: str, new_data: OrderDetail
) -> dict[str, int]:
    key = OrderDetailsResource.composite_key(orderNumber, productCode)
    try:
        updated = order_details_resource.put(key, new_data)
    except ValueError as exc:
        raise _http_exc_from_value_error(exc) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return {"updated": updated}


@app.delete(
    "/orders/{orderNumber}/orderdetails/{productCode}",
    tags=["orderdetails"],
)
def delete_order_detail(orderNumber: int, productCode: str) -> dict[str, int]:
    key = OrderDetailsResource.composite_key(orderNumber, productCode)
    try:
        deleted = order_details_resource.delete(key)
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    if deleted == 0:
        raise HTTPException(
            status_code=404,
            detail=f"No order detail for orderNumber={orderNumber}, productCode={productCode!r}",
        )
    return {"deleted": deleted}


if __name__ == "__main__":
    import uvicorn

    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))

    uvicorn.run(app, host=host, port=port)
