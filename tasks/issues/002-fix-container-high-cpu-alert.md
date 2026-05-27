---
id: "002"
created: 2026-05-26
updated: 2026-05-26
status: active
---

# Task: Fix ContainerHighCPU alert expression unit mismatch

## Priority

P0 — The alert as written never fires for any container with `cpus ≤ 0.85` (all containers in this stack) and fires incorrectly for containers without a CPU limit. The monitoring rule is silently broken.

## Dependencies

- No task dependency; can start independently.
- No ADR dependency; this task uses existing architecture.

## Assignability

**AFK** — the correct PromQL is deterministic; no architectural decision is required.

## Context

`services/prometheus/rules/lab-alerts.yaml:7-12` contains:

```yaml
expr: |
  sum by (name) (
    rate(container_cpu_usage_seconds_total{image!=""}[2m])
  ) > 0.85
```

`rate(container_cpu_usage_seconds_total[2m])` returns CPU **cores consumed** (seconds per second). The literal `0.85` is therefore 0.85 CPU cores, not 85% of a container's limit. Every container in this stack is capped at ≤ 2 CPUs, so the expression _can_ fire, but it fires at 0.85 cores used — regardless of whether that is 85% or 6% of the allocated limit. A `micro` container (0.15 CPU) can never reach 0.85 cores, so the alert is permanently dark for all small services.

The correct expression divides observed CPU usage by the per-container CPU quota to produce a 0–1 fraction comparable to 0.85 (85% of limit).

cAdvisor exposes:
- `container_spec_cpu_quota` — CFS quota in microseconds per period
- `container_spec_cpu_period` — CFS period in microseconds
- CPU limit in cores = `quota / period`

## Use Cases

- **Feature**: Container resource alerts
- **Scenario**: Operator is alerted when a container is CPU-throttled
- **Given** `cadvisor` is running and a container is consuming 90% of its CPU limit for 5 minutes
- **When** Prometheus evaluates the `ContainerHighCPU` rule
- **Then** an alert fires with the container name and usage percentage

## Definition of Ready

- Prometheus is running at `localhost:9090` with the rules file mounted.
- cAdvisor is running and `container_spec_cpu_quota`, `container_spec_cpu_period`, and `container_cpu_usage_seconds_total` are present in the Prometheus scrape.

## Functional Requirements

- `FR-001`: The alert must fire when a container's CPU usage exceeds 85% of its configured CPU limit for 5 minutes.
- `FR-002`: The alert must not fire for containers with no CPU limit set (`container_spec_cpu_quota == -1` or `0`).
- `FR-003`: The alert must include the container `name` label in its output.

## Non-Functional Requirements

- `NFR-001`: The updated expression must be valid PromQL — `promtool check rules` must exit 0.
- `NFR-002`: The alert threshold and `for: 5m` guard remain unchanged.

## Observability Requirements

- `OBS-001`: The alert annotation `description` must render the value as a human-readable percentage via `| humanizePercentage`.

## Acceptance Criteria

- `AC-001`: **Given** the updated rules file is loaded, **When** `promtool check rules services/prometheus/rules/lab-alerts.yaml` runs, **Then** it exits 0 with no errors.
- `AC-002`: **Given** cAdvisor metrics are available, **When** the expression is evaluated in Prometheus UI, **Then** results are values between 0 and 1 (not raw core counts).
- `AC-003`: **Given** a container with `cpus: 0.15` using 0.1 cores (67% of limit), **When** the expression is evaluated, **Then** the result is approximately `0.67`, not `0.1`.

## Required Tests

### Unit Tests

Not applicable — PromQL rules have no isolatable unit-testable logic outside of `promtool`.

### Integration Tests

Not applicable — correctness is verified via `promtool check rules` and Prometheus query UI inspection.

### Smoke Tests

- `SMK-001`: **Scenario**: Rules file passes promtool validation
  **Given** `promtool` is available (ships inside the Prometheus container)
  **When** `docker exec prometheus promtool check rules /etc/prometheus/rules/lab-alerts.yaml` runs
  **Then** it exits 0 with output `SUCCESS`
  Covers `AC-001`, `NFR-001`.

### End-to-End Tests

Not applicable — alert firing requires sustained CPU load; a functional correctness check via `promtool` and a manual Prometheus query UI inspection covers the scope.

### Regression Tests

Not applicable — no prior defect record.

### Performance Tests

Not applicable — PromQL rule evaluation overhead is negligible.

### Security Tests

Not applicable — this task does not touch authentication, secrets, or network exposure.

### Usability Tests

Not applicable — no user-facing behavior.

### Observability Tests

- `OT-001`: After loading the updated rules, query `ALERTS{alertname="ContainerHighCPU"}` in the Prometheus UI and verify that any firing result value is between 0 and 1. Covers `AC-002`, `OBS-001`.

## Definition of Done

- `services/prometheus/rules/lab-alerts.yaml` `ContainerHighCPU` expression divides CPU usage rate by `container_spec_cpu_quota / container_spec_cpu_period`.
- Containers with no CPU limit (`quota <= 0`) are excluded with a filter.
- `promtool check rules` exits 0.
- `SMK-001` passes.
