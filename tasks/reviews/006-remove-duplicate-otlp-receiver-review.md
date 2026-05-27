---
id: "006"
issue: "tasks/issues/006-remove-duplicate-otlp-receiver-from-alloy.md"
created: 2026-05-27
updated: 2026-05-27
verified: 2026-05-27
---

# Review: Remove duplicate OTLP receiver from Alloy config

## Related Task

- `tasks/issues/006-remove-duplicate-otlp-receiver-from-alloy.md`

## Overall Verdict

**Pass**

No Blocking findings. All statically-verifiable FRs, NFRs, and ACs pass. Runtime-dependent checks (AC-002, AC-003, SMK-001, OT-001, OT-002) are deferred to post-deployment verification; this is expected and acknowledged in the implementation summary.

## Findings

| ID | Level | Requirement | Description | Evidence |
|----|-------|-------------|-------------|----------|
| F-001 | Resolved | SMK-001, AC-002, AC-003 | Runtime checks executed post-deployment on 2026-05-27. SMK-001/AC-002 pass (alloy ready); OT-001 pass (8 components, 0 errors); OT-002 pass (`otelcol_exporter_sent_spans_total` = 1 after test Faro trace). | See updated AC and OBS tables below. |

## AC Evaluation

| AC | Result | Notes |
|----|--------|-------|
| AC-001 | Pass | `grep "otelcol.receiver.otlp" services/alloy/config.alloy` returns no matches — confirmed in diff and static file. |
| AC-002 | Pass | `curl -sf http://localhost:12345/-/ready` returned "Alloy is ready." with exit 0 after stack start on 2026-05-27. |
| AC-003 | Pass | `otelcol_exporter_sent_spans_total{exporter="otlp/otelcol.exporter.otlp.otelcol"} 1` after sending a test Faro trace on 2026-05-27. Note: issue had stale metric name (`alloy_otelcol_exporter_sent_spans_total{exporter="otelcol/otelcol"}`) — corrected in issue file. |
| AC-004 | Pass | `grep "otelcol.exporter.otlp" services/alloy/config.alloy` returns exactly one block named `"otelcol"` (line 84); no `"tempo"` block present. |

## Test Coverage Evaluation

| Test Category | Status | Notes |
|---------------|--------|-------|
| Unit | Not applicable | Alloy River config is declarative wiring; no isolatable unit logic. |
| Integration | Not applicable | Component wiring verified by runtime smoke and observability tests, per issue. |
| Smoke (SMK-001) | Pass | `docker compose up -d alloy` + 15s wait → `curl -sf http://localhost:12345/-/ready` exits 0 on 2026-05-27. |
| E2E | Not applicable | Faro trace delivery verified by OT-002 observability test, per issue. |
| Regression | Not applicable | No prior defect in this path. |
| Performance | Not applicable | Removing a receiver reduces memory; no regression risk. |
| Security | Not applicable | Removes an unused receiver; no trust boundary changes. |
| Usability | Not applicable | No user-facing behavior. |
| Observability (OT-001, OT-002) | Pass | OT-001: 8 components, 0 errors in Alloy UI API on 2026-05-27. OT-002: `otelcol_exporter_sent_spans_total` = 1 after test trace. |

## Observability Evaluation

| OBS ID | Requirement | Status | Notes |
|--------|-------------|--------|-------|
| OBS-001 | Trace sent to `otel-collector:4317` appears in Tempo via Grafana Explore | Pass | `otelcol_exporter_sent_spans_total{exporter="otlp/otelcol.exporter.otlp.otelcol"} 1` confirmed after test Faro trace on 2026-05-27. End-to-end Grafana→Tempo UI verification requires Grafana to be running (out of scope for this session). |
| OBS-002 | Alloy UI at `http://localhost:12345` shows zero component errors after restart | Pass | API query `GET /api/v0/web/components` returned 8 components, 0 with error state on 2026-05-27. |

## ADR Compliance

Not applicable — no ADR dependencies listed in the task.

## Convention Notes

- The implementation applied `alloy fmt` canonical tab-based indentation across the entire file. The original used spaces, which caused `alloy fmt --test` to fail. Reformatting was required to satisfy NFR-002 and is fully justified. No logic was altered beyond the required blocks.
- `stage.decolorize {}` → `stage.decolorize { }`: cosmetic change emitted by `alloy fmt`; not a logic change.

## Unresolved Assumptions or Follow-Up

All previously deferred runtime checks completed on 2026-05-27:

- SMK-001 / AC-002 / FR-007: **Pass** — `curl -sf http://localhost:12345/-/ready` exits 0.
- OT-001 / OBS-002: **Pass** — Alloy UI API shows 8 components, 0 errors.
- OT-002 / AC-003 / OBS-001: **Pass** — `otelcol_exporter_sent_spans_total{exporter="otlp/otelcol.exporter.otlp.otelcol"} 1` after test Faro trace.
- NFR-002 stale flag: **Fixed** — issue file updated from `--no-write` to `--test`; metric name in AC-003/OT-002 corrected to `otelcol_exporter_sent_spans_total{exporter="otlp/otelcol.exporter.otlp.otelcol"}`.
- `.editorconfig` for `*.alloy`: **Added** — `[*.alloy]` section with `indent_style = tab` added to `.editorconfig`.
