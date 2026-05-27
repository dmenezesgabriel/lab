"""E2E-004: MLflow UI renders experiment state. Covers AC-004."""
import pytest
from pytest_bdd import scenarios

pytestmark = [pytest.mark.e2e, pytest.mark.mlflow]

scenarios("features/mlflow.feature")
