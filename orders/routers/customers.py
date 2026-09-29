from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import get_session
from ..errors import Conflict, NotFound
from ..models import Customer
from ..schemas import CustomerIn, CustomerOut

router = APIRouter(prefix="/customers", tags=["customers"])


@router.post("", response_model=CustomerOut, status_code=201)
def create_customer(payload: CustomerIn, session: Session = Depends(get_session)):
    existing = session.scalar(select(Customer).where(Customer.email == payload.email))
    if existing is not None:
        raise Conflict("email already registered")
    customer = Customer(email=payload.email.lower(), name=payload.name)
    session.add(customer)
    session.commit()
    session.refresh(customer)
    return customer


@router.get("/{customer_id}", response_model=CustomerOut)
def get_customer(customer_id: int, session: Session = Depends(get_session)):
    customer = session.get(Customer, customer_id)
    if customer is None:
        raise NotFound(f"customer {customer_id} not found")
    return customer
