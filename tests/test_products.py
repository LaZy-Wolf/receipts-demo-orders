def test_create_and_get(client, make_product):
    product = make_product(name="Coffee Mug", price_cents=1299)
    resp = client.get(f"/products/{product['id']}")
    assert resp.status_code == 200
    assert resp.json()["name"] == "Coffee Mug"


def test_duplicate_sku_conflicts(client, make_product):
    make_product(sku="MUG-1")
    resp = client.post("/products", json={"sku": "MUG-1", "name": "x", "category": "c", "price_cents": 1})
    assert resp.status_code == 409


def test_negative_price_rejected(client):
    resp = client.post("/products", json={"sku": "X", "name": "x", "category": "c", "price_cents": -1})
    assert resp.status_code == 422


def test_list_sorted_by_name(client, make_product):
    for name in ("Zebra Mug", "Apple Cup", "Mango Plate"):
        make_product(name=name)
    names = [p["name"] for p in client.get("/products").json()["items"]]
    assert names == ["Apple Cup", "Mango Plate", "Zebra Mug"]


def test_filter_by_category(client, make_product):
    make_product(name="Mug", category="kitchen")
    make_product(name="Pen", category="office")
    items = client.get("/products", params={"category": "office"}).json()["items"]
    assert [p["name"] for p in items] == ["Pen"]


def test_search_by_name(client, make_product):
    make_product(name="Coffee Mug")
    make_product(name="Tea Pot")
    items = client.get("/products", params={"q": "mug"}).json()["items"]
    assert [p["name"] for p in items] == ["Coffee Mug"]


def test_inactive_hidden_from_list(client, make_product):
    product = make_product(name="Old Mug")
    client.patch(f"/products/{product['id']}", json={"active": False})
    assert client.get("/products").json()["total"] == 0


def test_patch_updates_stock(client, make_product):
    product = make_product(stock=3)
    resp = client.patch(f"/products/{product['id']}", json={"stock": 7})
    assert resp.json()["stock"] == 7
