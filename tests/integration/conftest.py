"""Session-scoped Docker client fixture and shared BDD step definitions.

Usage example:
    docker_client = docker.from_env()
    assert_container_healthy(docker_client, "postgres-db")
"""
import sys
from pathlib import Path

# Allow test files to import from steps/ as a plain package.
sys.path.insert(0, str(Path(__file__).parent))

import docker
import httpx
import pytest
from pytest_bdd import then


@pytest.fixture(scope="session")
def docker_client() -> docker.DockerClient:
    return docker.from_env()


def assert_container_healthy(client: docker.DockerClient, name: str) -> docker.models.containers.Container:
    """Retrieve container by name and assert it is running and healthy.

    Raises AssertionError with container name, expected status, and actual
    status so failed steps are self-diagnosing (OBS-001).
    """
    try:
        container = client.containers.get(name)
    except docker.errors.NotFound:
        raise AssertionError(
            f"Container {name!r} not found; expected it to be running on lab-net"
        )
    container.reload()
    status = container.status
    health = container.attrs.get("State", {}).get("Health", {}).get("Status", "none")
    if status != "running":
        raise AssertionError(
            f"Container {name!r}: status={status!r}, expected 'running'"
        )
    if health not in ("healthy", "none"):
        raise AssertionError(
            f"Container {name!r}: status={status!r}, health={health!r}, expected health='healthy'"
        )
    return container


# ─── Shared steps ────────────────────────────────────────────────────────────


@then("container status is healthy")
def then_container_healthy(checked_container: docker.models.containers.Container) -> None:
    """Assert the container retrieved by the preceding When step is healthy."""
    checked_container.reload()
    name = checked_container.name
    status = checked_container.status
    health = checked_container.attrs.get("State", {}).get("Health", {}).get("Status", "none")
    assert status == "running", (
        f"Container {name!r}: status={status!r}, expected 'running'"
    )
    assert health == "healthy", (
        f"Container {name!r}: status={status!r}, health={health!r}, expected health='healthy'"
    )


@pytest.fixture
def service_name() -> str:
    return "<unknown>"


@then("the response status is 200")
def then_response_200(response: httpx.Response, service_name: str) -> None:
    assert response.status_code == 200, (
        f"service={service_name!r}: expected HTTP 200, got {response.status_code}: {response.text[:500]!r}"
    )
