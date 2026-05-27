Feature: Grafana UI availability

  Scenario: Grafana UI loads
    Given the observability profile stack is running
    When Playwright navigates to http://grafana:3000/login
    Then the page title contains "Grafana"
