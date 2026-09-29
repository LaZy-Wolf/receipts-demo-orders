from fastapi.testclient import TestClient


def test_health_needs_no_key(client):
    resp = TestClient(client.app).get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"
