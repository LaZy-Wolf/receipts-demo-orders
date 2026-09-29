from .errors import InvalidTransition

TRANSITIONS: dict[str, set[str]] = {
    "pending": {"paid", "cancelled"},
    "paid": {"shipped", "cancelled"},
    "shipped": {"delivered"},
    "delivered": set(),
    "cancelled": set(),
}


def can_transition(current: str, new: str) -> bool:
    return new in TRANSITIONS.get(current, set())


def ensure_transition(current: str, new: str) -> None:
    if not can_transition(current, new):
        raise InvalidTransition(f"cannot move order from {current} to {new}")
