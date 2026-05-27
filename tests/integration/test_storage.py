"""IT-001, IT-002: storage profile stack health. Covers AC-001, AC-002, FR-003, FR-004."""
import pytest
from pytest_bdd import scenarios

from steps.storage_steps import (  # noqa: F401 — registers steps with pytest-bdd
    storage_stack_running,
    check_postgres_container,
    postgres_tcp_reachable,
    get_minio_health,
)

pytestmark = pytest.mark.storage


@pytest.fixture
def service_name() -> str:
    return "minio"

scenarios("features/storage.feature")
