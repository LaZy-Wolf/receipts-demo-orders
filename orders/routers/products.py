from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..db import get_session
from ..errors import Conflict, NotFound
from ..models import Product
from ..pagination import paginate
from ..schemas import Page, ProductIn, ProductOut, ProductPatch

router = APIRouter(prefix="/products", tags=["products"])


@router.get("", response_model=Page[ProductOut])
def list_products(
    q: str | None = None,
    category: str | None = None,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1),
    session: Session = Depends(get_session),
):
    stmt = select(Product).where(Product.active.is_(True)).order_by(Product.name)
    if category:
        stmt = stmt.where(Product.category == category)
    if q:
        stmt = select(Product).where(Product.name.ilike(f"%{q}%")).order_by(Product.name)
    return paginate(session, stmt, page, size, ProductOut)


@router.post("", response_model=ProductOut, status_code=201)
def create_product(payload: ProductIn, session: Session = Depends(get_session)):
    product = Product(**payload.model_dump())
    session.add(product)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise Conflict(f"sku {payload.sku!r} already exists")
    session.refresh(product)
    return product


@router.get("/{product_id}", response_model=ProductOut)
def get_product(product_id: int, session: Session = Depends(get_session)):
    product = session.get(Product, product_id)
    if product is None:
        raise NotFound(f"product {product_id} not found")
    return product


@router.patch("/{product_id}", response_model=ProductOut)
def update_product(product_id: int, payload: ProductPatch, session: Session = Depends(get_session)):
    product = session.get(Product, product_id)
    if product is None:
        raise NotFound(f"product {product_id} not found")
    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(product, field, value)
    session.commit()
    session.refresh(product)
    return product
