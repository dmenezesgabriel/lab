Feature: lab-net hostname resolution

  Scenario: test-runner resolves postgres-db by hostname
    Given the test-runner container is running on lab-net
    When it resolves postgres-db by hostname
    Then the hostname resolves to a valid IP on lab-net
