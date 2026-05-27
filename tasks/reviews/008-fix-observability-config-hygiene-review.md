---
id: "008"
issue: "tasks/issues/008-fix-observability-config-hygiene.md"
created: 2026-05-27
updated: 2026-05-27
---

# Review: Fix observability service config hygiene

## Related Task

- `tasks/issues/008-fix-observability-config-hygiene.md`

## Overall Verdict

**Fail**

Blocked by F-001, F-002, F-003, F-004. All three config changes are correct; all four blocking findings are pending runtime verifications required by the Definition of Done. Once the Docker stack is running, executing the four pending tests clears all blockers.

## Findings

| ID | Level | Requirement | Description | Evidence |
|----|-------|-------------|-------------|----------|
| F-001 | Blocking | DoD / SMK-001 | SMK-001 (Alloy restart health check) is marked Pending; DoD requires "SMK-001, SMK-002, and SMK-003 pass" before done. | `tasks/implementation/008-fix-observability-config-hygiene-summary.md` — Smoke Tests table, SMK-001 Status: Pending |
| F-002 | Blocking | DoD / SMK-003 | SMK-003 (Grafana restart health check) is marked Pending; DoD requires it to pass. | Same summary — SMK-003 Status: Pending |
| F-003 | Blocking | DoD / UX-001 / AC-003 | UX-001 (provisioned dashboard delete button absent) is marked Pending; DoD requires "UX-001 and OT-001 pass." AC-003 specifies UI verification that cannot be confirmed from config inspection alone. | Same summary — UX-001 Status: Pending |
| F-004 | Blocking | DoD / OT-001 / AC-004 | OT-001 (zero Alloy log lines during 2-minute normal operation window) is marked Pending; DoD requires it to pass. AC-004 requires observing zero lines after restart, which has not been validated. | Same summary — OT-001 Status: Pending |
| F-005 | Suggestion | FR-002 | The `tempo` job's cross-profile marker is embedded in a descriptive comment (`# Tempo internal metrics — requires: observability-extras profile`) while the other four jobs use a standalone `# requires: observability-extras profile` line. FR-002 is satisfied — the required phrase is present — but the format is inconsistent. | `services/prometheus/prometheus.yaml:54` |

## AC Evaluation

| AC | Result | Notes |
|----|--------|-------|
| AC-001 | Pass | `services/alloy/config.alloy:2` — `level  = "warn"` confirmed in diff and file read. |
| AC-002 | Pass | SMK-002 ran `docker run … promtool check config` against the updated `prometheus.yaml` and exited 0 per implementation summary. |
| AC-003 | Conditional Pass | `services/grafana/grafana_dashboards.yaml:10` — `disableDeletion: true` confirmed. Full criterion requires Grafana to be running; UI verification (UX-001 / F-003) is pending. |
| AC-004 | Fail | Requires running Alloy and a 2-minute observation window; covered by OT-001 which is Pending (F-004). Config change is correct but the outcome has not been observed. |

## Test Coverage Evaluation

| Test Category | Status | Notes |
|---------------|--------|-------|
| Unit | Not applicable | YAML and River config changes with no isolatable logic — per issue. |
| Integration | Not applicable | Config correctness verified by process startup checks and smoke tests — per issue. |
| Smoke (SMK-001) | Pending | `docker compose restart alloy && curl -sf http://localhost:12345/-/ready` — requires running stack. See F-001. |
| Smoke (SMK-002) | Present / Pass | `promtool check config` exits 0 — verified per implementation summary. |
| Smoke (SMK-003) | Pending | `docker compose restart grafana` + health endpoint check — requires running stack. See F-002. |
| E2E | Not applicable | No complete user journey changes — per issue. |
| Regression | Not applicable | No known prior defect — per issue. |
| Performance | Not applicable | Log level and comment changes have no measurable runtime impact — per issue. |
| Security | Not applicable | No auth, secrets, or network exposure changes — per issue. |
| Usability (UX-001) | Pending | Open provisioned dashboard, verify delete button absent — requires running Grafana. See F-003. |
| Observability (OT-001) | Pending | `docker logs alloy --since=2m` must return zero lines — requires 2-minute running Alloy window. See F-004. |

## Observability Evaluation

| OBS ID | Requirement | Status | Notes |
|--------|-------------|--------|-------|
| OBS-001 | `docker logs alloy --since=1m` produces significantly fewer lines during normal operation | Pending | Config change (`level = "warn"`) is correct. OT-001 covers the runtime observation but is Pending (F-004). |
| OBS-002 | Provisioned Grafana dashboards show lock icon or disabled delete button | Pending | `disableDeletion: true` is set. UX-001 covers the UI verification but is Pending (F-003). |

## ADR Compliance

Not applicable — no ADR dependencies listed in the task.

## Convention Notes

- `F-005` — Suggestion — `services/prometheus/prometheus.yaml:54`: the `tempo` job's cross-profile comment format differs from the other four jobs. Four jobs use a standalone `# requires: observability-extras profile` line immediately above the `- job_name:` entry; the `tempo` job appends the phrase to an existing descriptive comment. FR-002 is satisfied but visual consistency would improve scanability if the comment is split or standardised.

## Unresolved Assumptions or Follow-Up

- All four blocking findings (F-001 through F-004) share the same root blocker: a running Docker stack is required. Spinning up the stack and running the five commands below clears all blockers in a single session:
  1. `docker compose restart alloy && curl -sf http://localhost:12345/-/ready` (SMK-001 / F-001)
  2. `docker compose restart grafana && curl -sf http://localhost:3001/api/health` (SMK-003 / F-002)
  3. Open any provisioned dashboard in the Grafana UI and confirm delete is absent (UX-001 / F-003)
  4. Wait 2 minutes, then `docker logs alloy --since=2m` and confirm zero output (OT-001 / F-004)
- The `git diff HEAD` output shows additional changes in `services/alloy/config.alloy` beyond the log level edit (removed `otelcol.receiver.otlp "local"`, removed `otelcol.processor.batch "default"`, renamed `otelcol.exporter.otlp "tempo"` → `"otelcol"`, updated `faro.receiver` output reference). The implementation summary correctly limits task 008's scope to the log level change; those additional edits appear to belong to task 006. No action required for this review, but it confirms that multiple task changes are co-mingled in the working tree.
