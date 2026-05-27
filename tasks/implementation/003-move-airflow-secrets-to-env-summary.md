---
id: "003"
task: "Move hardcoded Airflow secrets out of docker-compose.yml"
status: complete
date: 2026-05-26
---

# Implementation Summary

## Files Changed

- `docker-compose.yml` — replaced two hardcoded secret values in `x-airflow-env` with compose variable references (`${AIRFLOW__API_AUTH__JWT_SECRET}`, `${AIRFLOW__API_SERVER__SECRET_KEY}`); Docker Compose substitutes these from `.env` at parse time, so the anchor still supplies both values to all three Airflow services without duplication.
- `.env` — added both variables with freshly generated `token_hex(32)` values.
- `.env.template` — added both variable names with `# generate with: python3 -c "import secrets; print(secrets.token_hex(32))"` hints.

## Behavior Implemented

Both Airflow secrets are now sourced from `.env` (gitignored) rather than version control. The `x-airflow-env` YAML anchor continues to supply the values to `airflow-init`, `airflow-webserver`, and `airflow-scheduler` via compose variable substitution — no per-service duplication.

## Tests Added or Updated

None — per task specification, no unit, integration, or e2e tests apply to environment variable sourcing.

## Validations Run

| Check | Result |
|---|---|
| `AC-001`: `grep -E "OpN6nUDy6b\|your-super-secret" docker-compose.yml` | 0 matches |
| `AC-002`: `docker compose --profile airflow config` shows `.env` values | Pass — all 3 services render generated values |
| `AC-003`: `.env.template` contains both vars with generation hint | Pass |
| `NFR-001`: `docker compose config --quiet` exits 0 | Exit 0 |
| `SMK-001`: config output contains neither original secret string | Pass |

## Unresolved Assumptions

`ST-001` (`grep -rE "OpN6nUDy6b|your-super-secret" . --exclude='.env'`) returns one match: `services/airflow/webserver_config.py:117`, which uses `"your-super-secret-key-change-me"` as the `os.getenv()` fallback default. The task explicitly states "no change needed there." This string is a code-level fallback, not an injected credential, and is never reached when `.env` is populated. Removing the fallback (or replacing it with an explicit error) would harden the code further but is out of scope for this task.
