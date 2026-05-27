"""IT-005: SSO profile stack health. Covers AC-005, FR-004."""
import pytest
from pytest_bdd import scenarios

pytestmark = pytest.mark.sso


@pytest.fixture
def service_name() -> str:
    return "authelia"

scenarios("features/sso.feature")
