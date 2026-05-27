Feature: SSO stack health

  Scenario: Authelia health endpoint responds
    Given the sso profile stack is running
    When GET http://authelia:9091/api/health is called
    Then the response status is 200
