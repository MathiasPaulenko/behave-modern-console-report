"""Step definitions for the checkout example."""

import time

from behave import given, then, when


@given("the user has items in the cart")
def step_user_has_items(context: object) -> None:
    context.cart = ["item1"]


@when("the user completes the payment")
def step_user_completes_payment(context: object) -> None:
    time.sleep(0.3)
    context.payment = "valid"


@when("the user submits an invalid payment")
def step_user_submits_invalid_payment(context: object) -> None:
    time.sleep(0.3)
    context.payment = "invalid"


@then("the order is confirmed")
def step_order_confirmed(context: object) -> None:
    assert context.payment == "valid"


@then("an error is displayed")
def step_payment_error(context: object) -> None:
    assert context.payment == "invalid"


@given("the user has an empty cart")
def step_user_has_empty_cart(context: object) -> None:
    context.cart = []


@when("the user tries to checkout")
def step_user_tries_checkout(context: object) -> None:
    context.checkout_attempted = True


@then("an empty cart error is displayed")
def step_empty_cart_error(context: object) -> None:
    assert context.checkout_attempted
    assert not context.cart


@when('the user applies discount code "{code}"')
def step_apply_discount(context: object, code: str) -> None:
    context.discount_code = code


@then("the discount is applied")
def step_discount_applied(context: object) -> None:
    assert context.discount_code == "SAVE10"


@when("the user completes the payment with delay")
def step_user_completes_payment_with_delay(context: object) -> None:
    context.payment = "timeout"


@then("a timeout error is displayed")
def step_timeout_error(context: object) -> None:
    assert context.payment == "timeout"
