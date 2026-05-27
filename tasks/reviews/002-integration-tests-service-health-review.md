---
id: "002"
issue: "tasks/issues/002-integration-tests-service-health.md"
created: 2026-05-27
updated: 2026-05-27
---

# Review: Integration Tests for Service Health

## Related Task

- `tasks/issues/002-integration-tests-service-health.md`

## Overall Verdict

**Pass**

No Blocking findings. One Non-blocking finding against OBS-001; implementer should address before closing.

## Findings

| ID | Level | Requirement | Description | Evidence |
|----|-------|-------------|-------------|----------|
| F-001 | Non-blocking | OBS-001 | Shared `then_response_200` step omits the service/container name from the assertion message. Failures for IT-002 (MinIO) and IT-005 (Authelia) do not name the service inline, requiring the reader to correlate with the pytest scenario output rather than reading the assertion string alone. | `tests/integration/conftest.py:70` |

## AC Evaluation

| AC | Result | Notes |
|----|--------|-------|
| AC-001 | Pass | `storage.feature` IT-001 has both the container health check and TCP step. `then_container_healthy` (conftest.py:60–65) asserts `status == "running"` and `health == "healthy"`; `postgres_tcp_reachable` (storage_steps.py:22–30) asserts TCP to `postgres-db:5432` with 5 s timeout. |
| AC-002 | Pass | `get_minio_health` (storage_steps.py:33–38) calls `http://minio:9000/minio/health/ready` with `timeout=5`; `then_response_200` (conftest.py:68–72) asserts HTTP 200 with body truncated to 500 chars. |
| AC-003 | Pass | `prometheus_has_active_targets` (observability_steps.py:20–29) asserts `len(data["data"]["activeTargets"]) >= 1` with status code check and 500-char body in message. |
| AC-004 | Pass | `grafana_database_ok` (observability_steps.py:41–50) asserts `data.get("database") == "ok"` with status code, db_status, and body in message. |
| AC-005 | Pass | `get_authelia_health` (sso_steps.py:11–16) calls `http://authelia:9091/api/health` with `timeout=5`; `then_response_200` asserts HTTP 200. |
| AC-006 | Pass | `airflow_components_healthy` (orchestration_steps.py:19–33) asserts `scheduler.status == "healthy"` and `metadatabase.status == "healthy"` with status code, both component statuses, and body in message. |
| AC-007 | Pass | `check_sonarqube_container` (quality_steps.py:12–16) retrieves the container; `then_container_healthy` (conftest.py:53–65) asserts `status == "running"` and `health == "healthy"`. |

## Test Coverage Evaluation

| Test Category | Status | Notes |
|---------------|--------|-------|
| Unit | Not applicable | No domain logic to unit-test independently; stated in issue. |
| Integration — IT-001 | Present | `tests/integration/test_storage.py` + `features/storage.feature` scenario 1 |
| Integration — IT-002 | Present | `tests/integration/test_storage.py` + `features/storage.feature` scenario 2 |
| Integration — IT-003 | Present | `tests/integration/test_observability.py` + `features/observability.feature` scenario 1 |
| Integration — IT-004 | Present | `tests/integration/test_observability.py` + `features/observability.feature` scenario 2 |
| Integration — IT-005 | Present | `tests/integration/test_sso.py` + `features/sso.feature` |
| Integration — IT-006 | Present | `tests/integration/test_orchestration.py` + `features/orchestration.feature` |
| Integration — IT-007 | Present | `tests/integration/test_quality.py` + `features/quality.feature` |
| Smoke | Not applicable | Service startup smoke covered by Docker healthchecks; stated in issue. |
| E2E | Not applicable | No browser-driven journey; stated in issue. |
| Regression | Not applicable | No prior defect guarded against; stated in issue. |
| Performance | Not applicable | 10 s per-scenario is a practical timeout, not a benchmark; stated in issue. |
| Security | Not applicable | No auth/trust boundaries touched; stated in issue. |
| Usability | Not applicable | No user-facing UI; stated in issue. |
| Observability | Not applicable | No telemetry behavior introduced; stated in issue. |

## Observability Evaluation

| OBS ID | Requirement | Status | Notes |
|--------|-------------|--------|-------|
| OBS-001 | Failed step output includes container name, expected status, actual status, and HTTP response body (truncated to 500 chars). | Partial | Container-based steps (`then_container_healthy`, `assert_container_healthy`) include container name, expected and actual status/health — fully compliant. Service-specific HTTP steps (`prometheus_has_active_targets`, `grafana_database_ok`, `airflow_components_healthy`) include status code, expected value, actual value, and 500-char body — fully compliant. The shared `then_response_200` step includes expected/actual status and body but omits the service name — see F-001. |

## ADR Compliance

Not applicable — no ADR dependencies listed in the task. Docker Python SDK and pytest-bdd were declared native choices with no cross-cutting architectural impact.

## Convention Notes

- F-001 (Non-blocking) — the shared `then_response_200` step in `conftest.py` is intentionally generic to avoid pytest-bdd step registration conflicts. The trade-off is that its assertion message cannot include a service name without structural changes (e.g., a `service_name` fixture). A targeted fix: service-specific When steps could store the service name in a fixture so the Then step can embed it.

## Unresolved Assumptions or Follow-Up

- Full runtime execution requires target stacks to be running on `lab-net`. Runtime confirmation that all 7 scenarios exit 0 must be done via `make test-integration` after starting the relevant profile stacks.
- The `sonarqube` healthcheck in `compose/quality.yml` uses a TCP probe (`/dev/tcp/127.0.0.1/9000`), not an HTTP probe. If SonarQube adds an HTTP health endpoint in future, IT-007 should be updated to call it rather than checking container health status.
- `make test-integration MARKS=storage` filter behavior was verified with `--collect-only` but not with a live run; confirm it exits 0 with the stack running.
