def test_first_page(client, make_product):
    for _ in range(3):
        make_product()
    body = client.get("/products", params={"size": 2}).json()
    assert body["total"] == 3
    assert len(body["items"]) == 2
    assert body["page"] == 1


def test_exact_multiple(client, make_product):
    for _ in range(4):
        make_product()
    body = client.get("/products", params={"size": 2}).json()
    assert body["pages"] == 2


def test_empty(client):
    body = client.get("/products").json()
    assert body == {"items": [], "total": 0, "page": 1, "size": 20, "pages": 0}


def test_page_zero_rejected(client):
    assert client.get("/products", params={"page": 0}).status_code == 422
