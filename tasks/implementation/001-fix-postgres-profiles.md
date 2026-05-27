---
task: "001"
date: 2026-05-26
status: complete
---

# Implementation: Fix postgres-db missing profiles for quality and lineage

## Files changed

- `docker-compose.yml` — added `quality` and `lineage` to `postgres-db.profiles` (line 224–229)

## Behavior implemented

`postgres-db` is now included in the Docker Compose stack whenever `--profile quality` or `--profile lineage` is activated, satisfying FR-001 and FR-002. Existing `model-registry` and `airflow` profile behavior is unchanged (FR-003).

## Tests added or updated

None — no unit or integration tests apply to Docker Compose profile metadata.

## Validations run

- `docker compose config --quiet` — exits 0 (NFR-002 satisfied).

## Smoke tests

SMK-001 and SMK-002 require running containers; they can be verified with:

```bash
# SMK-001
docker compose --profile quality up -d --wait
docker ps --format '{{.Names}}' | grep -E 'postgres-db|sonarqube'

# SMK-002
docker compose --profile lineage up -d --wait
docker ps --format '{{.Names}}' | grep -E 'postgres-db|marquez'
```

## Intentional non-applicable test categories

- Unit, integration, E2E, regression, performance, security, usability, observability — none apply; the change is profile metadata only with no runtime logic.

## Unresolved assumptions

None.
