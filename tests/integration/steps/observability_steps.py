"""Step definitions for the observability profile stack (prometheus, grafana)."""
import httpx
from pytest_bdd import given, when, then


@given("the observability profile stack is running")
def observability_stack_running() -> None:
    pass  # tests assume the stack is already running; Docker healthchecks confirm readiness


@when(
    "GET http://prometheus:9090/api/v1/targets is called",
    target_fixture="response",
)
def get_prometheus_targets() -> httpx.Response:
    return httpx.get("http://prometheus:9090/api/v1/targets", timeout=5)


@then("the response JSON contains at least one entry in data.activeTargets")
def prometheus_has_active_targets(response: httpx.Response) -> None:
    body = response.text[:500]
    assert response.status_code == 200, (
        f"Expected HTTP 200 from Prometheus targets, got {response.status_code}: {body!r}"
    )
    data = response.json()
    active_targets = data.get("data", {}).get("activeTargets", [])
    assert len(active_targets) >= 1, (
        f"Expected at least one activeTarget in Prometheus response; body={body!r}"
    )


@when(
    "GET http://grafana:3000/api/health is called",
    target_fixture="response",
)
def get_grafana_health() -> httpx.Response:
    return httpx.get("http://grafana:3000/api/health", timeout=5)


@then('the response JSON field database equals "ok"')
def grafana_database_ok(response: httpx.Response) -> None:
    body = response.text[:500]
    assert response.status_code == 200, (
        f"Expected HTTP 200 from Grafana health, got {response.status_code}: {body!r}"
    )
    data = response.json()
    db_status = data.get("database")
    assert db_status == "ok", (
        f"Grafana health: database={db_status!r}, expected 'ok'; body={body!r}"
    )
