"""Step definitions for the product catalog example."""

import time

from behave import given, then, when


@given("the user is on the product catalog page")
def step_user_on_catalog_page(context: object) -> None:
    context.page = "catalog"
    context.products = [
        {"name": "Laptop Pro", "category": "electronics"},
        {"name": "Laptop Air", "category": "electronics"},
        {"name": "Phone", "category": "electronics"},
        {"name": "T-Shirt", "category": "clothing"},
    ]


@when("the user views the product list")
def step_user_views_product_list(context: object) -> None:
    context.viewed_products = list(context.products)


@then("the user sees at least {count:d} products")
def step_user_sees_at_least_products(context: object, count: int) -> None:
    assert len(context.viewed_products) >= count


@when('the user searches for "{query}"')
def step_user_searches(context: object, query: str) -> None:
    time.sleep(0.6)
    context.search_query = query
    context.search_results = [
        p for p in context.products if query.lower() in p["name"].lower()
    ]


@then("the user sees {count:d} products")
def step_user_sees_count_products(context: object, count: int) -> None:
    assert len(context.search_results) == count


@when('the user filters by category "{category}"')
def step_user_filters_by_category(context: object, category: str) -> None:
    time.sleep(0.6)
    context.filter_category = category
    context.filtered_products = [p for p in context.products if p["category"] == category]


@then("only electronics products are shown")
def step_only_electronics_shown(context: object) -> None:
    assert context.filter_category == "electronics"
    assert all(p["category"] == "electronics" for p in context.filtered_products)
