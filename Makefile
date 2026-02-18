# SurfPulse - Makefile
# Uso: make dev-up | make dev-down | make ps | make logs | make security | make test

COMPOSE = docker compose
BASE    = -f docker-compose.yml

DEV = $(BASE) -f docker-compose.dev.yml
STG = $(BASE) -f docker-compose.stg.yml
PRD = $(BASE) -f docker-compose.prd.yml

.PHONY: help dev-up dev-down stg-up stg-down prd-up prd-down build rebuild ps logs health security test clean

help:
	@echo "Targets:"
	@echo "  dev-up/dev-down    - Sobe/derruba ambiente DEV"
	@echo "  stg-up/stg-down    - Sobe/derruba ambiente STG"
	@echo "  prd-up/prd-down    - Sobe/derruba ambiente PRD"
	@echo "  build              - Build (cache normal)"
	@echo "  rebuild            - Build sem cache"
	@echo "  ps                 - Status dos containers"
	@echo "  logs               - Logs (DEV)"
	@echo "  health             - Healthcheck rapido do gateway"
	@echo "  security           - Bandit + pip-audit (host e containers)"
	@echo "  test               - Testes (se existirem)"
	@echo "  clean              - Remove containers/volumes e imagens locais"

dev-up:
	$(COMPOSE) $(DEV) up -d --build

dev-down:
	$(COMPOSE) $(DEV) down

stg-up:
	$(COMPOSE) $(STG) up -d --build

stg-down:
	$(COMPOSE) $(STG) down

prd-up:
	$(COMPOSE) $(PRD) up -d --build

prd-down:
	$(COMPOSE) $(PRD) down

build:
	$(COMPOSE) $(DEV) build

rebuild:
	$(COMPOSE) $(DEV) build --no-cache

ps:
	$(COMPOSE) $(DEV) ps

logs:
	$(COMPOSE) $(DEV) logs -f --tail=200

health:
	@curl -sS -i http://localhost:5000/health | head -n 20

security:
	@echo "== Host (.venv) =="
	@bash -lc 'set -e; \
	if [ -d ".venv" ]; then \
		source .venv/bin/activate; \
		bandit -r services -ll; \
		pip-audit; \
	else \
		echo "No .venv found. Create with:"; \
		echo "  python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements-dev.txt"; \
		exit 1; \
	fi'
	@echo ""
	@echo "== Container Images (Trivy) =="
	@command -v trivy >/dev/null 2>&1 || { echo "Trivy não instalado. Instale com: sudo apt-get update && sudo apt-get install -y trivy"; exit 1; }
	@trivy image --severity CRITICAL,HIGH --ignore-unfixed --exit-code 1 projeto_final_devops_alisson_melo-gateway
	@trivy image --severity CRITICAL,HIGH --ignore-unfixed --exit-code 1 projeto_final_devops_alisson_melo-surf-data-service
	@trivy image --severity CRITICAL,HIGH --ignore-unfixed --exit-code 1 projeto_final_devops_alisson_melo-notification-service
	@trivy image --severity CRITICAL,HIGH --ignore-unfixed --exit-code 1 projeto_final_devops_alisson_melo-scheduler-service
	
# Testes (se você tiver pytest configurado em algum lugar)
test:
	@echo "== Tests =="
	@bash -lc 'if [ -d ".venv" ]; then source .venv/bin/activate && pytest -q || true; else echo "No .venv found. Skipping."; fi'

clean:
	$(COMPOSE) $(DEV) down -v --remove-orphans
	@echo "Removendo imagens locais do projeto (opcional)..."
	@docker image rm -f projeto_final_devops_alisson_melo-gateway 2>/dev/null || true
	@docker image rm -f projeto_final_devops_alisson_melo-surf-data-service 2>/dev/null || true
	@docker image rm -f projeto_final_devops_alisson_melo-notification-service 2>/dev/null || true
	@docker image rm -f projeto_final_devops_alisson_melo-scheduler-service 2>/dev/null || true
