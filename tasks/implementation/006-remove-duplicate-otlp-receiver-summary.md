---
id: "006"
issue: tasks/issues/006-remove-duplicate-otlp-receiver-from-alloy.md
created: 2026-05-27
updated: 2026-05-27
verified: 2026-05-27
---

# Implementation Summary: Remove duplicate OTLP receiver from Alloy config

## Files changed

- `services/alloy/config.alloy` — removed dead OTLP receiver, batch processor, and tempo exporter; added otelcol exporter targeting otel-collector; rewired faro traces output; applied canonical tab-based formatting.

## Behavior implemented

- `FR-001`: Removed `otelcol.receiver.otlp "local"` block (gRPC 4317 / HTTP 4318).
- `FR-002`: Removed `otelcol.processor.batch "default"` block (now unreferenced).
- `FR-003`: Removed `otelcol.exporter.otlp "tempo"` block (now unreferenced).
- `FR-004`: Added `otelcol.exporter.otlp "otelcol"` block targeting `otel-collector:4317` with `tls.insecure = true`.
- `FR-005`: Updated `faro.receiver "local"` traces output from `otelcol.processor.batch.default.input` to `otelcol.exporter.otlp.otelcol.input`.
- `FR-006`: `otelcol.exporter.loki "local"` left unchanged.
- `NFR-002`: Applied `alloy fmt` canonical formatting (tabs) — file was previously using spaces; `alloy fmt --test` now exits 0.

## Design notes

The original file used spaces for indentation, which `alloy fmt` rejects. Since NFR-002 requires the formatter to pass, the entire file was written in the canonical tab-indented style emitted by `alloy fmt`. No logic was changed beyond the required blocks.

## Tests added or updated

None — Alloy River config has no isolatable unit logic (per task: unit and integration tests not applicable).

## Validations run

- `AC-001`: `grep "otelcol.receiver.otlp"` returns no matches — PASS.
- `AC-004`: `grep "otelcol.exporter.otlp"` shows exactly one block named `"otelcol"`, no `"tempo"` block — PASS.
- `NFR-002`: `docker run grafana/alloy fmt --test /etc/alloy/config.alloy` exits 0 — PASS.

## ADRs updated

None — this is a routine dead-code removal with unambiguous routing.

## Observability added or changed

None added. The new `otelcol.exporter.otlp "otelcol"` exporter will emit `alloy_otelcol_exporter_sent_spans_total{exporter="otelcol/otelcol"}` when faro traces are received (OT-002 / AC-003).

## Skipped or not-applicable test categories

- **Unit tests**: Not applicable — Alloy River config is declarative wiring; no isolatable logic.
- **Integration tests**: Not applicable — component wiring is verified by runtime smoke and observability tests.
- **End-to-end tests**: Not applicable — Faro trace delivery is verified by OT-002 observability test.
- **Regression tests**: Not applicable — no prior defect in this path.
- **Performance tests**: Not applicable — removing a receiver reduces memory; no regression risk.
- **Security tests**: Not applicable — removes an unused receiver; no trust boundary changes.
- **Usability tests**: Not applicable — no user-facing behavior.
- **SMK-001**: Requires a running Docker environment; not executed in this session. Run `docker compose restart alloy` and verify `curl -sf http://localhost:12345/-/ready` exits 0.
- **OT-001 / OT-002**: Require running stack; not executed in this session.

## Runtime validation (2026-05-27)

- `SMK-001` / `AC-002`: **Pass** — `curl -sf http://localhost:12345/-/ready` exits 0 after stack start.
- `OT-001` / `OBS-002`: **Pass** — Alloy UI API shows 8 components, 0 errors.
- `OT-002` / `AC-003` / `OBS-001`: **Pass** — `otelcol_exporter_sent_spans_total{exporter="otlp/otelcol.exporter.otlp.otelcol"} 1` after test Faro trace ingested via `POST /collect`.

## Unresolved assumptions or follow-up work

- None. All deferred checks have been executed.
- `.editorconfig` added with `[*.alloy] indent_style = tab` to prevent spaces-vs-tabs drift.
