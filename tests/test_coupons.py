def test_create_normalises_code(client):
    resp = client.post("/coupons", json={"code": " save10 ", "kind": "percent", "value": 10})
    assert resp.status_code == 201
    assert resp.json()["code"] == "SAVE10"


def test_validate_ok(client):
    client.post("/coupons", json={"code": "SAVE10", "kind": "percent", "value": 10, "min_order_cents": 5000})
    body = client.get("/coupons/save10/validate", params={"subtotal_cents": 8000}).json()
    assert body == {"valid": True, "discount_cents": 800}


def test_validate_below_minimum(client):
    client.post("/coupons", json={"code": "SAVE10", "kind": "percent", "value": 10, "min_order_cents": 5000})
    body = client.get("/coupons/SAVE10/validate", params={"subtotal_cents": 1000}).json()
    assert body["valid"] is False


def test_validate_unknown(client):
    assert client.get("/coupons/NOPE/validate", params={"subtotal_cents": 1}).status_code == 404
