from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from . import inventory, pricing, status
from .config import Settings
from .db import utcnow
from .errors import Conflict, CouponError, NotFound
from .models import Coupon, Customer, Order, OrderItem, Product
from .schemas import OrderIn


def find_coupon(session: Session, code: str) -> Coupon | None:
    return session.scalar(select(Coupon).where(Coupon.code == code.strip().upper()))


def create_order(session: Session, payload: OrderIn, settings: Settings, now: datetime | None = None) -> Order:
    now = now or utcnow()
    if session.get(Customer, payload.customer_id) is None:
        raise NotFound(f"customer {payload.customer_id} not found")

    coupon = None
    if payload.coupon_code:
        coupon = find_coupon(session, payload.coupon_code)
        if coupon is None:
            raise CouponError(f"unknown coupon {payload.coupon_code!r}")

    quantities: dict[int, int] = {}
    for item in payload.items:
        quantities[item.product_id] = quantities.get(item.product_id, 0) + item.quantity

    order = Order(customer_id=payload.customer_id, coupon_code=coupon.code if coupon else None)
    lines = []
    for product_id, quantity in quantities.items():
        product = session.get(Product, product_id)
        if product is None:
            raise NotFound(f"product {product_id} not found")
        inventory.reserve(product, quantity)
        order.items.append(OrderItem(product_id=product_id, quantity=quantity, unit_price_cents=product.price_cents))
        lines.append((product.price_cents, quantity))

    totals = pricing.price_order(lines, coupon, settings, now)
    order.subtotal_cents = totals.subtotal_cents
    order.discount_cents = totals.discount_cents
    order.shipping_cents = totals.shipping_cents
    order.tax_cents = totals.tax_cents
    order.total_cents = totals.total_cents
    session.add(order)
    session.commit()
    session.refresh(order)
    return order


def get_order(session: Session, order_id: int) -> Order:
    order = session.get(Order, order_id)
    if order is None:
        raise NotFound(f"order {order_id} not found")
    return order


def change_status(session: Session, order_id: int, new_status: str) -> Order:
    if new_status == "cancelled":
        return cancel_order(session, order_id)
    order = get_order(session, order_id)
    status.ensure_transition(order.status, new_status)
    order.status = new_status
    session.commit()
    session.refresh(order)
    return order


def cancel_order(session: Session, order_id: int) -> Order:
    order = get_order(session, order_id)
    if order.status == "cancelled":
        raise Conflict(f"order {order_id} is already cancelled")
    order.status = "cancelled"
    session.commit()
    session.refresh(order)
    return order
