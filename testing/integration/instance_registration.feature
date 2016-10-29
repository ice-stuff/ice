Feature: instance registration
  Scenario: instances call back the registry
    Given we start iCE registry server
    And we create session 'test'
    When we spawn 2 containers in session 'test'
    Then the 2 instances become available in less than 60 seconds in session 'test'
