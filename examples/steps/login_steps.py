"""Step definitions for the login example."""

import time

from behave import given, then, when


@given("the user is on the login page")
def step_user_on_login_page(context: object) -> None:
    context.page = "login"


@when("the user enters valid credentials")
def step_user_enters_valid_credentials(context: object) -> None:
    time.sleep(0.3)
    context.credentials = "valid"


@when("the user enters invalid credentials")
def step_user_enters_invalid_credentials(context: object) -> None:
    time.sleep(0.3)
    context.credentials = "invalid"


@when("the user enters locked account credentials")
def step_user_enters_locked_credentials(context: object) -> None:
    time.sleep(0.3)
    context.credentials = "locked"


@when("the user chooses to login with OAuth")
def step_user_chooses_oauth(context: object) -> None:
    context.credentials = "oauth"


@then("the user is redirected to the dashboard")
def step_user_redirected_to_dashboard(context: object) -> None:
    assert context.credentials == "valid", "Only valid credentials should redirect"


@then("an error message is displayed")
def step_error_message(context: object) -> None:
    assert context.credentials == "invalid", "Invalid credentials should show an error"


@when('the user requests a password reset for "{email}"')
def step_password_reset(context: object, email: str) -> None:
    context.reset_email = email


@then("a reset email is sent")
def step_reset_email_sent(context: object) -> None:
    assert context.reset_email == "user@example.com"


@when("the user enters valid credentials with remember me enabled")
def step_user_enters_valid_credentials_remember_me(context: object) -> None:
    context.credentials = "valid"
    context.remember_me = True
