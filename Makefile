.PHONY: up down tear-down build logs help \
        up-storage up-modeling up-airflow up-observability up-management up-sso up-llm up-quality \
        setup-hosts generate-oidc-key setup-sso \
        lock-tests test-integration test-e2e test-smoke test-security

UID        := $(shell id -u)
GID        := $(shell id -g)
DOCKER_GID := $(shell stat -c '%g' /var/run/docker.sock)
COMPOSE    := UID=$(UID) GID=$(GID) DOCKER_GID=$(DOCKER_GID) docker compose

MARKS       ?=
PYTEST_MARKS = $(if $(MARKS),-m $(MARKS),)

# ─── All services ─────────────────────────────────────────────────────────────

up: setup-hosts generate-oidc-key ## Start every service (all profiles)
	$(COMPOSE) --profile '*' up -d

down: ## Stop all running services
	$(COMPOSE) --profile '*' down

tear-down: ## Stop all services and delete volumes
	$(COMPOSE) --profile '*' down -v

build: ## Rebuild all custom images
	$(COMPOSE) --profile '*' build

logs: ## Follow logs for all services
	$(COMPOSE) --profile '*' logs -f

# ─── Stack targets ────────────────────────────────────────────────────────────

up-storage: ## Postgres + MinIO
	$(COMPOSE) --profile model-registry up -d

up-modeling: setup-hosts ## MLflow + storage
	$(COMPOSE) --profile model-registry up -d

up-airflow: setup-hosts generate-oidc-key ## Airflow webserver + scheduler (includes storage)
	$(COMPOSE) --profile airflow up -d

up-observability: ## Prometheus + Grafana + Loki + extras
	$(COMPOSE) --profile observability --profile observability-extras up -d

up-management: setup-hosts generate-oidc-key ## Homepage + Portainer + Adminer (includes SSO)
	$(COMPOSE) --profile sso --profile management --profile management-extras up -d

up-sso: setup-hosts generate-oidc-key ## Authelia + Caddy only
	$(COMPOSE) --profile sso up -d

up-quality: ## SonarQube (includes storage)
	$(COMPOSE) --profile quality up -d

up-llm: ## llama.cpp inference server
	$(COMPOSE) --profile llm up -d

# ─── Per-service helpers ──────────────────────────────────────────────────────

restart-%: ## Restart a service: make restart-grafana
	$(COMPOSE) restart $*

logs-%: ## Tail logs for a service: make logs-airflow-scheduler
	$(COMPOSE) logs -f $*

# ─── Setup ────────────────────────────────────────────────────────────────────

setup-hosts: ## Add *.app.localhost → 127.0.0.1 to /etc/hosts
	@bash scripts/setup_hosts.sh

generate-oidc-key: ## Generate Authelia OIDC RSA key (idempotent)
	@bash scripts/generate_oidc_key.sh

setup-sso: generate-oidc-key ## Generate OIDC key and start SSO stack
	$(COMPOSE) build airflow-webserver
	$(COMPOSE) --profile sso --profile management --profile management-extras up -d
	@printf '\nSSO ready:\n  Auth:      https://auth.app.localhost\n  Airflow:   https://airflow.app.localhost\n  Grafana:   https://grafana.app.localhost\n  Portainer: https://portainer.app.localhost\n  Homepage:  https://home.app.localhost\n'

# ─── Tests ───────────────────────────────────────────────────────────────────

lock-tests: ## Regenerate tests/uv.lock enforcing 7-day supply-chain age gate
	uv lock --project tests/ --exclude-newer $(shell date -u -d '7 days ago' +%Y-%m-%dT%H:%M:%SZ)

test-integration: ## Run integration tests in container; MARKS=<marker> to filter
	$(COMPOSE) -f compose/tests.yml run --rm test-runner pytest $(PYTEST_MARKS) integration/

test-e2e: ## Run end-to-end tests in container; MARKS=<marker> to filter
	$(COMPOSE) -f compose/tests.yml run --rm test-runner pytest $(PYTEST_MARKS) e2e/

test-smoke: ## Run smoke tests in container (builds test-runner image, checks playwright)
	$(COMPOSE) -f compose/tests.yml run --rm test-runner pytest smoke/

test-security: ## Run security tests in container (checks no secret env vars)
	$(COMPOSE) -f compose/tests.yml run --rm test-runner pytest security/

# ─── Help ─────────────────────────────────────────────────────────────────────

help: ## Show available targets
	@grep -E '^[a-zA-Z0-9_%/-]+:.*##' $(MAKEFILE_LIST) \
	  | awk 'BEGIN {FS = ":.*##"}; {printf "  \033[36m%-26s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help
