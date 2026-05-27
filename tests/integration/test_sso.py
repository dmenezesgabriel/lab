"""IT-005: SSO profile stack health. Covers AC-005, FR-004."""
import pytest
from pytest_bdd import scenarios

from steps.sso_steps import (  # noqa: F401 — registers steps with pytest-bdd
    sso_stack_running,
    get_authelia_health,
)

pytestmark = pytest.mark.sso


@pytest.fixture
def service_name() -> str:
    return "authelia"

scenarios("features/sso.feature")
