---
id: "003"
created: 2026-05-26
updated: 2026-05-26
status: active
---

# Task: Move hardcoded Airflow secrets out of docker-compose.yml

## Priority

P0 — Two secrets are committed verbatim in `docker-compose.yml`: the JWT signing key used for API authentication tokens and the Flask session signing key (currently a placeholder never changed). Both are readable by anyone with repo access.

## Dependencies

- No task dependency; can start independently.
- No ADR dependency; `.env` is already the established pattern for this repo (`.env.template` exists).

## Assignability

**AFK** — the destination (`.env`) and the source (two `environment:` entries in `docker-compose.yml`) are unambiguous; no architectural decision is required.

## Context

`docker-compose.yml` currently hardcodes two secrets directly in the `x-airflow-env` anchor:

```yaml
# line 18
AIRFLOW__API_AUTH__JWT_SECRET: "OpN6nUDy6b+Wa4QF6TPQsMcVxltHBV8PC8FvofpWLMM="
# line 20
AIRFLOW__API_SERVER__SECRET_KEY: "your-super-secret-key-change-me"
```

`AIRFLOW__API_AUTH__JWT_SECRET` signs the JWTs issued to API clients. `AIRFLOW__API_SERVER__SECRET_KEY` signs Flask sessions for the web UI. The second one is a placeholder that was never replaced.

`.env` is already gitignored. `.env.template` already documents the pattern. Both secrets must be moved there with generated default values documented in `.env.template`.

`webserver_config.py:117` reads `AIRFLOW__API_SERVER__SECRET_KEY` from the environment — no change needed there.

## Use Cases

- **Feature**: Secret hygiene
- **Scenario**: Developer clones the repo and starts the stack
- **Given** the developer copies `.env.template` to `.env` and fills in the secrets
- **When** `docker compose --profile airflow up -d` runs
- **Then** Airflow starts with the developer-supplied secrets, not shared defaults from version control

## Definition of Ready

- `.env.template` exists at the repo root.
- `.env` is listed in `.gitignore`.
- `docker-compose.yml` `x-airflow-env` anchor is at line 10.

## Functional Requirements

- `FR-001`: `AIRFLOW__API_AUTH__JWT_SECRET` must be read from the environment (`.env` file) rather than hardcoded in `docker-compose.yml`.
- `FR-002`: `AIRFLOW__API_SERVER__SECRET_KEY` must be read from the environment rather than hardcoded in `docker-compose.yml`.
- `FR-003`: `.env.template` must document both variables with a `# generate with: python3 -c "import secrets; print(secrets.token_hex(32))"` hint.
- `FR-004`: `.env` must contain generated (non-placeholder) values for both variables.
- `FR-005`: `docker-compose.yml` must not contain either secret string after this change.

## Non-Functional Requirements

- `NFR-001`: `docker compose config --quiet` must exit 0 after the change.
- `NFR-002`: The `x-airflow-env` anchor must still supply both variables to all three Airflow services (init, webserver, scheduler) via `env_file` or environment reference without duplication.

## Observability Requirements

- `OBS-001`: Not applicable — secret rotation is a configuration concern; no operational telemetry changes.

## Acceptance Criteria

- `AC-001`: **Given** the updated `docker-compose.yml`, **When** `grep -E "OpN6nUDy6b|your-super-secret" docker-compose.yml` runs, **Then** it returns no matches.
- `AC-002`: **Given** `.env` contains `AIRFLOW__API_AUTH__JWT_SECRET` and `AIRFLOW__API_SERVER__SECRET_KEY`, **When** `docker compose --profile airflow config` runs, **Then** both variables appear with their `.env` values in the rendered config.
- `AC-003`: **Given** `.env.template` is inspected, **When** it is read, **Then** both variable names appear with a generation hint comment.

## Required Tests

### Unit Tests

Not applicable — this task moves environment variable declarations; there is no isolated logic to unit-test.

### Integration Tests

Not applicable — secret injection is verified by the smoke test below.

### Smoke Tests

- `SMK-001`: **Scenario**: Airflow config renders secrets from .env
  **Given** `.env` contains non-empty values for both secrets
  **When** `docker compose --profile airflow config` runs
  **Then** the output contains neither `"OpN6nUDy6b+Wa4QF6TPQsMcVxltHBV8PC8FvofpWLMM="` nor `"your-super-secret-key-change-me"`
  Covers `AC-001`, `AC-002`.

### End-to-End Tests

Not applicable — no user journey changes.

### Regression Tests

Not applicable — no known prior defect.

### Performance Tests

Not applicable — environment variable sourcing has no measurable performance impact.

### Security Tests

- `ST-001`: Run `grep -rE "OpN6nUDy6b|your-super-secret" .` (excluding `.env`) and verify zero matches after the change. Covers `FR-005`, `AC-001`.

### Usability Tests

Not applicable — no user-facing behavior.

### Observability Tests

Not applicable — no logs, metrics, or traces are affected.

## Definition of Done

- Both secrets removed from `docker-compose.yml`.
- `.env.template` documents both variables with a generation hint.
- `.env` contains generated values for both variables.
- `docker compose config --quiet` exits 0.
- `SMK-001` and `ST-001` pass.
