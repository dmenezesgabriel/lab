"""IT-006: orchestration profile stack health. Covers AC-006, FR-004."""
import pytest
from pytest_bdd import scenarios

from steps.orchestration_steps import (  # noqa: F401 — registers steps with pytest-bdd
    orchestration_stack_running,
    get_airflow_health,
    airflow_components_healthy,
)

pytestmark = pytest.mark.orchestration

scenarios("features/orchestration.feature")
