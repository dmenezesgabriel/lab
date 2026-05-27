Feature: MLflow UI availability

  Scenario: MLflow UI renders experiment state
    Given the model-registry profile stack is running
    When Playwright navigates to http://mlflow:5000
    Then the page renders without a 5xx error
    And the page contains "Experiments" or an empty-state indicator
