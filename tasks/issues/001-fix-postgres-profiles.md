---
id: "001"
created: 2026-05-26
updated: 2026-05-26
status: active
---

# Task: Fix postgres-db missing profiles for quality and lineage

## Priority

P0 — SonarQube and Marquez cannot start at all when their profiles are launched without `model-registry` or `airflow`, because postgres-db is excluded from the stack.

## Dependencies

- No task dependency; this is a standalone fix.
- No ADR dependency; this task uses existing architecture.

## Assignability

**AFK** — the change is a 2-line addition to `docker-compose.yml`; all acceptance criteria are verifiable by running compose commands.

## Context

`postgres-db` is the shared metadata database for MLflow, Airflow, Marquez, and SonarQube. In `docker-compose.yml:223`, the service declares only `profiles: [model-registry, airflow]`. Marquez (`lineage` profile) and SonarQube (`quality` profile) both declare `depends_on: postgres-db: condition: service_healthy`, but when those profiles are started in isolation, Docker Compose excludes `postgres-db` from the stack and the dependent containers immediately fail.

The fix is adding `quality` and `lineage` to the `postgres-db` profiles list.

## Use Cases

- **Feature**: Profile-isolated stack startup
- **Scenario**: Operator starts SonarQube alone for a code quality scan
- **Given** no other profiles are running
- **When** `docker compose --profile quality up -d` is executed
- **Then** `postgres-db` starts, becomes healthy, and `sonarqube` starts successfully

- **Scenario**: Operator starts Marquez alone for lineage browsing
- **Given** no other profiles are running
- **When** `docker compose --profile lineage up -d` is executed
- **Then** `postgres-db` starts, becomes healthy, and `marquez` starts successfully

## Definition of Ready

- `docker-compose.yml` is accessible and the `postgres-db` service definition is at line 223.
- The `sonarqube` and `marquez` services already declare `depends_on: postgres-db: condition: service_healthy`.

## Functional Requirements

- `FR-001`: `postgres-db` must start whenever the `quality` profile is activated.
- `FR-002`: `postgres-db` must start whenever the `lineage` profile is activated.
- `FR-003`: Existing `model-registry` and `airflow` profile behavior must remain unchanged.

## Non-Functional Requirements

- `NFR-001`: The change must not alter `postgres-db` resource limits, startup command, or healthcheck.
- `NFR-002`: `docker compose config --quiet` must exit 0 after the change.

## Observability Requirements

- `OBS-001`: Not applicable — this task changes only profile membership; no operational behavior changes.

## Acceptance Criteria

- `AC-001`: **Given** only `--profile quality` is activated, **When** `docker compose up -d` runs, **Then** both `postgres-db` and `sonarqube` containers appear in `docker ps`.
- `AC-002`: **Given** only `--profile lineage` is activated, **When** `docker compose up -d` runs, **Then** both `postgres-db` and `marquez` containers appear in `docker ps`.
- `AC-003`: **Given** `--profile model-registry` is activated alone, **When** `docker compose up -d` runs, **Then** `postgres-db` still starts as before.

## Required Tests

### Unit Tests

Not applicable — this task changes only Docker Compose profile metadata; there is no isolated logic to unit-test.

### Integration Tests

Not applicable — profile membership is verified by the smoke tests below.

### Smoke Tests

- `SMK-001`: **Scenario**: SonarQube starts with postgres-db on quality profile alone
  **Given** no lab containers are running
  **When** `docker compose --profile quality up -d --wait` is executed
  **Then** `docker ps --format '{{.Names}}'` includes both `postgres-db` and `sonarqube`
  Covers `AC-001`, `FR-001`.

- `SMK-002`: **Scenario**: Marquez starts with postgres-db on lineage profile alone
  **Given** no lab containers are running
  **When** `docker compose --profile lineage up -d --wait` is executed
  **Then** `docker ps --format '{{.Names}}'` includes both `postgres-db` and `marquez`
  Covers `AC-002`, `FR-002`.

### End-to-End Tests

Not applicable — no user journey involves this change; profile isolation is verified by smoke tests.

### Regression Tests

Not applicable — no known prior defect to guard against.

### Performance Tests

Not applicable — profile metadata change has no runtime performance impact.

### Security Tests

Not applicable — this task does not touch authentication, secrets, or network exposure.

### Usability Tests

Not applicable — no user-facing behavior changes.

### Observability Tests

Not applicable — no logs, metrics, or traces are affected.

## Definition of Done

- `docker-compose.yml` `postgres-db.profiles` includes `quality` and `lineage`.
- `docker compose config --quiet` exits 0.
- `SMK-001` and `SMK-002` pass.
- No other service's behavior has changed.
