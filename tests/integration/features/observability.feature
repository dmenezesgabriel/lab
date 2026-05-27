Feature: Observability stack health

  Scenario: Prometheus has active scrape targets
    Given the observability profile stack is running
    When GET http://prometheus:9090/api/v1/targets is called
    Then the response JSON contains at least one entry in data.activeTargets

  Scenario: Grafana database connection is healthy
    Given the observability profile stack is running
    When GET http://grafana:3000/api/health is called
    Then the response JSON field database equals "ok"
