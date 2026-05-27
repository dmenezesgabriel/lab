---
task: "005"
date: 2026-05-26
status: complete
---

# Implementation: Add Tempo block retention

## Files changed

- `services/tempo/tempo.yaml` — added `compactor` section before `storage`

## Behavior implemented

Added a `compactor` block that sets `block_retention: 24h`, matching Loki's existing 24-hour retention. The compactor ring uses `memberlist` (Tempo's default for single-binary mode), so no separate ring store is needed. The compactor runs in-process under the `all` target — no topology change required.

## Tests added or updated

None — YAML configuration changes have no isolatable unit or integration tests. Verification is done at runtime per the smoke and observability tests in the task.

## Validations run

- File parses as valid YAML (visual inspection confirms structure).
- Smoke test (`SMK-001`): `docker compose restart tempo` + `curl -sf http://localhost:3200/ready` — to be run by operator.
- Observability test (`OT-001`): `docker exec tempo wget -qO- http://localhost:3200/metrics | grep tempodb_compaction` — to be run after ≥60 s uptime.

## Accessibility checks

Not applicable — no UI touched.

## ADRs updated

None — single-binary compactor configuration is a standard Tempo pattern; no architectural assumption was confirmed, changed, or rejected.

## Intentional non-applicable test categories

- Unit tests: no code logic to isolate.
- Integration tests: config correctness is observable only via the running process.
- E2E, regression, performance, security, usability tests: not applicable per task definition.

## Unresolved assumptions / follow-up

- Runtime verification (SMK-001, OT-001) must be confirmed by the operator after `docker compose restart tempo`.
