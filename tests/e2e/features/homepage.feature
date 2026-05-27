Feature: Homepage availability

  Scenario: Homepage loads without authentication
    Given the management profile stack is running
    When Playwright navigates to http://homepage:3000
    Then the page title contains "Homepage"
    And no unhandled console errors are logged
