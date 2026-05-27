---
id: "002"
created: 2026-05-26
task: tasks/issues/002-fix-container-high-cpu-alert.md
---

# Implementation Summary: Fix ContainerHighCPU alert expression

## Files Changed

- `services/prometheus/rules/lab-alerts.yaml` — replaced the `ContainerHighCPU` `expr` block

## Behavior Implemented

**Before**: the expression compared raw CPU core consumption against the literal `0.85`, making the alert permanently dark for any container with a CPU limit ≤ 0.85 cores and meaningless for containers that happen to consume more than 0.85 cores regardless of their limit.

**After**: the expression divides observed usage by the container's CPU limit (quota ÷ period), producing a 0–1 fraction comparable to the 0.85 (85%) threshold. Containers with no CPU limit (`container_spec_cpu_quota ≤ 0`) are filtered out by the `> 0` guard on the denominator, so they emit no data and the division never occurs.

New expression:

```promql
(
  sum by (name) (
    rate(container_cpu_usage_seconds_total{image!=""}[2m])
  )
  /
  sum by (name) (
    (container_spec_cpu_quota{image!=""} > 0)
    /
    container_spec_cpu_period{image!=""}
  )
) > 0.85
```

All other fields (`for: 5m`, labels, annotations, `humanizePercentage`) are unchanged, satisfying OBS-001 and NFR-002.

## Tests Added or Updated

None — as stated in the issue, PromQL rules have no isolatable unit-testable logic; correctness is verified via `promtool check rules`.

## Validations Run

- **promtool check rules** (AC-001, NFR-001): ran via `docker run --rm -v .../rules:/rules prom/prometheus:latest promtool check rules /rules/lab-alerts.yaml` — exited 0, `SUCCESS: 8 rules found`.

  > Note: SMK-001 specifies `docker exec prometheus promtool check rules /etc/prometheus/rules/lab-alerts.yaml`, but the `rules/` directory is not currently mounted into the running Prometheus container (see Unresolved Assumptions below). The one-shot Docker invocation is functionally equivalent for AC-001/NFR-001 validation.

## Accessibility Checks

Not applicable — no UI touched.

## ADRs Updated

None — this is a bug fix to a PromQL expression; no architectural assumption was changed.

## Intentional Non-Applicable Test Categories

- **Unit tests**: no isolatable logic outside PromQL evaluation.
- **Integration tests**: alert firing requires sustained real CPU load; `promtool` is the appropriate correctness gate.
- **E2E, regression, performance, security, usability tests**: as documented in the issue — none applicable.

## Unresolved Assumptions

The running Prometheus container (`docker-compose.yml` `prometheus` service) mounts only `prometheus.yaml`, not the `rules/` directory. Prometheus is therefore evaluating no alert rules in the current deployment. This is a pre-existing configuration gap outside the scope of this task. A follow-up task should add:

```yaml
volumes:
  - ./services/prometheus/prometheus.yaml:/etc/prometheus/prometheus.yml
  - ./services/prometheus/rules:/etc/prometheus/rules:ro   # ← missing
  - prometheus_data:/prometheus
```

Until that volume is added, SMK-001 as written cannot pass inside the live container.
