from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import services
from ..db import get_session
from ..models import Order
from ..pagination import paginate
from ..schemas import OrderIn, OrderOut, Page, StatusChange

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("", response_model=OrderOut, status_code=201)
def create_order(payload: OrderIn, request: Request, session: Session = Depends(get_session)):
    return services.create_order(session, payload, request.app.state.settings)


@router.get("", response_model=Page[OrderOut])
def list_orders(
    customer_id: int | None = None,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1),
    session: Session = Depends(get_session),
):
    stmt = select(Order).order_by(Order.id)
    if customer_id is not None:
        stmt = stmt.where(Order.customer_id == customer_id)
    return paginate(session, stmt, page, size, OrderOut)


@router.get("/{order_id}", response_model=OrderOut)
def get_order(order_id: int, session: Session = Depends(get_session)):
    return services.get_order(session, order_id)


@router.post("/{order_id}/status", response_model=OrderOut)
def change_status(order_id: int, payload: StatusChange, session: Session = Depends(get_session)):
    return services.change_status(session, order_id, payload.status)


@router.post("/{order_id}/cancel", response_model=OrderOut)
def cancel_order(order_id: int, session: Session = Depends(get_session)):
    return services.cancel_order(session, order_id)
