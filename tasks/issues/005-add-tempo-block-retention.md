---
id: "005"
created: 2026-05-26
updated: 2026-05-26
status: active
---

# Task: Add Tempo block retention to prevent unbounded disk growth

## Priority

P1 — Tempo writes traces to `/var/tempo/blocks` with no compactor or retention configured. The ingester creates very small blocks (500 KB max, 5-minute max duration), which means blocks accumulate rapidly. Without a TTL, disk fills and Tempo crashes.

## Dependencies

- No task dependency; can start independently.
- No ADR dependency; Tempo's compactor is a standard single-binary config block.

## Assignability

**AFK** — the retention value (24 h, matching Loki's `retention_period: 24h`) is determined from the existing config; no architectural decision is required.

## Context

`services/tempo/tempo.yaml` has an `ingester` section creating blocks with `max_block_bytes: 500000` (500 KB) and `max_block_duration: 5m`. At that rate, a moderately active lab stack can produce hundreds of blocks per day. There is no `compactor` section, so blocks are never merged or expired.

Loki already sets `limits_config.retention_period: 24h`. Tempo should match to keep the observability pipeline consistent: traces are retained for one day, then deleted.

The fix adds a `compactor` section with `block_retention: 24h`. Tempo's compactor runs in the `all` target (single-binary mode) alongside the ingester and distributor — no topology change needed.

## Use Cases

- **Feature**: Trace retention lifecycle
- **Scenario**: Lab runs overnight and the disk is checked in the morning
- **Given** Tempo is configured with 24 h block retention
- **When** 24 hours have elapsed since the first trace was received
- **Then** blocks older than 24 hours are deleted and disk usage stabilizes

## Definition of Ready

- `services/tempo/tempo.yaml` is accessible.
- Tempo runs in `all` target (single-binary mode) — confirmed at `target: all` (implicitly, via `stream_over_http_enabled: true` and single service definition).
- Available disk space is 114 GiB (49% used on a 233 GiB volume).

## Functional Requirements

- `FR-001`: Tempo must delete trace blocks older than 24 hours.
- `FR-002`: The compactor must run in-process (no new container or sidecar needed).
- `FR-003`: The compactor working directory must be on the same persistent volume as blocks (`/var/tempo`).

## Non-Functional Requirements

- `NFR-001`: Tempo must restart cleanly after the config change — `docker compose restart tempo` followed by `GET /ready` must return HTTP 200.
- `NFR-002`: The compactor must not consume more than 64 MB of additional memory during a compaction cycle (the `small` resource limit of 192 MB must remain sufficient).

## Observability Requirements

- `OBS-001`: Prometheus scrapes `tempo:3200/metrics` — after the compactor is active, `tempodb_compaction_objects_combined_total` must be visible in the Prometheus UI as evidence that compaction is running.

## Acceptance Criteria

- `AC-001`: **Given** the updated `tempo.yaml`, **When** Tempo starts, **Then** `GET http://localhost:3200/ready` returns HTTP 200.
- `AC-002`: **Given** the updated `tempo.yaml`, **When** Tempo has been running for at least 30 seconds, **Then** `curl -s localhost:3200/api/status/buildinfo` includes no error indicating a config parse failure.
- `AC-003`: **Given** the compactor is active, **When** `docker exec tempo wget -qO- http://localhost:3200/metrics | grep tempodb_compaction` runs, **Then** at least one compaction metric line is returned.

## Required Tests

### Unit Tests

Not applicable — YAML configuration changes have no isolatable unit logic.

### Integration Tests

Not applicable — Tempo config correctness is verified by the smoke test and metric check below.

### Smoke Tests

- `SMK-001`: **Scenario**: Tempo starts healthy after adding the compactor section
  **Given** the updated `services/tempo/tempo.yaml`
  **When** `docker compose restart tempo` completes and 30 seconds pass
  **Then** `curl -sf http://localhost:3200/ready` exits 0
  Covers `AC-001`, `NFR-001`.

### End-to-End Tests

Not applicable — no user journey involves trace retention lifecycle directly.

### Regression Tests

Not applicable — no known prior defect.

### Performance Tests

Not applicable — compaction runs asynchronously and does not affect trace ingestion latency.

### Security Tests

Not applicable — this task does not touch authentication, secrets, or network exposure.

### Usability Tests

Not applicable — no user-facing behavior changes.

### Observability Tests

- `OT-001`: After Tempo has been running for at least 60 seconds, run `docker exec tempo wget -qO- http://localhost:3200/metrics | grep tempodb_compaction` and verify at least one metric line is present. Covers `AC-003`, `OBS-001`.

## Definition of Done

- `services/tempo/tempo.yaml` includes a `compactor` section with `block_retention: 24h`.
- `SMK-001` passes.
- `OT-001` returns at least one compaction metric.
- Tempo memory usage observed in `docker stats` remains within the 192 MB limit.
