"""IT-001, IT-002: storage profile stack health. Covers AC-001, AC-002, FR-003, FR-004."""
import pytest
from pytest_bdd import scenarios

pytestmark = pytest.mark.storage


@pytest.fixture
def service_name() -> str:
    return "minio"

scenarios("features/storage.feature")
