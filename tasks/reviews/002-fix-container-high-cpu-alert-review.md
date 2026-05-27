---
id: "002"
issue: "tasks/issues/002-fix-container-high-cpu-alert.md"
created: 2026-05-26
updated: 2026-05-26
---

# Review: Fix ContainerHighCPU alert expression

## Related Task

- `tasks/issues/002-fix-container-high-cpu-alert.md`

## Overall Verdict

**Pass**

No Blocking findings. Two Non-blocking findings must be addressed in a follow-up task (infrastructure gap prevents live verification). One Suggestion is optional.

## Findings

| ID | Level | Requirement | Description | Evidence |
|----|-------|-------------|-------------|----------|
| F-001 | Non-blocking | SMK-001 | DoD requires `SMK-001` to pass via `docker exec prometheus promtool check rules /etc/prometheus/rules/lab-alerts.yaml`, but this invocation cannot succeed because the `rules/` directory is not mounted into the Prometheus container. An equivalent `docker run` invocation was used instead, satisfying AC-001/NFR-001 in spirit but not SMK-001's exact form. | `docker-compose.yml:647-649` — only `prometheus.yaml` is mounted; `rules/` volume is absent |
| F-002 | Non-blocking | AC-002, AC-003 | Runtime ACs requiring a live Prometheus with the rules file mounted and cAdvisor providing metrics cannot be verified. AC-002 (UI shows values 0–1) and AC-003 (0.15-CPU container at 0.1 cores → ~0.67) are mathematically implied by the correct expression but were not observed in a live environment. | `docker-compose.yml:647-649` — rules directory not mounted; implementation summary "Unresolved Assumptions" |
| F-003 | Suggestion | — | `docker-compose.yml` has an uncommitted working-tree change (adding `quality` and `lineage` profiles to `postgres-db`, lines 227-228) that is unrelated to this task. It should be committed separately or stashed to keep the changeset clean. | `git diff -- docker-compose.yml` |

## AC Evaluation

| AC | Result | Notes |
|----|--------|-------|
| AC-001 | Pass | `promtool check rules` exited 0 with "SUCCESS: 8 rules found" via `docker run --rm prom/prometheus:latest promtool check rules`; expression is syntactically valid PromQL confirmed by visual inspection |
| AC-002 | Not verified | Requires live Prometheus with rules mounted; expression is semantically correct (ratio produces 0–1 fraction). Links to F-002. |
| AC-003 | Not verified | Requires live cAdvisor metrics; mathematically: 0.1 cores / (0.15 CPU limit) ≈ 0.667, which is what the expression would produce. Links to F-002. |

## Test Coverage Evaluation

| Test Category | Status | Notes |
|---------------|--------|-------|
| Unit | Not applicable | PromQL rules have no isolatable unit-testable logic outside of `promtool`; stated in issue |
| Integration | Not applicable | Correctness verified via `promtool check rules`; stated in issue |
| Smoke (SMK-001) | Partial | Equivalent `docker run` invocation passed; exact `docker exec` invocation not possible — `rules/` not mounted in Prometheus container. Links to F-001. |
| Observability (OT-001) | Not verified | Requires live Prometheus UI with rules loaded; blocked by same infrastructure gap as F-002 |
| E2E | Not applicable | Alert firing requires sustained CPU load; stated in issue |
| Regression | Not applicable | No prior defect record; stated in issue |
| Performance | Not applicable | PromQL rule evaluation overhead negligible; stated in issue |
| Security | Not applicable | No authentication, secrets, or network exposure touched; stated in issue |
| Usability | Not applicable | No user-facing behavior; stated in issue |

## Observability Evaluation

| OBS ID | Requirement | Status | Notes |
|--------|-------------|--------|-------|
| OBS-001 | `description` annotation renders value via `| humanizePercentage` | Met | `services/prometheus/rules/lab-alerts.yaml:24` — `{{ $value | humanizePercentage }}` is present and unchanged |

## ADR Compliance

Not applicable — no ADR dependencies listed in the task.

## Convention Notes

- `F-003` — Suggestion — `docker-compose.yml` contains an unrelated uncommitted change (postgres profiles) that should be isolated in its own commit to keep this task's diff reviewable.

## Unresolved Assumptions or Follow-Up

- **Rules volume mount missing** (root cause of F-001 and F-002): `docker-compose.yml` `prometheus` service mounts only `prometheus.yaml`, not the `rules/` directory. Prometheus is therefore evaluating no alert rules in the live deployment. A follow-up task should add the volume mount:
  ```yaml
  volumes:
    - ./services/prometheus/prometheus.yaml:/etc/prometheus/prometheus.yml
    - ./services/prometheus/rules:/etc/prometheus/rules:ro   # ← missing
    - prometheus_data:/prometheus
  ```
  Once added, SMK-001 can be run as specified and AC-002/AC-003 can be verified in the Prometheus UI.
- **OT-001** (query `ALERTS{alertname="ContainerHighCPU"}` in Prometheus UI) cannot be verified until the volume mount is in place and cAdvisor is scraping.
