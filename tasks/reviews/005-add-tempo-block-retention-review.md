---
id: "005"
issue: "tasks/issues/005-add-tempo-block-retention.md"
created: 2026-05-26
updated: 2026-05-26
---

# Review: Add Tempo block retention

## Related Task

- `tasks/issues/005-add-tempo-block-retention.md`

## Overall Verdict

**Pass**

No Blocking findings. Three Non-blocking findings and one Suggestion require attention before or shortly after the operator runs the runtime verification steps.

## Findings

| ID | Level | Requirement | Description | Evidence |
|----|-------|-------------|-------------|----------|
| F-001 | Non-blocking | DoD | Change is uncommitted. The `compactor` block exists in the working tree but has not been committed to git. A `git checkout -- services/tempo/tempo.yaml` would silently discard it. | `git status` shows `M services/tempo/tempo.yaml`; `git diff HEAD` shows the compactor block is unstaged |
| F-002 | Non-blocking | SMK-001 / AC-001 / NFR-001 | SMK-001 has not been executed. The DoD requires `curl -sf http://localhost:3200/ready` to exit 0 after `docker compose restart tempo`. The config is structurally correct but health has not been confirmed at runtime. | Implementation summary: "to be run by operator" |
| F-003 | Non-blocking | OT-001 / AC-003 / OBS-001 | OT-001 has not been executed. The DoD requires at least one `tempodb_compaction_*` metric line after ≥60 s uptime. Cannot be verified from config alone. | Implementation summary: "to be run after ≥60 s uptime" |
| F-004 | Suggestion | FR-002 | `ring.kvstore.store: memberlist` is Tempo's default for the `all` single-binary target. Explicitly setting it is harmless but redundant; omitting it would reduce config noise without changing behavior. | `services/tempo/tempo.yaml:27–29` |

## AC Evaluation

| AC | Result | Notes |
|----|--------|-------|
| AC-001 | Cannot verify (runtime) | Config is structurally valid; SMK-001 not yet run (→ F-002). No parse-breaking syntax detected. |
| AC-002 | Cannot verify (runtime) | Requires live Tempo to confirm `/api/status/buildinfo` returns no parse-failure error. Config structure is correct YAML with recognized Tempo keys. |
| AC-003 | Cannot verify (runtime) | Requires OT-001 to be run after ≥60 s uptime (→ F-003). Compactor section is present and should produce metrics once active. |

## Test Coverage Evaluation

| Test Category | Status | Notes |
|---------------|--------|-------|
| Unit | Not applicable | YAML config change has no isolatable unit logic — per issue. |
| Integration | Not applicable | Config correctness verified by smoke and observability tests — per issue. |
| Smoke (SMK-001) | Defined / Not executed | Defined in issue; pending operator run post-deploy (→ F-002). |
| E2E | Not applicable | No user journey touches trace retention lifecycle directly — per issue. |
| Regression | Not applicable | No known prior defect — per issue. |
| Performance | Not applicable | Compaction is async, doesn't affect ingestion latency — per issue. |
| Security | Not applicable | No auth, secrets, or network exposure changes — per issue. |
| Usability | Not applicable | No user-facing behavior changes — per issue. |
| Observability (OT-001) | Defined / Not executed | Defined in issue; pending operator run after ≥60 s uptime (→ F-003). |

## Observability Evaluation

| OBS ID | Requirement | Status | Notes |
|--------|-------------|--------|-------|
| OBS-001 | `tempodb_compaction_objects_combined_total` visible in Prometheus after compactor is active | Cannot verify (runtime) | Compactor section is present; metric will appear only after a compaction cycle runs. Covered by OT-001 (→ F-003). |

## ADR Compliance

Not applicable — no ADR dependencies listed in the task. The implementation summary correctly notes that single-binary compactor configuration is a standard Tempo pattern and no ADR was needed.

## Convention Notes

- F-004 — Suggestion — `services/tempo/tempo.yaml:27–29`: the `ring.kvstore.store: memberlist` key under `compactor.ring` mirrors a pattern from `services/loki/loki.yaml` where ring store is explicitly set (Loki uses `inmemory`, Tempo should use `memberlist` for multi-process compatibility). The explicit setting is consistent with Loki's convention of being explicit about ring stores, so this may be intentional. Classified as Suggestion rather than a convention deviation.

## Unresolved Assumptions or Follow-Up

- **Commit pending (F-001)**: The compactor change must be committed before it can be considered durably applied. Recommend committing immediately after runtime verification passes.
- **SMK-001 / OT-001 runtime verification (F-002, F-003)**: Both tests must be run by the operator: `docker compose restart tempo`, wait 30 s, `curl -sf http://localhost:3200/ready`; then after ≥60 s, `docker exec tempo wget -qO- http://localhost:3200/metrics | grep tempodb_compaction`. Results should be logged (e.g., appended to this review or a follow-up note) to satisfy the DoD.
- **FR-003 implicit satisfaction**: Tempo's compactor operates directly on the storage backend (`storage.trace.local.path: /var/tempo/blocks`) and has no separate working-directory config. FR-003 is satisfied implicitly — the compactor's I/O stays within `/var/tempo`. No additional config is needed, but this assumption should be confirmed at runtime.
- **NFR-002 memory**: The 192 MB memory limit for the container was not verifiable from config. It must be observed via `docker stats tempo` during the first compaction cycle.
