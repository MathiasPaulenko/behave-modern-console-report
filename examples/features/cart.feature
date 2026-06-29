Feature: Shopping Cart

  Users can manage their cart before proceeding to checkout.

  @smoke
  Scenario: Add a product to the cart
    Given the user is on the product catalog page
    When the user adds "Laptop" to the cart
    Then the cart contains 1 item

  @smoke
  Scenario: Add multiple products to the cart
    Given the user is on the product catalog page
    When the user adds "Laptop" to the cart
    And the user adds "Phone" to the cart
    Then the cart contains 2 items

  @regression
  Scenario: Remove a product from the cart
    Given the user is on the product catalog page
    And the user adds "Laptop" to the cart
    When the user removes "Laptop" from the cart
    Then the cart contains 0 items

  @slow @regression
  Scenario: Cart persists after login
    Given the user is on the login page
    When the user enters valid credentials
    And the user adds "Laptop" to the cart
    Then the cart contains 1 item
