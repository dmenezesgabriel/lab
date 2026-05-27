"""E2E-002: Authelia login portal is reachable. Covers AC-002."""
import pytest
from pytest_bdd import scenarios

pytestmark = [pytest.mark.e2e, pytest.mark.sso]

scenarios("features/authelia.feature")
