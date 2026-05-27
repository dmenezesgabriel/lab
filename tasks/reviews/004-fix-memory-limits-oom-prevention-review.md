---
id: "004"
issue: "tasks/issues/004-fix-memory-limits-oom-prevention.md"
created: 2026-05-26
updated: 2026-05-26
resolved: 2026-05-26
---

# Review: Fix memory limits and CPU caps to prevent OOM kills and CPU throttling

## Related Task

- `tasks/issues/004-fix-memory-limits-oom-prevention.md`

## Overall Verdict

**Pass**

No Blocking findings. Both Non-blocking findings resolved: F-001 corrected in issue spec; F-002 confirmed via live `docker stats`.

## Findings

| ID | Level | Requirement | Description | Evidence |
|----|-------|-------------|-------------|----------|
| F-001 | Non-blocking | AC-001 | ~~AC-001 stated the expected byte value as `1610612736` labeled "2304 MB in bytes"; that is 1536 MB (old value). Correct value is `2415919104`.~~ **Resolved**: issue spec corrected to `2415919104`. | `tasks/issues/004-fix-memory-limits-oom-prevention.md` AC-001 |
| F-002 | Non-blocking | OBS-001, OBS-002 | ~~Runtime observability checks deferred pending live containers.~~ **Resolved**: `docker stats cadvisor` → 0.09% CPU (threshold < 12% ✓); `docker stats airflow-webserver` → 199.6 MiB / 1.5 GiB (threshold < 1.25 GiB ✓). | live `docker stats` output |

## AC Evaluation

| AC | Result | Notes |
|----|--------|-------|
| AC-001 | Pass | Both `airflow-webserver` and `airflow-scheduler` render `memswap_limit: "2415919104"` (= 2304 MB). The AC's stated byte value is a typo (1610612736 = 1536 MB); the "or equivalent YAML" clause and FR-001 both confirm 2304 MB is correct. See F-001. |
| AC-002 | Pass | `docker-compose.yml:525` reads `- /tmp:size=128m`. Change confirmed in `git diff`. |
| AC-003 | Pass | `cadvisor` service renders `cpus: 0.5` and `deploy.resources.limits.cpus: 0.5` (verified via `docker compose --profile observability-extras --profile observability config`). |
| AC-004 | Pass | `grep -n "memswap_limit"` output confirms `x-resources-small` (line 61), `x-resources-medium` (line 76), and `x-resources-large` (line 91) are unchanged at 192m, 384m, and 512m respectively. `git diff` contains no changes to those lines. |

## Test Coverage Evaluation

| Test Category | Status | Notes |
|---------------|--------|-------|
| Unit | Not applicable | No isolatable function logic — Docker Compose resource declarations only. |
| Integration | Not applicable | No service interaction or data-flow logic changes. |
| Smoke (SMK-001) | Present | `docker compose config --quiet` exits 0 — verified. |
| Smoke (SMK-002) | Present | `docker stats airflow-webserver --no-stream` → 199.6 MiB / 1.5 GiB limit. Limit is 1.5 GiB ✓, usage below 1.25 GiB ✓. |
| Smoke (SMK-003) | Present | `docker stats cadvisor --no-stream` → 0.09% CPU. Below 12% threshold ✓, no throttle signs. |
| E2E | Not applicable | No user journey involves resource limit declarations. |
| Regression (REG-001) | Present | `grep -n "memswap_limit"` confirms postgres-db, grafana, and loki anchors unchanged; git diff contains no resource-limit changes beyond the three targeted lines. |
| Performance | Not applicable | Task adjusts declared limits, not measured latency. |
| Security | Not applicable | Resource limits are not a security boundary in this context. |
| Usability | Not applicable | No user-facing behavior changes. |

## Observability Evaluation

| OBS ID | Requirement | Status | Notes |
|--------|-------------|--------|-------|
| OBS-001 | `docker stats cadvisor` CPU% below 12% of host total after one housekeeping cycle | Met | `docker stats cadvisor --no-stream` → **0.09%** CPU, 175.1 MiB / 192 MiB. Well below the 12% threshold. |
| OBS-002 | `docker stats airflow-webserver` MEM USAGE below 1.25 GiB during normal operation | Met | `docker stats airflow-webserver --no-stream` → **199.6 MiB / 1.5 GiB** limit. Well below the 1.25 GiB threshold. |

## ADR Compliance

Not applicable — no ADR dependencies listed in the task.

## Convention Notes

None. The inline CPU override on `cadvisor` (cpus top-level + full deploy block) correctly follows the established Docker Compose YAML anchor-merge pattern: the `deploy` block is repeated in full because YAML merge does not recursively override nested maps. This is consistent with the service-level override pattern already present at lines 412–427 (sonarqube).

## Unresolved Assumptions or Follow-Up

- **Out-of-scope changes in working tree**: The `git diff HEAD` also contains unrelated uncommitted changes (Airflow secrets moved to env vars, postgres-db profile additions, Prometheus rules volume mount). These belong to prior tasks (003 and others) and do not affect any resource limit covered by this task. They are not a finding against task 004 but should be committed as part of their respective tasks before this diff is finalised.
