"""Example Behave environment setup."""


def before_all(context: object) -> None:
    """Initialize shared context before the test run."""
    context.base_url = "https://example.com"


def before_scenario(context: object, scenario: object) -> None:
    """Reset scenario-specific state and honor skip tags."""
    if "skip" in scenario.tags:
        scenario.skip()
    context.page = None
    context.credentials = None
    context.payment = None
    context.cart = []
    context.products = []
