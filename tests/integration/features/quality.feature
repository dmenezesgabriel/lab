Feature: Quality stack health

  Scenario: SonarQube container is healthy
    Given the quality profile stack is running
    When the Docker client checks the sonarqube container
    Then container status is healthy
