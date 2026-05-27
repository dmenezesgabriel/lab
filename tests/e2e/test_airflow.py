"""E2E-005: Airflow UI renders or redirects cleanly. Covers AC-005."""
import pytest
from pytest_bdd import scenarios

pytestmark = [pytest.mark.e2e, pytest.mark.airflow]

scenarios("features/airflow.feature")
