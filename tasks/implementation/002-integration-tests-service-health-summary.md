---
id: "002"
issue: "tasks/issues/002-integration-tests-service-health.md"
created: 2026-05-27
updated: 2026-05-27
---

# Implementation Summary: Integration Tests for Service Health

## Related Task

- `tasks/issues/002-integration-tests-service-health.md`

## Files Changed

- `tests/integration/conftest.py` — session-scoped `docker_client` fixture, `assert_container_healthy` helper, shared BDD steps (`container status is healthy`, `response status is 200`)
- `tests/integration/steps/__init__.py` — makes `steps/` a Python package importable from test files
- `tests/integration/steps/storage_steps.py` — Given/When/Then steps for postgres-db and minio
- `tests/integration/steps/observability_steps.py` — Given/When/Then steps for prometheus and grafana
- `tests/integration/steps/orchestration_steps.py` — Given/When/Then steps for airflow-webserver
- `tests/integration/steps/sso_steps.py` — Given/When steps for authelia
- `tests/integration/steps/quality_steps.py` — Given/When steps for sonarqube
- `tests/integration/features/storage.feature` — Gherkin scenarios IT-001 (postgres-db) and IT-002 (minio)
- `tests/integration/features/observability.feature` — Gherkin scenarios IT-003 (prometheus) and IT-004 (grafana)
- `tests/integration/features/orchestration.feature` — Gherkin scenario IT-006 (airflow)
- `tests/integration/features/sso.feature` — Gherkin scenario IT-005 (authelia)
- `tests/integration/features/quality.feature` — Gherkin scenario IT-007 (sonarqube)
- `tests/integration/test_storage.py` — binds storage.feature scenarios; `pytestmark = pytest.mark.storage`
- `tests/integration/test_observability.py` — binds observability.feature; `pytestmark = pytest.mark.observability`
- `tests/integration/test_orchestration.py` — binds orchestration.feature; `pytestmark = pytest.mark.orchestration`
- `tests/integration/test_sso.py` — binds sso.feature; `pytestmark = pytest.mark.sso`
- `tests/integration/test_quality.py` — binds quality.feature; `pytestmark = pytest.mark.quality`
- `tests/pyproject.toml` — added `[tool.pytest.ini_options]` with all five stack markers plus existing `security` and `smoke` markers

## Behavior Implemented

- IT-001: Checks `postgres-db` Docker status is `running`/`healthy` and TCP connection to port 5432 succeeds.
- IT-002: `GET http://minio:9000/minio/health/ready` asserts HTTP 200.
- IT-003: `GET http://prometheus:9090/api/v1/targets` asserts at least one entry in `data.activeTargets`.
- IT-004: `GET http://grafana:3000/api/health` asserts `database == "ok"`.
- IT-005: `GET http://authelia:9091/api/health` asserts HTTP 200.
- IT-006: `GET http://airflow-webserver:8080/api/v2/monitor/health` asserts `scheduler.status == "healthy"` and `metadatabase.status == "healthy"`.
- IT-007: Checks `sonarqube` Docker status is `running`/`healthy`.
- All HTTP calls use `httpx` with a 5-second timeout.
- No test starts, stops, or modifies any container or service state.
- `make test-integration MARKS=storage` filters to storage tests only (verified with `pytest -m storage --collect-only`).

## Design Notes

- Shared step texts (`container status is healthy`, `the response status is 200`) are defined once in `conftest.py` to avoid pytest-bdd registration conflicts.
- Feature-specific steps live in `steps/*.py`; test files import them explicitly to register them with pytest-bdd before scenario collection.
- `conftest.py` adds its own directory (`integration/`) to `sys.path` so test files can import from `steps/` as a plain package without needing the broader import path.
- `assert_container_healthy` in `conftest.py` accepts containers with and without healthchecks (`"none"`) for generality; the `@then("container status is healthy")` BDD step enforces `"healthy"` strictly since postgres-db and sonarqube both have healthchecks configured.
- All assertion error messages include the container name, expected value, actual value, and (for HTTP) the response body truncated to 500 chars (OBS-001).

## Tests Added or Updated

- `tests/integration/features/storage.feature` + `test_storage.py` — IT-001 (postgres-db status + TCP) and IT-002 (minio health endpoint)
- `tests/integration/features/observability.feature` + `test_observability.py` — IT-003 (prometheus targets) and IT-004 (grafana database)
- `tests/integration/features/orchestration.feature` + `test_orchestration.py` — IT-006 (airflow health)
- `tests/integration/features/sso.feature` + `test_sso.py` — IT-005 (authelia health)
- `tests/integration/features/quality.feature` + `test_quality.py` — IT-007 (sonarqube status)

## Test Categories Not Applicable

- `Unit`: Not applicable — this task adds integration boundary tests; there is no domain logic to unit-test independently.
- `Smoke`: Not applicable — service startup smoke is covered by Docker healthchecks in compose definitions; tests here go one level deeper.
- `E2E`: Not applicable — no browser-driven user journey is tested.
- `Regression`: Not applicable — no prior defect is being guarded against.
- `Performance`: Not applicable — the 10-second per-scenario budget in NFR-001 is a practical timeout enforced by httpx, not a performance benchmark.
- `Security`: Not applicable — this task does not touch authentication, authorization, or trust boundaries.
- `Accessibility`: Not applicable — no user-facing UI.
- `Observability`: Not applicable — this task does not introduce or modify operational telemetry behavior.

## Validation Run

```text
python3 -c "ast.parse(...)" on all 13 new .py files — all parse cleanly
uv run pytest --collect-only integration/ — 8 tests collected (7 new + 1 pre-existing), 0 warnings
uv run pytest --collect-only -m storage integration/ — 2/8 selected
uv run pytest --collect-only -m observability integration/ — 2/8 selected
uv run pytest --collect-only -m "storage or observability or orchestration or sso or quality" integration/ — 7/8 selected
```

Full runtime tests cannot be executed in this environment — they require the target service stacks running on `lab-net` inside the test-runner container (`make test-integration`).

## Accessibility Notes

Not applicable — this task does not change any user-facing UI, markup, keyboard behavior, or error states.

## Observability Changes

Not applicable — this task does not introduce or modify operational telemetry behavior. Assertion error messages in steps include container name, expected/actual status, and HTTP response body (≤500 chars) per OBS-001.

## ADR Updates

Not applicable — this task does not touch an ADR-backed architectural decision. Docker Python SDK and pytest-bdd were pre-selected in Task 001 with no cross-cutting architectural impact.

## Unresolved Assumptions or Follow-Up

- Full runtime execution requires target stacks running on `lab-net`; run `make test-integration` after starting the relevant profile stacks to confirm all scenarios pass.
- The `sonarqube` healthcheck in `compose/quality.yml` uses a TCP probe (`/dev/tcp/127.0.0.1/9000`), not an HTTP probe, so IT-007 checks container health status rather than an HTTP endpoint. If SonarQube adds an HTTP health endpoint in future, IT-007 should be updated to call it.
