---
id: "005"
issue: "tasks/issues/005-add-tempo-block-retention.md"
created: 2026-05-26
updated: 2026-05-27
---

# Review: Add Tempo block retention

## Related Task

- `tasks/issues/005-add-tempo-block-retention.md`

## Overall Verdict

**Pass — all findings resolved (2026-05-27)**

No Blocking findings. All three Non-blocking findings and the Suggestion have been resolved.

## Findings

| ID | Level | Requirement | Description | Evidence | Resolution |
|----|-------|-------------|-------------|----------|------------|
| F-001 | Non-blocking | DoD | Change is uncommitted. The `compactor` block exists in the working tree but has not been committed to git. A `git checkout -- services/tempo/tempo.yaml` would silently discard it. | `git status` shows `M services/tempo/tempo.yaml`; `git diff HEAD` shows the compactor block is unstaged | **Resolved 2026-05-27** — committed in `884d5c4` ("fix: services config"). Working tree is clean. |
| F-002 | Non-blocking | SMK-001 / AC-001 / NFR-001 | SMK-001 has not been executed. The DoD requires `curl -sf http://localhost:3200/ready` to exit 0 after `docker compose restart tempo`. The config is structurally correct but health has not been confirmed at runtime. | Implementation summary: "to be run by operator" | **Resolved 2026-05-27** — `docker compose restart tempo` succeeded; `curl -sf http://localhost:3200/ready` returned `ready` (exit 0). SMK-001 **PASS**. |
| F-003 | Non-blocking | OT-001 / AC-003 / OBS-001 | OT-001 has not been executed. The DoD requires at least one `tempodb_compaction_*` metric line after ≥60 s uptime. Cannot be verified from config alone. | Implementation summary: "to be run after ≥60 s uptime" | **Resolved 2026-05-27** — `tempodb_compaction_errors_total 0` present at 61 s uptime. OT-001 **PASS**. Note: `tempodb_compaction_objects_combined_total` is absent — expected in a lab with no ingested traces; that counter appears only after a completed compaction cycle. |
| F-004 | Suggestion | FR-002 | `ring.kvstore.store: memberlist` is Tempo's default for the `all` single-binary target. Explicitly setting it is harmless but redundant; omitting it would reduce config noise without changing behavior. | `services/tempo/tempo.yaml:27–29` | **Resolved 2026-05-27** — ring config was never included in the committed version of the file. `services/tempo/tempo.yaml` has no `compactor.ring` block. |

## AC Evaluation

| AC | Result | Notes |
|----|--------|-------|
| AC-001 | **Pass** | `curl -sf http://localhost:3200/ready` returned `ready` (exit 0) after `docker compose restart tempo`. SMK-001 executed 2026-05-27. |
| AC-002 | **Pass** | Tempo accepted the config with no parse-failure error; `/ready` endpoint is healthy, confirming the config was loaded successfully. |
| AC-003 | **Pass** | `tempodb_compaction_errors_total 0` present at 61 s uptime. Compactor is active and error-free. OT-001 executed 2026-05-27. |

## Test Coverage Evaluation

| Test Category | Status | Notes |
|---------------|--------|-------|
| Unit | Not applicable | YAML config change has no isolatable unit logic — per issue. |
| Integration | Not applicable | Config correctness verified by smoke and observability tests — per issue. |
| Smoke (SMK-001) | **Pass** | Executed 2026-05-27: `docker compose restart tempo` + `curl -sf http://localhost:3200/ready` → `ready` (exit 0). |
| E2E | Not applicable | No user journey touches trace retention lifecycle directly — per issue. |
| Regression | Not applicable | No known prior defect — per issue. |
| Performance | Not applicable | Compaction is async, doesn't affect ingestion latency — per issue. |
| Security | Not applicable | No auth, secrets, or network exposure changes — per issue. |
| Usability | Not applicable | No user-facing behavior changes — per issue. |
| Observability (OT-001) | **Pass** | Executed 2026-05-27 at 61 s uptime: `tempodb_compaction_errors_total 0` present. |

## Observability Evaluation

| OBS ID | Requirement | Status | Notes |
|--------|-------------|--------|-------|
| OBS-001 | `tempodb_compaction_objects_combined_total` visible in Prometheus after compactor is active | **Partial pass** | Compactor is active (`tempodb_compaction_errors_total 0` at 61 s uptime; no errors). `tempodb_compaction_objects_combined_total` absent — expected: this counter only appears after a compaction cycle completes, which requires ingested trace blocks. Will appear under real load. |

## ADR Compliance

Not applicable — no ADR dependencies listed in the task. The implementation summary correctly notes that single-binary compactor configuration is a standard Tempo pattern and no ADR was needed.

## Convention Notes

- F-004 — Suggestion — `services/tempo/tempo.yaml:27–29`: the `ring.kvstore.store: memberlist` key under `compactor.ring` mirrors a pattern from `services/loki/loki.yaml` where ring store is explicitly set (Loki uses `inmemory`, Tempo should use `memberlist` for multi-process compatibility). The explicit setting is consistent with Loki's convention of being explicit about ring stores, so this may be intentional. Classified as Suggestion rather than a convention deviation.

## Unresolved Assumptions or Follow-Up

- **F-001 — Resolved**: Committed in `884d5c4`. Working tree is clean.
- **F-002 / F-003 — Resolved**: SMK-001 and OT-001 both executed and passed on 2026-05-27 (see Findings table).
- **OBS-001 partial**: `tempodb_compaction_objects_combined_total` will appear in Prometheus after the first real compaction cycle runs under ingested load. No action needed — compactor is confirmed active.
- **NFR-002 memory**: The 192 MB container memory limit has not been stress-tested. Recommend running `docker stats tempo` during the first compaction cycle under real load to confirm the limit is not breached.
