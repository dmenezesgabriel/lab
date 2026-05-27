---
id: "003"
issue: "tasks/issues/003-e2e-tests-ui-journeys.md"
created: 2026-05-27
updated: 2026-05-27
---

# Review: E2E Tests for UI Journeys

## Related Task

- `tasks/issues/003-e2e-tests-ui-journeys.md`

## Overall Verdict

**Pass**

No Blocking findings. One Non-blocking finding against OBS-001 (two assertion messages omit the required `title=` field); implementer should address before closing.

## Findings

| ID | Level | Requirement | Description | Evidence |
|----|-------|-------------|-------------|----------|
| F-001 | Non-blocking | OBS-001 | Two assertion messages omit `title=` at failure time. `no_console_errors` (homepage) emits `url=` and `errors=` but not `title=`. `airflow_not_5xx` (airflow) emits `url=` and `status` but not `title=`. OBS-001 requires URL, page title, and first console error in every failure message. | `tests/e2e/steps/homepage_steps.py:34`, `tests/e2e/steps/airflow_steps.py:29` |
| F-002 | Suggestion | — | `mlflow_no_5xx` infers the absence of a 5xx by checking that `body_text.strip()` is non-empty rather than reading `response.status`. In contrast, `airflow_not_5xx` captures and checks `response.status < 500` directly. A 5xx error page that renders non-empty content (e.g., a framework error page) would pass the MLflow assertion while failing the Airflow one. | `tests/e2e/steps/mlflow_steps.py:22–32` |
| F-003 | Suggestion | — | `airflow_not_5xx` wraps its `assert status < 500` inside `if response is not None:`, so a null response silently skips the HTTP status assertion rather than failing. Playwright's `goto` with `wait_until="networkidle"` returns `None` only for non-HTTP navigations, making this unlikely to trigger, but the guard removes observability when it does. | `tests/e2e/steps/airflow_steps.py:24–31` |

## AC Evaluation

| AC | Result | Notes |
|----|--------|-------|
| AC-001 | Pass | `navigate_to_homepage` navigates `http://homepage:3000` with `wait_until="networkidle", timeout=10_000`. `homepage_title_contains` asserts `"Homepage" in title`. `no_console_errors` asserts `not errors` from the console listener wired in `conftest.py`. |
| AC-002 | Pass | `navigate_to_authelia` navigates `http://authelia:9091`. `authelia_has_username_input` uses `locator('input[name="username"], input[autocomplete="username"]')` and asserts `count >= 1`. |
| AC-003 | Pass | `navigate_to_grafana` navigates `http://grafana:3000/login`. `grafana_title_contains` asserts `"Grafana" in title`. |
| AC-004 | Pass | `navigate_to_mlflow` navigates `http://mlflow:5000`. `mlflow_no_5xx` asserts body is non-empty. `mlflow_has_experiments_or_empty_state` asserts body contains `"Experiments"`, `"experiments"`, `"No experiments"`, or `"no experiments"`, with a 300-char body excerpt on failure. |
| AC-005 | Pass | `navigate_to_airflow` navigates `http://airflow-webserver:8080`. `airflow_not_5xx` checks `response.status < 500` (when response is not None). `airflow_page_not_blank` asserts `body_text.strip()` is non-empty with `url=` and `title=` in message. |

## Test Coverage Evaluation

| Test Category | Status | Notes |
|---------------|--------|-------|
| Unit | Not applicable | No isolated step logic; stated in issue. |
| Integration | Not applicable | Service reachability covered by Task 002; stated in issue. |
| Smoke | Not applicable | Browser-based smoke is what these E2E scenarios are; stated in issue. |
| E2E — E2E-001 | Present | `tests/e2e/test_homepage.py` + `features/homepage.feature` |
| E2E — E2E-002 | Present | `tests/e2e/test_authelia.py` + `features/authelia.feature` |
| E2E — E2E-003 | Present | `tests/e2e/test_grafana.py` + `features/grafana.feature` |
| E2E — E2E-004 | Present | `tests/e2e/test_mlflow.py` + `features/mlflow.feature` |
| E2E — E2E-005 | Present | `tests/e2e/test_airflow.py` + `features/airflow.feature` |
| Regression | Not applicable | No prior defect guarded against; stated in issue. |
| Performance | Not applicable | 30-second budget is a timeout, not a benchmark; stated in issue. |
| Security | Not applicable | Authelia scenario only confirms form presence; stated in issue. |
| Usability | Not applicable | UI layout and accessibility out of scope; stated in issue. |
| Observability | Not applicable | No new telemetry introduced; stated in issue. |

## Observability Evaluation

| OBS ID | Requirement | Status | Notes |
|--------|-------------|--------|-------|
| OBS-001 | On failure, step output includes URL navigated to, page title at time of failure, and first console error if any. | Partial | Five of seven assertion messages include both `url=` and `title=`. Two are missing `title=`: `no_console_errors` at `homepage_steps.py:34` and `airflow_not_5xx` at `airflow_steps.py:29`. See F-001. |

## ADR Compliance

Not applicable — no ADR dependencies listed in the task.

## Convention Notes

- `F-002` — Suggestion — `mlflow_steps.py` uses an indirect body-content proxy for the 5xx check while `airflow_steps.py` checks `response.status` directly. The inconsistency is low-risk for SPA behaviour but worth aligning for readability.
- `F-003` — Suggestion — The `if response is not None` guard in `airflow_not_5xx` silently drops the status assertion on null response. Replacing with an explicit `assert response is not None` would make a null response a visible failure rather than a silent pass.

## Unresolved Assumptions or Follow-Up

- Runtime validation (actual browser execution against live stacks) was not performed. The implementation summary confirms `pytest --collect-only` passes and syntax is valid, but AC satisfaction is verified only at the code level. Full confidence requires `make test-e2e` to exit 0 against healthy stacks.
- `NFR-001` (30 s per scenario, 3 min total) cannot be confirmed without a live run. The 10-second `goto` timeout caps individual navigations, but slow network-idle waits on unhealthy services could still exceed the budget.
