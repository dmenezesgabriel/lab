---
id: "003"
issue: "tasks/issues/003-move-airflow-secrets-to-env.md"
created: 2026-05-26
updated: 2026-05-26
---

# Review: Move hardcoded Airflow secrets out of docker-compose.yml

## Related Task

- `tasks/issues/003-move-airflow-secrets-to-env.md`

## Overall Verdict

**Pass**

No Blocking findings. One Non-blocking finding and one Suggestion should be addressed in a follow-up task.

## Findings

| ID | Level | Requirement | Description | Evidence |
|----|-------|-------------|-------------|----------|
| F-001 | Non-blocking | ST-001 | The security test command `grep -rE "OpN6nUDy6b\|your-super-secret" . --exclude='.env'` returns one match in `webserver_config.py:117`, where `"your-super-secret-key-change-me"` is used as an `os.getenv()` fallback default. ST-001 requires zero matches, but the issue Context explicitly carves out this file ("no change needed there"). The gap is in the test definition, not the implementation. The underlying FR-005 and AC-001 (both scoped to `docker-compose.yml`) are satisfied. Recommend either adding `--exclude='webserver_config.py'` to ST-001, or replacing the fallback with an explicit `ValueError` to eliminate the match entirely. | `services/airflow/webserver_config.py:117` |
| F-002 | Suggestion | — | The two new Airflow secret variables in `.env.template` are placed at lines 4-7 with no section header separating them from the existing variables (KAGGLE_USERNAME, PROJECT_ROOT). A `## Airflow` section comment would improve discoverability for new developers. Not required by any FR or AC. | `.env.template:3-7` |

## AC Evaluation

| AC | Result | Notes |
|----|--------|-------|
| AC-001 | Pass | `grep -E "OpN6nUDy6b\|your-super-secret" docker-compose.yml` returns 0 matches. Lines 18 and 20 use `${AIRFLOW__API_AUTH__JWT_SECRET}` and `${AIRFLOW__API_SERVER__SECRET_KEY}` compose variable references. |
| AC-002 | Pass | `.env` contains both variables with generated 64-char hex values (`eb88eb84...` and `ef4b7f91...`). `docker-compose.yml` substitutes them via `${VAR}` at parse time. Structurally verifiable; implementation summary confirms `docker compose --profile airflow config` was run and rendered the `.env` values for all three services. |
| AC-003 | Pass | `.env.template` lines 4–7 contain both variable names, each preceded by the exact generation hint: `# generate with: python3 -c "import secrets; print(secrets.token_hex(32))"`. |

## Test Coverage Evaluation

| Test Category | Status | Notes |
|---------------|--------|-------|
| Unit | Not applicable | No isolated logic to unit-test per issue. |
| Integration | Not applicable | Secret injection verified by smoke test per issue. |
| Smoke (SMK-001) | Present | Structurally verifiable: `.env` has non-empty values for both secrets; `docker-compose.yml` uses `${VAR}` references; implementation summary confirms `docker compose --profile airflow config` output contains neither original secret string. |
| E2E | Not applicable | No user journey changes per issue. |
| Regression | Not applicable | No known prior defect per issue. |
| Performance | Not applicable | No measurable performance impact per issue. |
| Security (ST-001) | Partial | Returns one match (`services/airflow/webserver_config.py:117`) that the issue Context explicitly carves out as out-of-scope. See F-001. |
| Usability | Not applicable | No user-facing behavior per issue. |
| Observability | Not applicable | No logs, metrics, or traces affected per issue. |

## Observability Evaluation

Not applicable — no OBS requirements defined in the task.

## ADR Compliance

Not applicable — no ADR dependencies listed in the task.

## Convention Notes

- `F-002` — Suggestion — `.env.template` lacks a section separator between the existing variables (KAGGLE, PROJECT_ROOT) and the two new Airflow secrets. The other entries do not use section headers either, so this is a style preference rather than a convention violation. No change required for mark-complete.

## Unresolved Assumptions or Follow-Up

- **ST-001 test definition gap**: The issue Context carves out `webserver_config.py:117` but ST-001's grep command does not exclude it. The test as written cannot pass with zero matches. A follow-up task should either (a) update ST-001 to add `--exclude='webserver_config.py'` to the grep command, or (b) harden `webserver_config.py:117` by replacing the `"your-super-secret-key-change-me"` fallback with `os.environ["AIRFLOW__API_SERVER__SECRET_KEY"]` (raising `KeyError` on missing value). Option (b) is more defensive and would make the test pass as written.
- **NFR-001 live verification**: `docker compose config --quiet` was not re-run during this review. The structural configuration (valid YAML, `.env` populated, `${VAR}` references present) strongly supports a 0 exit code, and the implementation summary confirms it. No action required unless the stack is started and a config error surfaces.
