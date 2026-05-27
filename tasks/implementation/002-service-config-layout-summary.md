---
id: 002
issue: user-request
created: 2026-05-27
updated: 2026-05-27
---

# Service Config Layout Summary

## Task Implemented

Moved service-owned configuration out of root `config/` into `services/`, moved root Dockerfiles into their owning service directories, restarted the full Compose stack, and validated service health and browser UIs.

## Files Changed

- `docker-compose.yml` updated to reference `services/<service>/...` config paths and `services/<service>/Dockerfile` build files.
- `services/airflow/`, `services/jupyter/`, and `services/mlflow/` now contain their Dockerfile-specific files.
- `services/*` now contains service-owned runtime config formerly under `config/*`.
- `scripts/generate_oidc_key.sh` now writes OIDC keys under `services/authelia/secrets`.
- `scripts/setup_portainer_oauth.sh` comment updated for the new Authelia config path.
- `docker-compose.yml` Marquez memory limit increased from `256M` to `512M` after full-stack startup exposed an OOM kill.

## Behavior Implemented

- Root `config/` tree was removed after moving its files to `services/`.
- Compose builds still use the repository root as build context, with Dockerfiles living in the relevant service directories.
- Runtime mounts now use service-local config paths.
- Full profile stack starts with all services healthy or running as expected.

## Design Notes

- Kept root build context unchanged to avoid broad Dockerfile COPY rewrites.
- Kept container-internal `/config` paths for Authelia because those are part of the image contract, not host layout.
- Used Docker root to `chown` the old root-owned Homepage log path because interactive `sudo` was unavailable.

## Tests Added Or Updated

- No automated tests were added; this was a Compose/layout refactor validated through configuration checks, builds, container health checks, HTTP smoke tests, logs, and browser navigation.

## Validations Run

- `docker compose --profile "*" down`
- `docker compose --profile "*" config --quiet`
- `jq empty services/grafana/dashboards/*.json`
- `yamllint -d relaxed docker-compose.yml services/**/*.yml services/**/*.yaml` via Docker, with line-length warnings only.
- `docker compose --profile "*" up -d --build`
- `docker compose --profile "*" ps`
- HTTP smoke checks for Homepage, Jupyter, MLflow, MinIO, Prometheus, Loki, Tempo, cAdvisor, llama.cpp, and SonarQube.
- Internal health checks for Airflow and Marquez.
- Recent logs inspected for key services.
- Playwright UI navigation for Homepage, MLflow, JupyterLab, Prometheus, MinIO Console, and SonarQube.

## ADRs Updated

- None.

## Observability Added Or Changed

- No new observability behavior added.

## Skipped Or Not Applicable Test Categories

- Unit and integration tests were not applicable because no application logic changed.
- Accessibility-specific tests were not applicable because no UI code changed.

## Unresolved Assumptions Or Follow-Up Work

- JupyterLab loads but reports existing frontend extension version warnings and one FAST design token parse error.
- MinIO Console unauthenticated load reports an expected `403` for `/api/v1/session` before login.
- Direct HTTP access to Caddy HTTPS routes such as `http://localhost:3001/` returns the expected `Client sent an HTTP request to an HTTPS server`; Playwright could not continue through the local HTTPS certificate authority without a custom browser context.
