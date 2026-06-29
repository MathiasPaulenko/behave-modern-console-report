Feature: Checkout

  Users can complete purchases from their shopping cart.

  @smoke
  Scenario: Successful checkout
    Given the user has items in the cart
    When the user completes the payment
    Then the order is confirmed

  @regression
  Scenario: Payment failure
    Given the user has items in the cart
    When the user submits an invalid payment
    Then an error is displayed

  @regression
  Scenario: Empty cart cannot checkout
    Given the user has an empty cart
    When the user tries to checkout
    Then an empty cart error is displayed

  @regression
  Scenario: Apply discount code
    Given the user has items in the cart
    When the user applies discount code "SAVE10"
    Then the discount is applied

  @slow @regression
  Scenario: Checkout timeout shows error
    Given the user has items in the cart
    When the user completes the payment with delay
    Then a timeout error is displayed
