"""IT-003, IT-004: observability profile stack health. Covers AC-003, AC-004, FR-004."""
import pytest
from pytest_bdd import scenarios

from steps.observability_steps import (  # noqa: F401 — registers steps with pytest-bdd
    observability_stack_running,
    get_prometheus_targets,
    prometheus_has_active_targets,
    get_grafana_health,
    grafana_database_ok,
)

pytestmark = pytest.mark.observability

scenarios("features/observability.feature")
