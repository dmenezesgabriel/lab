"""Step definitions for the orchestration profile stack (airflow)."""
import httpx
from pytest_bdd import given, when, then


@given("the orchestration profile stack is running")
def orchestration_stack_running() -> None:
    pass  # tests assume the stack is already running; Docker healthchecks confirm readiness


@when(
    "GET http://airflow-webserver:8080/api/v2/monitor/health is called",
    target_fixture="response",
)
def get_airflow_health() -> httpx.Response:
    return httpx.get("http://airflow-webserver:8080/api/v2/monitor/health", timeout=5)


@then("the response JSON indicates healthy scheduler and metadatabase")
def airflow_components_healthy(response: httpx.Response) -> None:
    body = response.text[:500]
    assert response.status_code == 200, (
        f"Expected HTTP 200 from Airflow health, got {response.status_code}: {body!r}"
    )
    data = response.json()
    scheduler_status = data.get("scheduler", {}).get("status")
    metadatabase_status = data.get("metadatabase", {}).get("status")
    assert scheduler_status == "healthy", (
        f"Airflow scheduler: status={scheduler_status!r}, expected 'healthy'; body={body!r}"
    )
    assert metadatabase_status == "healthy", (
        f"Airflow metadatabase: status={metadatabase_status!r}, expected 'healthy'; body={body!r}"
    )
