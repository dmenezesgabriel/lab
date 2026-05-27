Feature: Orchestration stack health

  Scenario: Airflow API server reports healthy
    Given the orchestration profile stack is running
    When GET http://airflow-webserver:8080/api/v2/monitor/health is called
    Then the response JSON indicates healthy scheduler and metadatabase
