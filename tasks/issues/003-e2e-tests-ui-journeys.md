---
id: "003"
created: 2026-05-27
updated: 2026-05-27
status: active
---

# Task: E2E tests for UI journeys with Playwright and pytest-bdd

## Priority

P3 — Depends on Task 001. Integration tests (Task 003) are not a hard dependency, but this task assumes services are reachable, so they should be stable first.

## Dependencies

- Depends on Task 001 (`001-test-infrastructure-bootstrap.md`) — `tests/Dockerfile` must install Playwright Chromium, `tests/uv.lock` must include `playwright` and `pytest-playwright`, and `make test-e2e` target must exist.
- No ADR dependency; pytest-bdd + pytest-playwright is a well-established combination with no cross-cutting architecture implications.
- Requires target stacks to be running on `lab-net` (same prerequisite as Task 002).
- Services accessed: `homepage:3000`, `authelia:9091`, `grafana:3000`, `mlflow:5000`, `airflow-webserver:8080`.

## Assignability

**AFK** — service URLs, login credentials (all are default lab credentials defined in compose env vars), and expected UI elements are known from the compose configuration and service documentation. Safe to delegate.

## Context

E2E tests exercise real browser journeys through the lab UIs, running headless Chromium inside the `test-runner` container on `lab-net`. Playwright navigates service URLs by internal container hostname (bypassing Caddy/SSO where services expose a direct port) to avoid coupling test reliability to the SSO configuration.

pytest-bdd is used for Gherkin feature files because it integrates directly with pytest fixtures — the `page` fixture from `pytest-playwright` is available in step definitions without any bridging code. This keeps the toolchain flat: one test runner, one fixture scope, no separate Behave process.

Tests live in `tests/e2e/features/` (Gherkin) and `tests/e2e/steps/` (step definitions). A shared `conftest.py` provides the `page` fixture and a `base_url` helper per service.

## Use Cases

- **Feature**: Homepage availability
- **Scenario**: Developer confirms the homepage loads after a stack restart
- **Given** the `management` profile stack is running
- **When** the developer runs `make test-e2e MARKS=homepage`
- **Then** Playwright loads the homepage, the page title is verified, and the test exits 0

- **Feature**: Authelia login portal
- **Scenario**: Developer confirms the SSO portal is reachable before configuring OAuth clients
- **Given** the `sso` profile stack is running
- **When** `make test-e2e MARKS=sso` is run
- **Then** Playwright confirms the Authelia login form is present

## Definition of Ready

- Task 001 is complete: `tests/Dockerfile` builds with `playwright install --with-deps chromium`, and `make test-e2e` target exists.
- All target service containers expose ports accessible on `lab-net` by hostname.

## Functional Requirements

- `FR-001`: Playwright Chromium is installed inside the test-runner image during `docker build` (via `playwright install --with-deps chromium`), not at test runtime.
- `FR-002`: Feature files live in `tests/e2e/features/` with one file per service or service group (`homepage.feature`, `authelia.feature`, `grafana.feature`, `mlflow.feature`, `airflow.feature`).
- `FR-003`: Step definitions live in `tests/e2e/steps/` with a module per feature file.
- `FR-004`: `tests/e2e/conftest.py` provides a `browser` fixture (session-scoped, headless Chromium via `playwright.chromium.launch`) and a `page` fixture (function-scoped, new browser context per scenario).
- `FR-005`: No scenario logs in with real credentials through the SSO flow unless that journey is the explicit test subject (`authelia.feature`); for other services, tests use direct internal URLs that bypass Caddy.
- `FR-006`: Tests are tagged `@pytest.mark.e2e` globally and with a per-service marker (`@pytest.mark.homepage`, etc.). The `make test-e2e` target runs all e2e markers; individual markers can be passed via `make test-e2e MARKS=grafana`.
- `FR-007`: Each step that navigates to a URL waits for `networkidle` before asserting, with a 10-second timeout.

## Non-Functional Requirements

- `NFR-001`: Each scenario completes in under 30 seconds; the full E2E suite under 3 minutes.
- `NFR-002`: Tests run headless with no display server. The test-runner Dockerfile must not require `DISPLAY` or Xvfb.
- `NFR-003`: No screenshot or video is saved by default; these can be enabled via `PLAYWRIGHT_ARTIFACTS=1` env var for debugging.

## Observability Requirements

- `OBS-001`: On failure, the step output includes the URL navigated to, the page title at the time of failure, and the first console error if any — sufficient to diagnose redirect loops or blank pages without manual repro.

## Acceptance Criteria

- `AC-001`: **Given** `homepage` is running, **When** `E2E-001` runs, **Then** Playwright loads `http://homepage:3000`, the page title contains "Homepage", and no unhandled console errors are emitted.
- `AC-002`: **Given** `authelia` is running, **When** `E2E-002` runs, **Then** Playwright loads `http://authelia:9091`, and the DOM contains an input with `name="username"` or `autocomplete="username"`.
- `AC-003`: **Given** `grafana` is running, **When** `E2E-003` runs, **Then** Playwright loads `http://grafana:3000/login`, and the page title contains "Grafana".
- `AC-004`: **Given** `mlflow` is running, **When** `E2E-004` runs, **Then** Playwright loads `http://mlflow:5000`, and the page renders an experiments list or an empty state message without a 5xx error.
- `AC-005`: **Given** `airflow-webserver` is running, **When** `E2E-005` runs, **Then** Playwright loads `http://airflow-webserver:8080`, and the page renders the Airflow UI or a login redirect (not a 5xx or blank page).

## Required Tests

### Unit Tests

Not applicable — E2E step helpers have no isolated logic worth unit testing separately from the browser interaction.

### Integration Tests

Not applicable — service reachability is already covered in Task 003. E2E tests here go one level deeper: rendered UI.

### Smoke Tests

Not applicable — browser-based smoke is what the E2E scenarios already are; a separate smoke category would duplicate them.

### End-to-End Tests

- `E2E-001`: **Scenario**: Homepage loads without authentication  
  **Given** the `management` profile stack is running  
  **When** Playwright navigates to `http://homepage:3000`  
  **Then** the page title contains "Homepage"  
  **And** no unhandled console errors are logged  
  Covers `AC-001`, `FR-005`.

- `E2E-002`: **Scenario**: Authelia login portal is reachable  
  **Given** the `sso` profile stack is running  
  **When** Playwright navigates to `http://authelia:9091`  
  **Then** the page contains a username input field  
  Covers `AC-002`.

- `E2E-003`: **Scenario**: Grafana UI loads  
  **Given** the `observability` profile stack is running  
  **When** Playwright navigates to `http://grafana:3000/login`  
  **Then** the page title contains "Grafana"  
  Covers `AC-003`.

- `E2E-004`: **Scenario**: MLflow UI renders experiment state  
  **Given** the `model-registry` profile stack is running  
  **When** Playwright navigates to `http://mlflow:5000`  
  **Then** the page renders without a 5xx error  
  **And** the page contains "Experiments" or an empty-state indicator  
  Covers `AC-004`.

- `E2E-005`: **Scenario**: Airflow UI renders or redirects cleanly  
  **Given** the `airflow` profile stack is running  
  **When** Playwright navigates to `http://airflow-webserver:8080`  
  **Then** the HTTP response status is not 5xx  
  **And** the rendered page is not blank  
  Covers `AC-005`.

### Regression Tests

Not applicable — no prior defect is being guarded against.

### Performance Tests

Not applicable — the 30-second per-scenario budget in `NFR-001` is a practical timeout, not a benchmark.

### Security Tests

Not applicable — this task does not test authentication logic, authorization rules, or trust boundaries. The Authelia scenario only confirms the login form is present, not that auth is enforced.

### Usability Tests

Not applicable — UI layout and accessibility validation are out of scope for this infrastructure lab.

### Observability Tests

Not applicable — this task does not introduce or modify operational telemetry.

## Definition of Done

- `tests/e2e/features/` contains one feature file per service (homepage, authelia, grafana, mlflow, airflow).
- `tests/e2e/steps/` contains matching step definition modules.
- `tests/e2e/conftest.py` provides `browser` (session) and `page` (function) fixtures backed by headless Chromium.
- `make test-e2e` runs all five scenarios and exits 0 when target stacks are healthy.
- `make test-e2e MARKS=grafana` runs only the Grafana scenario.
- Playwright Chromium is confirmed installed in the test-runner image during `docker build`.
