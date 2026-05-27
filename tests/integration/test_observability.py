"""IT-003, IT-004: observability profile stack health. Covers AC-003, AC-004, FR-004."""
import pytest
from pytest_bdd import scenarios

pytestmark = pytest.mark.observability

scenarios("features/observability.feature")
