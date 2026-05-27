Feature: Authelia login portal

  Scenario: Authelia login portal is reachable
    Given the sso profile stack is running
    When Playwright navigates to http://authelia:9091
    Then the page contains a username input field
