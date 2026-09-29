def test_create_customer(client):
    resp = client.post("/customers", json={"email": "alice@example.com", "name": "Alice"})
    assert resp.status_code == 201
    assert resp.json()["email"] == "alice@example.com"


def test_duplicate_email_conflicts(client, make_customer):
    make_customer(email="alice@example.com")
    resp = client.post("/customers", json={"email": "alice@example.com", "name": "Alice 2"})
    assert resp.status_code == 409


def test_invalid_email_rejected(client):
    assert client.post("/customers", json={"email": "not-an-email", "name": "X"}).status_code == 422


def test_get_missing_customer(client):
    assert client.get("/customers/999").status_code == 404
