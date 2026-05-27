Feature: Storage stack health

  Scenario: postgres-db is running and reachable from lab-net
    Given the storage profile stack is running
    When the Docker client checks the postgres-db container
    Then container status is healthy
    And a TCP connection to postgres-db on port 5432 succeeds

  Scenario: MinIO health endpoint responds
    Given the storage profile stack is running
    When GET http://minio:9000/minio/health/ready is called
    Then the response status is 200
