"""E2E-003: Grafana UI loads. Covers AC-003."""
import pytest
from pytest_bdd import scenarios

pytestmark = [pytest.mark.e2e, pytest.mark.grafana]

scenarios("features/grafana.feature")
