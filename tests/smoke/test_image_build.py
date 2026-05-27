"""SMK-001: test-runner image builds cleanly. Covers FR-005, AC-005."""
import docker
import pytest


@pytest.mark.smoke
def test_test_runner_image_builds():
    """Build the test-runner image from /workspace and verify playwright imports."""
    client = docker.from_env()
    image, _ = client.images.build(
        path="/workspace/tests",
        dockerfile="Dockerfile",
        rm=True,
    )
    # ContainerError raised automatically if exit code != 0
    client.containers.run(
        image.id,
        command='python -c "import playwright"',
        remove=True,
    )
