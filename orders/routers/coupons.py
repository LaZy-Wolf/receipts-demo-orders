from fastapi import APIRouter, Depends, Query
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..db import get_session, utcnow
from ..errors import Conflict, NotFound
from ..models import Coupon
from ..pricing import coupon_discount
from ..schemas import CouponIn, CouponOut
from ..services import find_coupon

router = APIRouter(prefix="/coupons", tags=["coupons"])


@router.post("", response_model=CouponOut, status_code=201)
def create_coupon(payload: CouponIn, session: Session = Depends(get_session)):
    data = payload.model_dump()
    data["code"] = data["code"].strip().upper()
    if data["expires_at"] is not None and data["expires_at"].tzinfo is not None:
        data["expires_at"] = data["expires_at"].replace(tzinfo=None) - payload.expires_at.utcoffset()
    coupon = Coupon(**data)
    session.add(coupon)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise Conflict(f"coupon {data['code']!r} already exists")
    session.refresh(coupon)
    return coupon


@router.get("/{code}/validate")
def validate_coupon(code: str, subtotal_cents: int = Query(ge=0), session: Session = Depends(get_session)):
    """Quick check used by the checkout page before the order is placed."""
    coupon = find_coupon(session, code)
    if coupon is None:
        raise NotFound(f"unknown coupon {code!r}")
    if not coupon.active:
        return {"valid": False, "reason": "coupon is not active"}
    if coupon.expires_at is not None and coupon.expires_at < utcnow():
        return {"valid": False, "reason": "coupon has expired"}
    if subtotal_cents < coupon.min_order_cents:
        return {"valid": False, "reason": "order total below coupon minimum"}
    return {"valid": True, "discount_cents": coupon_discount(coupon, subtotal_cents)}
