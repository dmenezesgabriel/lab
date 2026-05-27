---
id: "008"
created: 2026-05-26
updated: 2026-05-26
status: active
---

# Task: Fix observability service config hygiene — log levels, cross-profile scrape noise, and dashboard deletion

## Priority

P2 — Three low-friction config gaps produce ongoing operational noise: Alloy logs at `info` while its peers log at `warn` (generating verbose output that Loki then ingests from itself); Prometheus logs `connection refused` for five targets every 30–60 s when `observability-extras` is not running; and provisioned Grafana dashboards can be deleted from the UI, which confuses operators when they reappear after restart.

## Dependencies

- No task dependency; can start independently.
- No ADR dependency; all three changes use existing configuration patterns.

## Assignability

**AFK** — all three changes are single-line edits to existing service config files with deterministic target values.

## Context

**1. Alloy log level (`services/alloy/config.alloy:2`)**
```
logging { level = "info" }
```
Loki (`log_level: warn`) and Tempo (`log_level: warn`) both use `warn`. Alloy at `info` emits one structured log line per container log line it processes and per OTLP span received. In a resource-constrained environment these logs amplify I/O and fill Loki with internal telemetry. Set to `warn`.

**2. Prometheus cross-profile scrape errors (`services/prometheus/prometheus.yaml`)**
Prometheus is in the `observability` profile. The config statically references five targets that are only present in the `observability-extras` profile: `cadvisor:8080`, `tempo:3200`, `alloy:12345`, `otel-collector:8889`, and `pushgateway:9091`. When running `observability` without `observability-extras`, Prometheus logs a `connection refused` scrape error for each target every 30–60 s. This is not a crash, but it adds noise to every Prometheus log tail and fills the `scrape_duration_seconds` metric with failures.

The fix is a YAML comment block above each cross-profile target group explaining that the target requires `observability-extras` to be active. This documents the expected behavior without adding brittle health checks.

**3. Grafana dashboard deletion (`services/grafana/grafana_dashboards.yaml:8`)**
```yaml
disableDeletion: false
```
Provisioned dashboards can be deleted from the Grafana UI. They reappear after the next Grafana restart (or the 300-second update interval). This creates a confusing operator experience: the dashboard disappears, then reappears. Set `disableDeletion: true`.

## Use Cases

- **Feature**: Quiet observability stack operation
- **Scenario**: Operator tails alloy logs while the stack is under normal load
- **Given** alloy log level is `warn`
- **When** containers emit normal log output and spans are processed
- **Then** alloy logs are silent unless a warning or error condition occurs

- **Scenario**: Operator deletes a provisioned dashboard by mistake
- **Given** `disableDeletion: true` in the dashboards provisioner config
- **When** the operator attempts to delete a provisioned dashboard in the Grafana UI
- **Then** the delete button is disabled and the dashboard cannot be removed from the UI

## Definition of Ready

- `services/alloy/config.alloy` line 2 is accessible.
- `services/prometheus/prometheus.yaml` cross-profile target jobs are identifiable.
- `services/grafana/grafana_dashboards.yaml` line 8 is accessible.

## Functional Requirements

- `FR-001`: Alloy `logging.level` must be changed from `"info"` to `"warn"`.
- `FR-002`: Each cross-profile job in `prometheus.yaml` (`cadvisor`, `tempo`, `alloy`, `otel-collector`, `pushgateway`) must have an inline comment stating it requires the `observability-extras` profile.
- `FR-003`: `grafana_dashboards.yaml` `disableDeletion` must be set to `true`.

## Non-Functional Requirements

- `NFR-001`: Alloy must restart cleanly after the log level change.
- `NFR-002`: Prometheus must restart cleanly after the comment additions (`promtool check config` must exit 0).
- `NFR-003`: Grafana must restart cleanly after the dashboards provider change.

## Observability Requirements

- `OBS-001`: After setting alloy to `warn`, `docker logs alloy --since=1m` during normal operation must produce significantly fewer lines than before (ideally zero lines when no warnings exist).
- `OBS-002`: In Grafana, provisioned dashboards must show a lock icon or a disabled delete button when `disableDeletion: true` is active.

## Acceptance Criteria

- `AC-001`: **Given** the updated alloy config, **When** `grep "level" services/alloy/config.alloy` runs, **Then** it shows `level = "warn"`.
- `AC-002`: **Given** the updated prometheus config, **When** `docker exec prometheus promtool check config /etc/prometheus/prometheus.yml` runs, **Then** it exits 0.
- `AC-003`: **Given** Grafana is running with the updated provisioner config, **When** a provisioned dashboard is opened in the UI, **Then** the delete option is not available.
- `AC-004`: **Given** alloy restarted with `warn` level, **When** `docker logs alloy --since=2m` is tailed during normal operation (no errors), **Then** zero log lines are emitted.

## Required Tests

### Unit Tests

Not applicable — these are YAML and River config changes with no isolatable logic.

### Integration Tests

Not applicable — config correctness is verified by process startup checks and smoke tests.

### Smoke Tests

- `SMK-001`: **Scenario**: Alloy restarts cleanly with warn log level
  **Given** the updated `services/alloy/config.alloy`
  **When** `docker compose restart alloy` completes
  **Then** `curl -sf http://localhost:12345/-/ready` exits 0
  Covers `AC-001`, `NFR-001`.

- `SMK-002`: **Scenario**: Prometheus config is valid after comment additions
  **Given** the updated `services/prometheus/prometheus.yaml`
  **When** `docker exec prometheus promtool check config /etc/prometheus/prometheus.yml` runs
  **Then** it exits 0
  Covers `AC-002`, `NFR-002`.

- `SMK-003`: **Scenario**: Grafana restarts cleanly with disableDeletion true
  **Given** the updated `services/grafana/grafana_dashboards.yaml`
  **When** `docker compose restart grafana` completes and the healthcheck passes
  **Then** `curl -sf http://localhost:3001/api/health` exits 0 (via Caddy) or direct `docker exec grafana wget -qO- http://localhost:3000/api/health` exits 0
  Covers `FR-003`, `NFR-003`.

### End-to-End Tests

Not applicable — no complete user journey changes.

### Regression Tests

Not applicable — no known prior defect.

### Performance Tests

Not applicable — log level and comment changes have no measurable runtime impact.

### Security Tests

Not applicable — this task does not touch authentication, secrets, or network exposure.

### Usability Tests

- `UX-001`: Open any provisioned dashboard in the Grafana UI and verify the delete/remove button is absent or disabled. Covers `AC-003`, `OBS-002`.

### Observability Tests

- `OT-001`: After restarting alloy with `warn` level and waiting 2 minutes of normal operation, run `docker logs alloy --since=2m` and verify zero log lines are produced. Covers `AC-004`, `OBS-001`.

## Definition of Done

- `services/alloy/config.alloy` `logging.level` is `"warn"`.
- `services/prometheus/prometheus.yaml` cross-profile jobs have inline `# requires: observability-extras profile` comments.
- `services/grafana/grafana_dashboards.yaml` `disableDeletion: true`.
- `SMK-001`, `SMK-002`, and `SMK-003` pass.
- `UX-001` and `OT-001` pass.
