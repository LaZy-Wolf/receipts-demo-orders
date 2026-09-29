from fastapi.testclient import TestClient


def test_missing_key_rejected(client):
    bare = TestClient(client.app)
    assert bare.get("/products").status_code == 401


def test_wrong_key_rejected(client):
    assert client.get("/products", headers={"X-API-Key": "nope"}).status_code == 401


def test_valid_key_accepted(client):
    assert client.get("/products").status_code == 200
