def place(client, customer, *lines, coupon=None):
    body = {"customer_id": customer["id"], "items": [{"product_id": p["id"], "quantity": q} for p, q in lines]}
    if coupon:
        body["coupon_code"] = coupon
    return client.post("/orders", json=body)


def test_create_order_totals(client, make_product, make_customer):
    mug = make_product(price_cents=1000, stock=5)
    resp = place(client, make_customer(), (mug, 2))
    assert resp.status_code == 201
    order = resp.json()
    assert order["subtotal_cents"] == 2000
    assert order["shipping_cents"] == 750
    assert order["tax_cents"] == 220
    assert order["total_cents"] == 2970
    assert order["status"] == "pending"


def test_create_order_reserves_stock(client, make_product, make_customer):
    mug = make_product(stock=5)
    place(client, make_customer(), (mug, 2))
    assert client.get(f"/products/{mug['id']}").json()["stock"] == 3


def test_same_product_twice_is_merged(client, make_product, make_customer):
    mug = make_product(stock=5)
    order = place(client, make_customer(), (mug, 1), (mug, 2)).json()
    assert order["items"] == [{"product_id": mug["id"], "quantity": 3, "unit_price_cents": 1000}]


def test_out_of_stock(client, make_product, make_customer):
    mug = make_product(stock=1)
    assert place(client, make_customer(), (mug, 2)).status_code == 409


def test_failed_order_does_not_reserve(client, make_product, make_customer):
    mug = make_product(stock=5)
    pen = make_product(stock=0)
    assert place(client, make_customer(), (mug, 2), (pen, 1)).status_code == 409
    assert client.get(f"/products/{mug['id']}").json()["stock"] == 5


def test_order_with_coupon(client, make_product, make_customer):
    client.post("/coupons", json={"code": "SAVE10", "kind": "percent", "value": 10, "min_order_cents": 5000})
    lamp = make_product(price_cents=8000)
    order = place(client, make_customer(), (lamp, 1), coupon="save10").json()
    assert order["discount_cents"] == 800
    assert order["coupon_code"] == "SAVE10"


def test_unknown_coupon(client, make_product, make_customer):
    lamp = make_product()
    assert place(client, make_customer(), (lamp, 1), coupon="NOPE").status_code == 422


def test_unknown_customer(client, make_product):
    lamp = make_product()
    assert place(client, {"id": 999}, (lamp, 1)).status_code == 404


def test_status_flow(client, make_product, make_customer):
    order = place(client, make_customer(), (make_product(), 1)).json()
    for new in ("paid", "shipped", "delivered"):
        resp = client.post(f"/orders/{order['id']}/status", json={"status": new})
        assert resp.status_code == 200
        assert resp.json()["status"] == new


def test_cannot_skip_to_delivered(client, make_product, make_customer):
    order = place(client, make_customer(), (make_product(), 1)).json()
    assert client.post(f"/orders/{order['id']}/status", json={"status": "delivered"}).status_code == 409


def test_cancel_pending(client, make_product, make_customer):
    order = place(client, make_customer(), (make_product(), 1)).json()
    resp = client.post(f"/orders/{order['id']}/cancel")
    assert resp.status_code == 200
    assert resp.json()["status"] == "cancelled"


def test_cancel_twice_conflicts(client, make_product, make_customer):
    order = place(client, make_customer(), (make_product(), 1)).json()
    client.post(f"/orders/{order['id']}/cancel")
    assert client.post(f"/orders/{order['id']}/cancel").status_code == 409


def test_list_orders_by_customer(client, make_product, make_customer):
    alice, bob = make_customer(), make_customer()
    product = make_product()
    place(client, alice, (product, 1))
    place(client, bob, (product, 1))
    body = client.get("/orders", params={"customer_id": alice["id"]}).json()
    assert body["total"] == 1
