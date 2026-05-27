---
id: "001"
issue: "tasks/issues/001-test-infrastructure-bootstrap.md"
created: 2026-05-27
updated: 2026-05-27
---

# Review: Bootstrap test infrastructure with uv security hardening and test runner container

## Related Task

- `tasks/issues/001-test-infrastructure-bootstrap.md`

## Overall Verdict

**Fail**

Blocked by F-001, F-002, F-003. Three required test categories defined in the issue are entirely absent from the codebase. Implementer must resolve all Blocking findings before mark-complete.

## Findings

| ID | Level | Requirement | Description | Evidence |
|----|-------|-------------|-------------|----------|
| F-001 | Blocking | IT-001 | Integration test IT-001 (lab-net hostname resolution) is entirely absent. The issue defines it as a pytest-bdd scenario covering FR-006 and AC-003. The implementation summary defers it to task 002, but the issue includes it in this task's Required Tests. | No file under `tests/` matches; `tests/` contains only `Dockerfile`, `pyproject.toml`, `uv.lock` |
| F-002 | Blocking | SMK-001 | Smoke test SMK-001 (test-runner image builds cleanly) is entirely absent as a codified or automated test. The issue defines it as a required smoke test covering FR-005 and AC-005. | No test script or CI artifact for this test exists in the codebase |
| F-003 | Blocking | ST-001 | Security test ST-001 (no secret env vars beyond DOCKER_HOST) is entirely absent. The issue defines it as a required security test covering NFR-002. | No test, script, or automated check exists in the codebase |
| F-004 | Non-blocking | NFR-003 | `tests/uv.lock`, `tests/pyproject.toml`, and `tests/Dockerfile` are untracked files in the working tree — not committed to git. NFR-003 requires `tests/uv.lock` to be committed. The Definition of Done requires all four test infrastructure files committed. `compose/tests.yml` is already committed. | `git ls-files --others --exclude-standard tests/` lists all three files |
| F-005 | Suggestion | — | The Dockerfile copies uv from `ghcr.io/astral-sh/uv:latest` without pinning to a specific version or digest. This introduces minor non-determinism in the build tool itself. Pinning to a specific release tag (e.g., `ghcr.io/astral-sh/uv:0.7.0`) matches the same supply-chain discipline applied to Python dependencies. | `tests/Dockerfile:3` |

## AC Evaluation

| AC | Result | Notes |
|----|--------|-------|
| AC-001 | Pass | `make lock-tests` uses `--exclude-newer $(shell date -u -d '7 days ago' +%Y-%m-%dT%H:%M:%SZ)` (`Makefile:81`). `tests/uv.lock` contains `exclude-newer = "2026-05-20T16:35:49Z"` and 253 SHA-256 hashes. |
| AC-002 | Pass | The `--exclude-newer` flag is correctly passed to `uv lock` in the `lock-tests` target (`Makefile:81`). uv natively exits non-zero when a resolved package version falls within the exclusion window; no additional tooling is required. Behavior is enforced by the flag, not custom logic. |
| AC-003 | Pass | `compose/tests.yml` attaches `test-runner` to `lab-net` (external). `make test-integration MARKS=storage` resolves to `PYTEST_MARKS=-m storage` and runs `docker compose -f compose/tests.yml run --rm test-runner pytest -m storage integration/`. Network reachability to `postgres-db` and `minio` follows from `lab-net` attachment. (`compose/tests.yml:10-15`, `Makefile:83-84`) |
| AC-004 | Pass | `tests/Dockerfile:7` runs `uv sync --frozen`. `tests/pyproject.toml:17-18` sets `[tool.uv.pip] require-hashes = true`. Together these enforce hash-verified installation of exactly the locked versions. |
| AC-005 | Pass | `tests/Dockerfile:9` sets `PATH="/opt/test-env/.venv/bin:$PATH"` and `tests/Dockerfile:11` runs `playwright install --with-deps chromium` using that venv's playwright binary. Playwright is installable; Chromium is installed at build time. |

## Test Coverage Evaluation

| Test Category | Status | Notes |
|---------------|--------|-------|
| Unit | Not applicable | Issue states: not applicable — infrastructure files and Makefile targets with no application logic. |
| Integration (IT-001) | Missing | IT-001 scenario is absent. No file under `tests/` implements the lab-net hostname resolution check. Implementation summary defers to task 002, but the issue requires it here. → F-001 |
| Smoke (SMK-001) | Missing | SMK-001 (image builds cleanly) is absent. No CI step, script, or automated check exists for this test. → F-002 |
| E2E | Not applicable | Issue states: not applicable — infrastructure task, not a user journey. |
| Regression | Not applicable | Issue states: not applicable — no prior defect to guard against. |
| Performance | Not applicable | Issue states: not applicable — build time bounded by NFR-001, no throughput requirement. |
| Security (ST-001) | Missing | ST-001 (no secret env vars in container) is absent. No verification script or automated check exists. → F-003 |
| Usability | Not applicable | Issue states: not applicable — no user-facing UI or CLI output. |
| Observability | Not applicable | Issue states: not applicable — no operational telemetry introduced. |

## Observability Evaluation

| OBS ID | Requirement | Status | Notes |
|--------|-------------|--------|-------|
| OBS-001 | When `make lock-tests` is blocked by the age check, uv's native error message names the offending package and version | Met | The `--exclude-newer` flag in `Makefile:81` delegates error reporting entirely to uv's native output. No extra logging is needed or present. |
| OBS-002 | Test run output uses pytest default stdout; CI captures it with standard log collection | Met | `make test-integration` and `make test-e2e` invoke pytest directly with no `--reporter` or custom plugin flags (`Makefile:83-87`). |

## ADR Compliance

Not applicable — no ADR dependencies listed in the task.

## Convention Notes

- `F-005` — Suggestion — `tests/Dockerfile:3` copies uv from `ghcr.io/astral-sh/uv:latest`. Using `latest` for the build tool is inconsistent with the supply-chain hardening philosophy applied to the Python dependencies (pinned versions + SHA-256 hashes). Not required by any named FR/NFR.

## Unresolved Assumptions or Follow-Up

- `NFR-001` (build time under 60 seconds on warm Docker cache) cannot be verified without running `docker build -f tests/Dockerfile tests/`. This was acknowledged in the implementation summary and remains unresolved pending a live build.
- `IT-001` is explicitly deferred to task 002 in the implementation summary. If the intent is to keep IT-001 in this task's contract, it must be implemented before mark-complete. If the intent is to descope it to task 002, the issue file should be updated to remove IT-001 from this task's Required Tests and move it to `tasks/issues/002-integration-tests-service-health.md`.
- `SMK-001` and `ST-001` are described in the implementation summary as post-merge verifications. If these are accepted as manual checks (not automated test files), the issue should clarify their verification method to avoid blocking future reviews. As written, the Required Tests section implies codified tests.
- `tests/uv.lock` `exclude-newer` timestamp is `2026-05-20T16:35:49Z` (7 days before 2026-05-27). On the next `make lock-tests` run the cutoff will advance, which is the expected behavior. No action needed.
