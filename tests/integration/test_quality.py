"""IT-007: quality profile stack health. Covers AC-007, FR-003."""
import pytest
from pytest_bdd import scenarios

pytestmark = pytest.mark.quality

scenarios("features/quality.feature")
