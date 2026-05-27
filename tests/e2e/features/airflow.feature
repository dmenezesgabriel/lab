Feature: Airflow UI availability

  Scenario: Airflow UI renders or redirects cleanly
    Given the airflow profile stack is running
    When Playwright navigates to http://airflow-webserver:8080
    Then the HTTP response status is not 5xx
    And the rendered page is not blank
