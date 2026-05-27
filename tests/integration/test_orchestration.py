"""IT-006: orchestration profile stack health. Covers AC-006, FR-004."""
import pytest
from pytest_bdd import scenarios

pytestmark = pytest.mark.orchestration

scenarios("features/orchestration.feature")
