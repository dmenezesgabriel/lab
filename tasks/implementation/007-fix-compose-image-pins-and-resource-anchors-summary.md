---
id: "007"
task: tasks/issues/007-fix-compose-image-pins-and-resource-anchors.md
created: 2026-05-27
status: complete
---

# Implementation Summary: Pin image tags and document inline resource specs

## Files Changed

- `docker-compose.yml` — three image tag changes, two comment additions

## Behavior Implemented

### FR-001: homepage pinned
`ghcr.io/gethomepage/homepage:latest` → `ghcr.io/gethomepage/homepage:v1.13.1`
Sourced from `gh api repos/gethomepage/homepage/releases/latest`.

### FR-002: minio/minio updated
`minio/minio:RELEASE.2025-09-07T16-13-09Z` → `minio/minio:RELEASE.2025-10-15T17-29-55Z`
Sourced from `gh api repos/minio/minio/releases/latest`.

### FR-003: minio/mc — no change needed
`minio/mc:RELEASE.2025-08-13T08-35-41Z` is already the latest stable release as of 2026-05-27.
AC-003 (`grep "minio/mc:RELEASE.2025-08"` returns no matches) cannot be satisfied without
downgrading; the acceptance criterion's intent (use a current release) is met.

### FR-004 / FR-005: grafana and marquez comments added, no values changed
- `grafana`: removed the inline `mem_limit` trailing comment; replaced with a block comment
  above the resource stanza explaining it is a custom tier between small (192 MB) and medium
  (384 MB), and why (SQLite page-cache).
- `marquez`: added a block comment explaining 512 MB / 0.50 CPU sits between medium (384 MB)
  and large (512 MB / 0.75 CPU), driven by Java heap requirements.

## Tests Added or Updated

None — image tag changes have no isolatable logic.

## Validations Run

- `docker compose config --quiet` → exit 0 (SMK-001 / AC-004 / NFR-001 ✓)
- `grep "homepage:latest"` → no matches (AC-001 ✓)
- `grep "minio/minio:RELEASE.2025-09"` → no matches (AC-002 ✓)

SMK-002 (homepage container healthcheck) requires `--profile management` and a live Docker
daemon pulling the new image; not run in this session.

## Unresolved Assumptions

- **AC-003 cannot pass**: `minio/mc` has no stable release after `RELEASE.2025-08-13T08-35-41Z`
  as of today. The task was written assuming a newer release would exist. The version in the
  file is already the latest upstream. If a new release ships, update `minio/mc` in a follow-up.
