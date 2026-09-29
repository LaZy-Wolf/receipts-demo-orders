import pytest
from fastapi.testclient import TestClient

from orders.config import Settings
from orders.main import create_app

API_KEY = "test-key"


@pytest.fixture
def settings():
    return Settings(database_url="sqlite://", api_key=API_KEY)


@pytest.fixture
def client(settings):
    with TestClient(create_app(settings), headers={"X-API-Key": API_KEY}) as c:
        yield c


@pytest.fixture
def make_product(client):
    counter = iter(range(1, 10_000))

    def make(**overrides):
        n = next(counter)
        body = {"sku": f"SKU-{n}", "name": f"Product {n}", "category": "misc", "price_cents": 1000, "stock": 10}
        body.update(overrides)
        resp = client.post("/products", json=body)
        assert resp.status_code == 201, resp.text
        return resp.json()

    return make


@pytest.fixture
def make_customer(client):
    counter = iter(range(1, 10_000))

    def make(**overrides):
        n = next(counter)
        body = {"email": f"customer{n}@example.com", "name": f"Customer {n}"}
        body.update(overrides)
        resp = client.post("/customers", json=body)
        assert resp.status_code == 201, resp.text
        return resp.json()

    return make
