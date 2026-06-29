"""Step definitions for the shopping cart example."""

import time

from behave import given, then, when


@given('the user adds "{product}" to the cart')
@when('the user adds "{product}" to the cart')
def step_user_adds_product_to_cart(context: object, product: str) -> None:
    time.sleep(0.3)
    if not hasattr(context, "cart"):
        context.cart = []
    context.cart.append(product)


@given('the user removes "{product}" from the cart')
@when('the user removes "{product}" from the cart')
def step_user_removes_product_from_cart(context: object, product: str) -> None:
    if product in context.cart:
        context.cart.remove(product)


@then("the cart contains {count:d} items")
@then("the cart contains {count:d} item")
def step_cart_contains_items(context: object, count: int) -> None:
    cart = getattr(context, "cart", [])
    assert len(cart) == count
