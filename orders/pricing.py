from dataclasses import dataclass
from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal

from .config import Settings
from .errors import CouponError
from .models import Coupon


@dataclass(frozen=True)
class Totals:
    subtotal_cents: int
    discount_cents: int
    shipping_cents: int
    tax_cents: int

    @property
    def total_cents(self) -> int:
        return self.subtotal_cents - self.discount_cents + self.shipping_cents + self.tax_cents


def subtotal(lines: list[tuple[int, int]]) -> int:
    """Sum of unit_price_cents * quantity."""
    return sum(price * qty for price, qty in lines)


def check_coupon(coupon: Coupon, subtotal_cents: int, now: datetime) -> None:
    if not coupon.active:
        raise CouponError("coupon is not active")
    if coupon.expires_at is not None and coupon.expires_at < now:
        raise CouponError("coupon has expired")
    if not subtotal_cents > coupon.min_order_cents:
        raise CouponError("order total below coupon minimum")


def coupon_discount(coupon: Coupon, subtotal_cents: int) -> int:
    if coupon.kind == "percent":
        return subtotal_cents * coupon.value // 100
    return min(coupon.value, subtotal_cents)


def shipping(discounted_cents: int, settings: Settings) -> int:
    return 0 if discounted_cents >= settings.free_shipping_threshold_cents else settings.flat_shipping_cents


def tax(amount_cents: int, rate: Decimal) -> int:
    return int((Decimal(amount_cents) * rate).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def price_order(lines: list[tuple[int, int]], coupon: Coupon | None, settings: Settings, now: datetime) -> Totals:
    sub = subtotal(lines)
    discount = 0
    if coupon is not None:
        check_coupon(coupon, sub, now)
        discount = coupon_discount(coupon, sub)
    ship = shipping(sub - discount, settings)
    return Totals(sub, discount, ship, tax(sub - discount + ship, settings.tax_rate))
