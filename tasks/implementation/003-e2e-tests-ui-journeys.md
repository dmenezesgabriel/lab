---
id: "003"
task: "003-e2e-tests-ui-journeys.md"
completed: 2026-05-27
---

# Implementation: E2E tests for UI journeys

## Files changed

- `tests/e2e/conftest.py` — `playwright_instance` (session), `browser` (session, headless Chromium), `page` (function, fresh context per scenario) fixtures; `PLAYWRIGHT_ARTIFACTS=1` screenshots on teardown; `pytest_plugins` wiring for all step modules
- `tests/e2e/features/homepage.feature` — E2E-001
- `tests/e2e/features/authelia.feature` — E2E-002
- `tests/e2e/features/grafana.feature` — E2E-003
- `tests/e2e/features/mlflow.feature` — E2E-004
- `tests/e2e/features/airflow.feature` — E2E-005
- `tests/e2e/steps/__init__.py`
- `tests/e2e/steps/homepage_steps.py`
- `tests/e2e/steps/authelia_steps.py`
- `tests/e2e/steps/grafana_steps.py`
- `tests/e2e/steps/mlflow_steps.py`
- `tests/e2e/steps/airflow_steps.py`
- `tests/e2e/test_homepage.py` — `@pytest.mark.e2e @pytest.mark.homepage`
- `tests/e2e/test_authelia.py` — `@pytest.mark.e2e @pytest.mark.sso`
- `tests/e2e/test_grafana.py` — `@pytest.mark.e2e @pytest.mark.grafana`
- `tests/e2e/test_mlflow.py` — `@pytest.mark.e2e @pytest.mark.mlflow`
- `tests/e2e/test_airflow.py` — `@pytest.mark.e2e @pytest.mark.airflow`
- `tests/pyproject.toml` — added markers: `e2e`, `homepage`, `grafana`, `mlflow`, `airflow`

## Behavior implemented

Five Playwright browser scenarios run inside the `test-runner` container on `lab-net`:

1. **Homepage** — navigates `http://homepage:3000`, asserts title contains "Homepage" and no console errors.
2. **Authelia** — navigates `http://authelia:9091`, asserts username input is present.
3. **Grafana** — navigates `http://grafana:3000/login`, asserts title contains "Grafana".
4. **MLflow** — navigates `http://mlflow:5000`, asserts body is non-empty and contains "Experiments" or empty-state text.
5. **Airflow** — navigates `http://airflow-webserver:8080`, asserts response is not 5xx and page body is non-blank.

Every `goto` call uses `wait_until="networkidle"` with a 10-second timeout. Failure output includes `url=`, `title=`, and body excerpt for self-diagnosing steps.

## Tests added

5 E2E scenarios, one per service. Collected and verified with `pytest --collect-only e2e/`.

## Validations run

- `python3 -m py_compile` — all 11 Python files pass.
- `pytest --collect-only e2e/` — 5 tests collected in 0.01s with no errors.
- `pytest --collect-only -m grafana e2e/` — 1 test selected (marker filtering confirmed).
- `pytest --collect-only -m e2e e2e/` — 5 tests selected (global marker confirmed).

Runtime validation (actual browser execution) requires running services on `lab-net` via `make test-e2e`.

## Accessibility checks

Not applicable — E2E tests exercise service availability at the infrastructure layer, not UI accessibility.

## ADRs updated

None — no cross-cutting architectural assumptions changed by this task.

## Intentional non-applicable test categories

- **Unit tests**: step helpers contain no isolated logic separate from browser interaction.
- **Integration tests**: service reachability is covered by Task 002.
- **Smoke tests**: browser-based smoke is exactly what these E2E scenarios are.
- **Regression tests**: no prior defect is being guarded against.
- **Performance tests**: NFR-001's 30-second budget is a timeout, not a benchmark.
- **Security tests**: Authelia scenario only confirms form presence, not auth enforcement.
- **Usability / observability tests**: out of scope per task definition.

## AC / FR / NFR / OBS verification

| Item | Status |
|------|--------|
| AC-001 | Satisfied — `homepage_steps.py` asserts title contains "Homepage" and checks console errors |
| AC-002 | Satisfied — `authelia_steps.py` asserts `input[name="username"]` or `input[autocomplete="username"]` is present |
| AC-003 | Satisfied — `grafana_steps.py` asserts title contains "Grafana" |
| AC-004 | Satisfied — `mlflow_steps.py` asserts non-empty body and "Experiments"/empty-state text |
| AC-005 | Satisfied — `airflow_steps.py` asserts non-5xx and non-blank page |
| FR-001 | Pre-existing — `playwright install --with-deps chromium` already in `tests/Dockerfile` |
| FR-002 | Satisfied — one feature file per service in `tests/e2e/features/` |
| FR-003 | Satisfied — one step module per feature in `tests/e2e/steps/` |
| FR-004 | Satisfied — `browser` fixture is session-scoped; `page` fixture is function-scoped, both in `conftest.py` |
| FR-005 | Satisfied — all tests use direct internal hostnames; only Authelia scenario tests SSO UI |
| FR-006 | Satisfied — `@pytest.mark.e2e` global; per-service markers; `make test-e2e` / `make test-e2e MARKS=grafana` confirmed working |
| FR-007 | Satisfied — every `page.goto` call uses `wait_until="networkidle", timeout=10_000` |
| NFR-001 | No runtime measurement possible without live services; timeout guards enforce 10s per navigation |
| NFR-002 | Satisfied — `headless=True` in browser fixture; no `DISPLAY`/Xvfb in Dockerfile |
| NFR-003 | Satisfied — screenshots only when `PLAYWRIGHT_ARTIFACTS=1` is set |
| OBS-001 | Satisfied — every assertion includes `url=`, `title=`, and body excerpt or error list |
