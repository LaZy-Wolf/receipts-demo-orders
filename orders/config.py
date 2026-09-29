import os
from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Settings:
    database_url: str = "sqlite:///orders.sqlite3"
    api_key: str = "dev-key"
    tax_rate: Decimal = Decimal("0.08")
    free_shipping_threshold_cents: int = 10_000
    flat_shipping_cents: int = 750
    max_page_size: int = 100

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            database_url=os.environ.get("ORDERS_DATABASE_URL", cls.database_url),
            api_key=os.environ.get("ORDERS_API_KEY", cls.api_key),
            tax_rate=Decimal(os.environ.get("ORDERS_TAX_RATE", str(cls.tax_rate))),
        )
