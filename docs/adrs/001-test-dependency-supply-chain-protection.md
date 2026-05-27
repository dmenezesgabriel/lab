# ADR 001: Test dependency supply chain protection strategy

## Status

Accepted

## Date

2026-05-27

## Context

- The test environment depends on third-party Python packages (pytest, playwright, docker SDK, pytest-bdd, httpx) installed via uv.
- Fast-publish supply chain attacks exploit the window between a package being published and the community auditing it. Attackers push a malicious version and rely on automation to install it before anyone notices.
- uv provides native flags for both hash enforcement and publication-age filtering, so no custom tooling is needed.

## Decision

Use two native uv security mechanisms:

1. `[tool.uv.pip] require-hashes = true` in `tests/pyproject.toml` — every `uv sync` enforces SHA-256 hash verification against `tests/uv.lock`, preventing tampered packages from installing silently.
2. `uv lock --exclude-newer <date>` — when regenerating the lockfile, pass a cutoff date 7 days in the past so uv refuses to resolve any package version published within that window. Exposed as `make lock-tests`.

## Options Considered

1. Native uv `--exclude-newer` + `require-hashes`. `(recommended)`
2. `uv lock` with hashes only — no publication-age restriction.
3. Custom Python script querying the PyPI JSON API for each package's `upload_time`.

Option 1 is chosen because both protections are flags on the existing uv toolchain — zero extra scripts, zero extra dependencies, and the error messages are native uv output. Option 2 alone protects against version tampering but not against a freshly published malicious version. Option 3 provides the same age-check logic as Option 1 but requires a maintained script, external HTTP calls in a separate step, and re-implements logic uv already has.

## Consequences

Positive:
- Hash verification: any tampered file at install time causes `uv sync --frozen` to abort with a clear mismatch error.
- Age gate: `make lock-tests` natively refuses to pin any package version published within 7 days.
- No custom tooling: the protection is entirely in uv flags and `pyproject.toml` config.

Negative:
- Updating a dependency to a version released within the last 7 days requires waiting before running `make lock-tests`.
- `--exclude-newer` accepts an absolute datetime, so the Makefile must compute "7 days ago" at invocation time (`$(shell date -u -d '7 days ago' +%Y-%m-%dT%H:%M:%SZ)`).
- Hash-only installs require the lockfile to be regenerated whenever any dependency changes — no ad-hoc `uv add` without re-locking.

## Validation

- `AC-001` and `AC-002` in Task 001 verify the `make lock-tests` target enforces the age window in practice.
- `AC-004` in Task 001 verifies `uv sync --frozen` installs with hash verification.
- `NFR-003` in Task 001 requires `tests/uv.lock` to be committed and diffable in git.

## Open Questions

None — decision is fully resolved.
