Feature: experiment running
  Scenario: instances can be used by an experiment
    Given we start iCE registry server
    And we create session 'test'
    When we spawn 2 containers with sshd in session 'test'
    Then the 2 instances become available in less than 60 seconds in session 'test'
    And we can run './testing/assets/exp_simple.py' experiment with task 'get_hostname' under session 'test'
