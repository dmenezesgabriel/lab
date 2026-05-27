"""ST-001: no secret env vars in container beyond DOCKER_HOST. Covers NFR-002."""
import re
import socket

import docker
import pytest

_SECRET_PATTERN = re.compile(
    r"(SECRET|PASSWORD|TOKEN|API_KEY|PRIVATE_KEY|CREDENTIAL)", re.IGNORECASE
)


@pytest.mark.security
def test_no_secret_env_vars():
    """docker inspect shows no secret-named env vars in the running container."""
    client = docker.from_env()
    container = client.containers.get(socket.gethostname())
    env_list = container.attrs["Config"]["Env"] or []
    env_keys = [e.split("=", 1)[0] for e in env_list]
    secret_vars = [k for k in env_keys if _SECRET_PATTERN.search(k)]
    assert not secret_vars, f"Secret env vars found in container: {secret_vars}"
