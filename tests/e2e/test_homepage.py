"""E2E-001: Homepage loads without authentication. Covers AC-001, FR-005."""
import pytest
from pytest_bdd import scenarios

pytestmark = [pytest.mark.e2e, pytest.mark.homepage]

scenarios("features/homepage.feature")
