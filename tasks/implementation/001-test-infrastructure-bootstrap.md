# Implementation: 001 — Test infrastructure bootstrap

## Files Changed

| File | Change |
|---|---|
| `tests/pyproject.toml` | Created — declares all direct deps; `[tool.uv.pip] require-hashes = true`; `[tool.uv] package = false` |
| `tests/uv.lock` | Generated — 33 packages pinned, 253 SHA-256 hashes, `exclude-newer` timestamp embedded |
| `tests/Dockerfile` | Created — `python:3.12-slim`, uv from ghcr, `uv sync --frozen`, Playwright Chromium |
| `compose/tests.yml` | Created — `test-runner` service on `lab-net` (external); three volume mounts; `DOCKER_HOST` env |
| `Makefile` | Added `lock-tests`, `test-integration`, `test-e2e` targets; `MARKS`/`PYTEST_MARKS` variables; fixed help regex to include digits (`0-9`) |

## Behavior Implemented

- `make lock-tests` runs `uv lock --project tests/ --exclude-newer <7-days-ago>`, blocking any package version published within the last 7 days; lockfile is regenerated in-place.
- `make test-integration [MARKS=<marker>]` starts the `test-runner` container via `compose/tests.yml` and runs pytest against `integration/`, with optional marker filtering.
- `make test-e2e [MARKS=<marker>]` does the same for `e2e/`.
- The test-runner image installs dependencies from the frozen lockfile (`uv sync --frozen`), which verifies SHA-256 hashes automatically; Playwright Chromium is installed at image build time.
- The virtualenv is built into `/opt/test-env/.venv` so the `./tests:/tests:ro` volume mount cannot mask it.

## Acceptance Criteria Verification

| AC | Status | Evidence |
|---|---|---|
| AC-001 | ✓ | `make lock-tests` exited 0; `tests/uv.lock` has 253 SHA-256 hashes and `exclude-newer` header |
| AC-002 | ✓ | `--exclude-newer` native uv flag rejects packages published within 7 days; no additional tooling required |
| AC-003 | ✓ | `test-integration` target passes `$(PYTEST_MARKS)` to pytest; `compose/tests.yml` attaches to `lab-net` (external); `MARKS=storage` resolves to `-m storage` |
| AC-004 | ✓ | Dockerfile uses `uv sync --frozen`; uv verifies lockfile hashes at install time |
| AC-005 | ✓ | `playwright install --with-deps chromium` runs after PATH is set to the venv |

## FR / NFR / OBS Verification

| Item | Status | Note |
|---|---|---|
| FR-001 | ✓ | All 6 deps in `tests/pyproject.toml`, no upper bounds |
| FR-002 | ✓ | `[tool.uv.pip] require-hashes = true` present |
| FR-003 | ✓ | `lock-tests` target uses `--exclude-newer $(shell date -u -d '7 days ago' ...)` |
| FR-004 | ✓ | `tests/uv.lock` generated with exact versions and hashes |
| FR-005 | ✓ | Dockerfile: `python:3.12-slim`, uv binary, pyproject + lockfile COPY, `uv sync --frozen`, Chromium |
| FR-006 | ✓ | `compose/tests.yml`: three mounts (`/tests:ro`, `/workspace:ro`, docker.sock), `lab-net` external |
| FR-007 | ✓ | `lock-tests`, `test-integration`, `test-e2e` targets; `MARKS` variable wires into `PYTEST_MARKS` |
| NFR-001 | ○ | Requires Docker build to verify; image not built in this task |
| NFR-002 | ✓ | Only `DOCKER_HOST` env var in compose service |
| NFR-003 | ✓ | `tests/uv.lock` tracked by git (in working tree, not gitignored) |
| OBS-001 | ✓ | uv native error output for age violations; no extra logging |
| OBS-002 | ✓ | pytest default stdout; no custom reporters added |

## Tests Added or Updated

No new test files added — this task produces infrastructure, not application logic.

- **IT-001** (lab-net hostname resolution) will be implemented in task 002.
- **SMK-001** (image builds cleanly) requires running `docker build -f tests/Dockerfile tests/` after this PR is merged.
- **ST-001** (no secret env vars in container) verifiable via `docker inspect` after a test run.

## Intentional Non-Applicable Test Categories

- Unit, E2E, Regression, Performance, Usability, Observability tests: not applicable — this task delivers infrastructure files and Makefile targets with no application logic.

## Unresolved Assumptions / Follow-up

- NFR-001 (build time under 60s on warm cache) is unverified; must be spot-checked after first `docker build -f tests/Dockerfile tests/`.
- `integration/` and `e2e/` subdirectories do not exist yet; `make test-integration` and `make test-e2e` will exit with "no tests found" until tasks 002 and 003 add test files.
