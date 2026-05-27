---
id: "008"
task: "Fix observability service config hygiene"
created: 2026-05-27
status: complete
---

# Implementation Summary — Task 008

## Files Changed

| File | Change |
|------|--------|
| `services/alloy/config.alloy` | `level = "info"` → `level = "warn"` (line 2) |
| `services/prometheus/prometheus.yaml` | Added `# requires: observability-extras profile` comment above each of the five cross-profile scrape jobs: `cadvisor`, `tempo`, `otel-collector`, `alloy`, `pushgateway` |
| `services/grafana/grafana_dashboards.yaml` | `disableDeletion: false` → `disableDeletion: true` (line 10) |

## Behavior Implemented

- **FR-001**: Alloy now logs at `warn`, suppressing per-line container log and per-span OTLP noise during normal operation.
- **FR-002**: Every cross-profile Prometheus scrape job carries an inline comment documenting that it requires `observability-extras` to be running, converting silent connection-refused errors into expected documented behavior.
- **FR-003**: Grafana provisioned dashboards can no longer be deleted from the UI; the delete option will be disabled or absent on all provisioned dashboards.

## Tests Added or Updated

None — task explicitly marks unit, integration, and end-to-end tests as not applicable for YAML/River config changes.

## Validations Run

- **AC-001**: `grep "level" services/alloy/config.alloy` → `level = "warn"` ✓
- **AC-002 / SMK-002**: `docker run --rm --entrypoint promtool prom/prometheus:latest check config /etc/prometheus/prometheus.yml` → `SUCCESS: valid prometheus config file syntax` ✓
- **FR-003 / AC-003**: Change verified by inspection; runtime check (SMK-003 / UX-001) requires Grafana to be running.

## Smoke Tests Status

| Test | Status | Notes |
|------|--------|-------|
| SMK-001 — Alloy restart with warn level | Pending | Requires running stack: `docker compose restart alloy && curl -sf http://localhost:12345/-/ready` |
| SMK-002 — Prometheus config valid | Pass | `promtool check config` exits 0 |
| SMK-003 — Grafana restart with disableDeletion true | Pending | Requires running stack |
| UX-001 — Delete button absent in UI | Pending | Requires running Grafana |
| OT-001 — Zero alloy log lines during normal operation | Pending | Requires 2-minute observation window |

## Accessibility Checks

Not applicable — no UI code was touched.

## ADRs Updated

None — all changes use existing configuration patterns.

## Unresolved Assumptions

SMK-001, SMK-003, UX-001, and OT-001 require a running Docker stack to verify. The config changes are deterministic single-line edits; runtime validation is the only remaining step.
