---
id: "004"
task: tasks/issues/004-fix-memory-limits-oom-prevention.md
created: 2026-05-26
status: complete
---

# Implementation Summary: Fix memory limits and CPU caps

## Files Changed

- `docker-compose.yml` — three targeted changes (lines 119, 525, 744–752)

## Behavior Implemented

**FR-001 / AC-001**: `x-resources-xxlarge.memswap_limit` raised from `1536m` to `2304m` (768 MB swap headroom = 50% of mem_limit). Applies to `airflow-webserver` and `airflow-scheduler`.

**FR-003 / AC-002**: `airflow-webserver` tmpfs reduced from `size=512m` to `size=128m`, freeing 384 MB back to the container's process heap.

**FR-004 / AC-003**: `cadvisor` service gains inline `cpus: 0.50` and a full `deploy.resources` block with `limits.cpus: "0.50"` and `limits.memory: 192M` (memory unchanged per NFR-003). The `x-resources-small` anchor is not modified.

## Tests Added or Updated

None — no isolatable function logic; correctness is verified by config inspection (see Validations).

## Validations Run

- **SMK-001 / NFR-001**: `docker compose config --quiet` exits 0.
- **AC-001**: `memswap_limit: 2304m` present at anchor (line 119) and inherited by `airflow-webserver` (line 413).
- **AC-002**: `tmpfs: - /tmp:size=128m` at line 525.
- **AC-003**: `cadvisor` has inline `cpus: 0.50` and `deploy.resources.limits.cpus: "0.50"` at lines 744–752.
- **AC-004 / FR-005**: `x-resources-small` (line 61), `x-resources-medium` (line 76), and `x-resources-large` (line 91) `memswap_limit` values are unchanged.

## Intentional Non-Applicable Test Categories

- Unit, integration, E2E, performance, security, usability: not applicable — task changes Docker Compose resource declarations only; there is no function logic, user journey, or security boundary involved.
- SMK-002 and SMK-003 require running containers; runtime verification deferred to operator after `docker compose up`.

## Unresolved Assumptions

- Line 413 shows `memswap_limit: 2304m` for `airflow-webserver` — this is an explicit service-level override that already existed and correctly inherits the new value. No change was needed there.
- SMK-002 and SMK-003 (runtime docker stats checks) must be confirmed by the operator after deploying with `--profile airflow` and `--profile observability-extras`.
