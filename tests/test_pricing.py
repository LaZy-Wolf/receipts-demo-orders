from datetime import datetime
from decimal import Decimal

import pytest

from orders.config import Settings
from orders.errors import CouponError
from orders.models import Coupon
from orders.pricing import coupon_discount, price_order, shipping, tax

NOW = datetime(2026, 6, 1, 12, 0)
SETTINGS = Settings()


def test_tax_rounds_half_up():
    assert tax(1250, Decimal("0.08")) == 100
    assert tax(1256, Decimal("0.08")) == 100
    assert tax(1257, Decimal("0.08")) == 101


def test_free_shipping_threshold():
    assert shipping(10_000, SETTINGS) == 0
    assert shipping(9_999, SETTINGS) == 750


def test_percent_coupon_rounds_down():
    coupon = Coupon(code="P", kind="percent", value=15, min_order_cents=0, active=True)
    assert coupon_discount(coupon, 999) == 149


def test_fixed_coupon_capped_at_subtotal():
    coupon = Coupon(code="F", kind="fixed", value=5000, min_order_cents=0, active=True)
    assert coupon_discount(coupon, 1200) == 1200


def test_price_order_without_coupon():
    totals = price_order([(1000, 2), (550, 1)], None, SETTINGS, NOW)
    assert (totals.subtotal_cents, totals.shipping_cents, totals.tax_cents) == (2550, 750, 264)
    assert totals.total_cents == 3564


def test_price_order_with_coupon_above_minimum():
    coupon = Coupon(code="SAVE10", kind="percent", value=10, min_order_cents=5000, active=True)
    totals = price_order([(6000, 1)], coupon, SETTINGS, NOW)
    assert totals.discount_cents == 600


def test_expired_coupon_rejected():
    coupon = Coupon(code="OLD", kind="fixed", value=100, min_order_cents=0, active=True, expires_at=datetime(2026, 1, 1))
    with pytest.raises(CouponError, match="expired"):
        price_order([(1000, 1)], coupon, SETTINGS, NOW)


def test_coupon_below_minimum_rejected():
    coupon = Coupon(code="SAVE10", kind="percent", value=10, min_order_cents=5000, active=True)
    with pytest.raises(CouponError, match="minimum"):
        price_order([(4000, 1)], coupon, SETTINGS, NOW)
