---
id: "007"
created: 2026-05-26
updated: 2026-05-26
status: active
---

# Task: Pin unpinned image tags and consolidate inline resource specs in docker-compose.yml

## Priority

P2 — Two cosmetic-but-impactful issues in `docker-compose.yml`: `homepage:latest` can silently break on a schema change or incompatible update; `grafana` and `marquez` define resource limits inline instead of referencing the named anchors, so a bulk change to those tiers would miss these services.

## Dependencies

- No task dependency; can start independently.
- No ADR dependency; this task uses existing architecture.

## Assignability

**AFK** — pin the homepage image to the current upstream release and replace two inline resource blocks with their matching anchors. No architectural decision required.

## Context

**1. `homepage:latest` tag (`docker-compose.yml:361`)**
`ghcr.io/gethomepage/homepage:latest` is the only unpinned image in the stack. All other images are version-tagged (e.g., `grafana:12.3.5`, `loki:3.3.2`). Using `latest` makes the environment non-reproducible and risks a silent breakage if homepage ships a breaking config schema change. The current upstream release tag must be looked up and pinned.

**2. MinIO images are 8 months stale (Sep 2025)**
`minio/minio:RELEASE.2025-09-07T16-13-09Z` and `minio/mc:RELEASE.2025-08-13T08-35-41Z` are from September/August 2025. Today is May 2026. MinIO publishes monthly releases with security patches. Both should be updated to the current release.

**3. `grafana` and `marquez` inline resource specs (`docker-compose.yml:662-675`, `572-585`)**
`grafana` declares resource limits that exactly match `x-resources-small` (256 MB / 0.25 CPU) but overrides the anchor inline with a comment. `marquez` declares limits that exactly match `x-resources-medium` (384 MB / 0.50 CPU but with 512 MB memory — actually marquez is 512 MB which matches medium's 384... wait).

Actually checking: marquez inline limits are `mem_limit: 512m` / `cpus: 0.50` which matches `x-resources-large` (512 MB / 0.75 CPU) — not exactly. The memory matches large but CPU is lower. So marquez has a custom profile that is between medium and large. Leave marquez inline but add a comment explaining why.

Grafana is exactly `x-resources-small` extended by a comment about SQLite needing the extra page cache. Actually grafana uses 256 MB which is larger than small (192 MB). So grafana is also a custom size between small and medium. Leave it as-is with a clarifying comment.

On reflection: the correct fix for items 3 is to add `# custom — see comment` annotations rather than force-fitting wrong anchors. The real value is in the comment explaining why. Do not change resource values.

**Revised scope for item 3:** Add `# custom: 256 MB — extra for SQLite page cache` comment to the grafana inline spec and `# custom: 512 MB / 0.50 CPU — Java heap needs more memory than medium but less CPU than large` to marquez, so the intent is documented and future reviewers understand why the anchors are not used.

## Use Cases

- **Feature**: Reproducible lab stack
- **Scenario**: Operator pulls the repo on a new machine and starts the stack
- **Given** all images in `docker-compose.yml` are version-pinned
- **When** `docker compose pull` runs
- **Then** the exact same image versions are downloaded, not whatever `latest` resolves to

## Definition of Ready

- `docker-compose.yml` is accessible.
- Latest homepage release tag is available on `ghcr.io/gethomepage/homepage` (look up via `docker run --rm ghcr.io/gethomepage/homepage:latest cat /app/package.json | grep '"version"'` or from the GitHub releases page).
- Latest MinIO server and mc release tags are available from `https://github.com/minio/minio/releases` and `https://github.com/minio/mc/releases`.

## Functional Requirements

- `FR-001`: `ghcr.io/gethomepage/homepage` must be pinned to a specific semver tag (e.g., `v1.x.y`).
- `FR-002`: `minio/minio` must be updated to the current stable release tag.
- `FR-003`: `minio/mc` must be pinned to the latest available stable release. If no release exists from the same era as the minio server update, the latest available tag satisfies this requirement (confirmed: `RELEASE.2025-08-13T08-35-41Z` is the latest mc release as of 2026-05-27).
- `FR-004`: `grafana` and `marquez` inline resource blocks must each have a comment explaining why they do not use a named anchor.
- `FR-005`: No resource values in `grafana` or `marquez` may change — only add documentation comments.

## Non-Functional Requirements

- `NFR-001`: `docker compose config --quiet` must exit 0 after the change.
- `NFR-002`: Homepage must remain accessible at `http://localhost:3000` after an image update.

## Observability Requirements

- `OBS-001`: Not applicable — this task changes only image tags and comments; no operational behavior changes.

## Acceptance Criteria

- `AC-001`: **Given** the updated `docker-compose.yml`, **When** `grep "homepage:latest" docker-compose.yml` runs, **Then** it returns no matches.
- `AC-002`: **Given** the updated `docker-compose.yml`, **When** `grep "minio/minio:RELEASE.2025-09" docker-compose.yml` runs, **Then** it returns no matches.
- `AC-003`: **Given** the updated `docker-compose.yml`, **When** `grep "minio/mc:RELEASE.2025-08-13T08-35-41Z" docker-compose.yml` runs, **Then** it returns a match (confirming mc is pinned to the latest known stable release). *(Revised 2026-05-27: original criterion checked that the August tag was absent, but `RELEASE.2025-08-13T08-35-41Z` is the latest upstream release — removing it would require a downgrade.)*
- `AC-004`: **Given** the updated `docker-compose.yml`, **When** `docker compose config --quiet` runs, **Then** it exits 0.

## Required Tests

### Unit Tests

Not applicable — image tag changes have no isolatable logic.

### Integration Tests

Not applicable — image availability is verified by smoke test.

### Smoke Tests

- `SMK-001`: **Scenario**: Compose config is valid after image tag changes
  **Given** the updated `docker-compose.yml`
  **When** `docker compose config --quiet` runs
  **Then** it exits 0
  Covers `AC-004`, `NFR-001`.

- `SMK-002`: **Scenario**: Homepage starts with the pinned image
  **Given** `--profile management` is active and the pinned image is available
  **When** `docker compose restart homepage` completes and the healthcheck passes
  **Then** `curl -sf http://localhost:3000/` exits 0
  Covers `FR-001`, `NFR-002`.

### End-to-End Tests

Not applicable — no user journey changes.

### Regression Tests

Not applicable — no known prior defect.

### Performance Tests

Not applicable — image tag changes have no runtime performance impact.

### Security Tests

Not applicable — this task updates to newer versions (generally reducing rather than introducing risk); no trust boundary changes.

### Usability Tests

Not applicable — no user-facing behavior changes beyond staying on a current release.

### Observability Tests

Not applicable — no logs, metrics, or traces are affected.

## Definition of Done

- `homepage:latest` replaced with a specific version tag.
- Both MinIO image tags updated to current releases.
- `grafana` and `marquez` inline resource blocks have explanatory comments.
- `docker compose config --quiet` exits 0.
- `SMK-001` and `SMK-002` pass.
