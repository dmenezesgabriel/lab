"""Step definitions for the storage profile stack (postgres-db, minio)."""
import socket

import docker
import httpx
from pytest_bdd import given, when, then


@given("the storage profile stack is running")
def storage_stack_running() -> None:
    pass  # tests assume the stack is already running; Docker healthchecks confirm readiness


@when(
    "the Docker client checks the postgres-db container",
    target_fixture="checked_container",
)
def check_postgres_container(docker_client: docker.DockerClient) -> docker.models.containers.Container:
    return docker_client.containers.get("postgres-db")


@then("a TCP connection to postgres-db on port 5432 succeeds")
def postgres_tcp_reachable() -> None:
    try:
        sock = socket.create_connection(("postgres-db", 5432), timeout=5)
        sock.close()
    except OSError as exc:
        raise AssertionError(
            f"TCP connection to postgres-db:5432 failed: {exc!r}"
        ) from exc


@when(
    "GET http://minio:9000/minio/health/ready is called",
    target_fixture="response",
)
def get_minio_health() -> httpx.Response:
    return httpx.get("http://minio:9000/minio/health/ready", timeout=5)
