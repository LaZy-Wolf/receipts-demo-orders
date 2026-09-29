from datetime import datetime
from typing import Generic, Literal, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    size: int
    pages: int


class ProductIn(BaseModel):
    sku: str = Field(min_length=1, max_length=64)
    name: str = Field(min_length=1, max_length=200)
    category: str = Field(min_length=1, max_length=64)
    price_cents: int = Field(ge=0)
    stock: int = Field(default=0, ge=0)


class ProductPatch(BaseModel):
    price_cents: int | None = Field(default=None, ge=0)
    stock: int | None = Field(default=None, ge=0)
    active: bool | None = None


class ProductOut(ProductIn):
    model_config = ConfigDict(from_attributes=True)

    id: int
    active: bool


class CustomerIn(BaseModel):
    email: str = Field(pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    name: str = Field(min_length=1, max_length=200)


class CustomerOut(CustomerIn):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


class CouponIn(BaseModel):
    code: str = Field(min_length=1, max_length=32)
    kind: Literal["percent", "fixed"]
    value: int = Field(ge=0)
    min_order_cents: int = Field(default=0, ge=0)
    expires_at: datetime | None = None


class CouponOut(CouponIn):
    model_config = ConfigDict(from_attributes=True)

    id: int
    active: bool


class OrderItemIn(BaseModel):
    product_id: int
    quantity: int = Field(ge=1, le=1000)


class OrderIn(BaseModel):
    customer_id: int
    items: list[OrderItemIn] = Field(min_length=1)
    coupon_code: str | None = None


class OrderItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    product_id: int
    quantity: int
    unit_price_cents: int


class OrderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    customer_id: int
    status: str
    coupon_code: str | None
    items: list[OrderItemOut]
    subtotal_cents: int
    discount_cents: int
    shipping_cents: int
    tax_cents: int
    total_cents: int
    created_at: datetime


class StatusChange(BaseModel):
    status: Literal["pending", "paid", "shipped", "delivered", "cancelled"]
