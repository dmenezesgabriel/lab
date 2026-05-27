"""Step definitions for the quality profile stack (sonarqube)."""
import docker
from pytest_bdd import given, when


@given("the quality profile stack is running")
def quality_stack_running() -> None:
    pass  # tests assume the stack is already running; Docker healthchecks confirm readiness


@when(
    "the Docker client checks the sonarqube container",
    target_fixture="checked_container",
)
def check_sonarqube_container(docker_client: docker.DockerClient) -> docker.models.containers.Container:
    return docker_client.containers.get("sonarqube")
