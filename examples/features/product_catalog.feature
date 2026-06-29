Feature: Product Catalog

  Customers can browse, search, and filter products before adding them
to the cart.

  @regression
  Scenario: List all products
    Given the user is on the product catalog page
    When the user views the product list
    Then the user sees at least 3 products

  @search @regression
  Scenario Outline: Search for products
    Given the user is on the product catalog page
    When the user searches for "<query>"
    Then the user sees <count> products

    Examples:
      | query   | count |
      | laptop  | 2     |
      | phone   | 1     |
      | xyzabc  | 0     |

  @filter @regression
  Scenario: Filter products by category
    Given the user is on the product catalog page
    When the user filters by category "electronics"
    Then only electronics products are shown
