from .errors import OutOfStock
from .models import Product


def reserve(product: Product, quantity: int) -> None:
    if not product.active:
        raise OutOfStock(f"product {product.id} is not available")
    if product.stock < quantity:
        raise OutOfStock(f"only {product.stock} of product {product.id} left")
    product.stock -= quantity


def release(product: Product, quantity: int) -> None:
    product.stock += quantity
