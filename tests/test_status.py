from orders.status import can_transition


def test_forward_moves():
    assert can_transition("pending", "paid")
    assert can_transition("paid", "shipped")
    assert can_transition("shipped", "delivered")


def test_no_backwards_moves():
    assert not can_transition("shipped", "paid")
    assert not can_transition("delivered", "shipped")


def test_cancellation_rules():
    assert can_transition("pending", "cancelled")
    assert can_transition("paid", "cancelled")
    assert not can_transition("shipped", "cancelled")
    assert not can_transition("delivered", "cancelled")
