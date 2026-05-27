.PHONY: up down tear-down up-llm up-adminer up-airflow up-lineage build-lambdas tf-apply

UID := $(shell id -u)
GID := $(shell id -g)
DOCKER_GID := $(shell stat -c '%g' /var/run/docker.sock)
DOCKER_ENV := UID=$(UID) GID=$(GID) DOCKER_GID=$(DOCKER_GID)
COMPOSE := $(DOCKER_ENV) docker compose
COMPOSE_ALL := $(COMPOSE) --profile "*"
PROFILES_CORE := --profile modeling --profile model-registry
PROFILES_ORCHESTRATION := --profile airflow
PROFILES_MANAGEMENT := --profile management
PROFILES_MANAGEMENT_EXTRAS := --profile management-extras
PROFILES_OBSERVABILITY := --profile observability
PROFILES_OBSERVABILITY_EXTRAS := --profile observability-extras
PROFILES_SECURITY := --profile sso
PROFILES_QUALITY := --profile quality

PROFILES_GIVE_ME_SOME_CREDIT := \
	$(PROFILES_CORE) \
	$(PROFILES_ORCHESTRATION) \
	$(PROFILES_MANAGEMENT) \
	$(PROFILES_MANAGEMENT_EXTRAS) \
	$(PROFILES_OBSERVABILITY) \
	$(PROFILES_OBSERVABILITY_EXTRAS) \
	$(PROFILES_SECURITY) \
	$(PROFILES_QUALITY)

PROFILES_NYC_TAXI_TRIP := \
	$(PROFILES_CORE) \
	$(PROFILES_MANAGEMENT) \
	$(PROFILES_OBSERVABILITY) \
	$(PROFILES_SECURITY)

setup-hosts: ## Ensure *.app.localhost resolves to 127.0.0.1
	@bash scripts/setup_hosts.sh

up-give-me-some-credit: generate-oidc-key setup-hosts
	$(COMPOSE) $(PROFILES_GIVE_ME_SOME_CREDIT) up -d

up-nyc-taxi-trip: generate-oidc-key setup-hosts
	$(COMPOSE) $(PROFILES_NYC_TAXI_TRIP) up -d

down:
	$(COMPOSE_ALL) down

tear-down:
	$(COMPOSE_ALL) down -v

up-%:
	$(COMPOSE) up -d $(*)

down-%:
	$(COMPOSE) down $(*)

generate-oidc-key: ## Generate RSA key for Authelia OIDC (run once)
	@bash scripts/generate_oidc_key.sh

setup-sso: generate-oidc-key ## Full SSO setup: generate key + start services
	$(COMPOSE) build airflow-webserver
	$(COMPOSE) up -d authelia caddy portainer portainer-init airflow-webserver grafana homepage
	@echo ""
	@echo "SSO setup complete! Access URLs:"
	@echo "  Auth:      https://auth.app.localhost"
	@echo "  Grafana:   https://grafana.app.localhost"
	@echo "  Airflow:   https://airflow.app.localhost"
	@echo "  Portainer: https://portainer.app.localhost"
	@echo "  Homepage:  https://home.app.localhost"

build-lambdas: ## Install Lambda deps into .build/<name>/ (run before terraform apply)
	cd app/nyc_taxi_trip && uv run scripts/build_lambdas.py

tf-apply: ## Plan and apply Terraform for nyc_taxi_trip (requires build-lambdas first)
	cd app/nyc_taxi_trip/terraform && \
	  terraform init -upgrade -input=false && \
	  terraform apply -var="aws_endpoint=http://localhost:9002" -auto-approve
