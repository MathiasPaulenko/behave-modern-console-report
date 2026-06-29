Feature: User Login

  This feature demonstrates the modern console report with a mix of
  passing, failing, and skipped scenarios.

  @critical
  Scenario: Successful login
    Given the user is on the login page
    When the user enters valid credentials
    Then the user is redirected to the dashboard

  @regression
  Scenario: Failed login
    Given the user is on the login page
    When the user enters invalid credentials
    Then an error message is displayed

  @skip
  Scenario: Login with social provider
    Given the user is on the login page
    When the user chooses to login with OAuth
    Then the user is redirected to the dashboard

  @regression
  Scenario: Locked account shows error
    Given the user is on the login page
    When the user enters locked account credentials
    Then the user is redirected to the dashboard

  @regression
  Scenario: Password reset request
    Given the user is on the login page
    When the user requests a password reset for "user@example.com"
    Then a reset email is sent

  @regression
  Scenario: Remember me option
    Given the user is on the login page
    When the user enters valid credentials with remember me enabled
    Then the user is redirected to the dashboard
