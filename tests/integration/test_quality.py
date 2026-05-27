"""IT-007: quality profile stack health. Covers AC-007, FR-003."""
import pytest
from pytest_bdd import scenarios

from steps.quality_steps import (  # noqa: F401 — registers steps with pytest-bdd
    quality_stack_running,
    check_sonarqube_container,
)

pytestmark = pytest.mark.quality

scenarios("features/quality.feature")
