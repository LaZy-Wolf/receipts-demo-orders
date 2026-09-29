# orders-service

Order management API used by the storefront and the warehouse tools.

- FastAPI + SQLAlchemy 2 + Pydantic 2
- All money is stored and returned as integer cents
- Every endpoint except `/health` needs an `X-API-Key` header

## Running

```bash
pip install -e ".[test]"
ORDERS_API_KEY=secret uvicorn orders.main:app --reload
pytest
```

## API overview

| Method | Path | Notes |
| --- | --- | --- |
| GET | `/products` | Filters: `q` (name search), `category`. Paginated. |
| POST | `/products` | Create a product. |
| PATCH | `/products/{id}` | Update price, stock or active flag. |
| POST | `/customers` | Emails are unique, compared case-insensitively. |
| GET | `/customers/{id}` | |
| POST | `/coupons` | `kind` is `percent` or `fixed`. |
| GET | `/coupons/{code}/validate?subtotal_cents=` | Check a coupon before checkout. |
| POST | `/orders` | Reserves stock, applies coupon, shipping and tax. |
| GET | `/orders` | Filter by `customer_id`. Paginated. |
| GET | `/orders/{id}` | |
| POST | `/orders/{id}/status` | Move an order through its lifecycle. |
| POST | `/orders/{id}/cancel` | Cancel an order and return its stock. |

### Pagination

List endpoints take `page` (from 1) and `size` (default 20, **maximum 100**) and return
`{"items": [...], "total": n, "page": p, "size": s, "pages": number_of_pages}`.

### Pricing rules

1. Subtotal is the sum of `unit_price_cents * quantity`.
2. A coupon applies when the subtotal is **at least** its `min_order_cents`.
   Percent coupons round the discount down to the cent. Fixed coupons never exceed the subtotal.
3. Shipping is free when the discounted subtotal reaches `free_shipping_threshold_cents`, otherwise flat.
4. Tax is charged on the discounted subtotal plus shipping, rounded half up.

### Order lifecycle

`pending -> paid -> shipped -> delivered`. `pending` and `paid` orders can be cancelled.
Shipped and delivered orders cannot.
