SHELL := /bin/bash

.PHONY: help build up down logs clean security

PYTHON := python3
VENV := .venv
PY := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

# ==============================
# HELP
# ==============================
help:
	@echo "=== COMANDOS DISPONÍVEIS ==="
	@echo "make build     -> Build das imagens Docker"
	@echo "make up        -> Subir containers"
	@echo "make down      -> Parar containers"
	@echo "make logs      -> Ver logs"
	@echo "make clean     -> Limpar containers/imagens"
	@echo "make security  -> Rodar scans de segurança"

# ==============================
# DOCKER
# ==============================
build:
	docker compose -f docker-compose.yml build

up:
	docker compose -f docker-compose.yml up -d --build

dev:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build

stg:
	docker compose -f docker-compose.yml -f docker-compose.stg.yml up -d --build

down:
	docker compose down --remove-orphans

logs:
	docker compose logs -f

clean:
	docker compose down -v --rmi all --remove-orphans
	
security:
	@set -euo pipefail; \
	 echo "=== PREPARANDO AMBIENTE ==="; \
	 if [ ! -d "$(VENV)" ]; then $(PYTHON) -m venv $(VENV); fi; \
	 source "$(VENV)/bin/activate"; \
	 python -m pip install --upgrade pip >/dev/null; \
	 # Ferramentas (instaladas dentro do venv) \
	 pip install -q bandit pip-audit; \
	 # Trivy: se estiver instalado via pip no venv, este activate garante que o bin fica no PATH \
	 mkdir -p Testes_de_Vulnerabilidade/pip-audit; \
	 echo "=== PIP-AUDIT (DEPENDENCIES) ==="; \
	 mkdir -p Testes_de_Vulnerabilidade/pip-audit; \
	 REQ_FILES=$$(find . -type f -name "requirements*.txt" | sort); \
	 if [ -z "$$REQ_FILES" ]; then \
	   echo "Nenhum requirements encontrado."; \
	 else \
	   for f in $$REQ_FILES; do \
	     safe_name=$$(echo "$$f" | sed 's#^\./##' | tr '/.' '__'); \
	     echo "Auditando: $$f"; \
	     pip-audit -r "$$f" -f json -o "Testes_de_Vulnerabilidade/pip-audit/$${safe_name}.json"; \
	   done; \
	 fi;
	 @echo "=== TRIVY IMAGE SCAN ==="; \
	 trivy image --severity HIGH,CRITICAL --exit-code 1 local/webapp:test | tee Testes_de_Vulnerabilidade/trivy-webapp.txt; \
	 trivy image --severity HIGH,CRITICAL --exit-code 1 local/surf-data-service:test | tee Testes_de_Vulnerabilidade/trivy-surf-data.txt; \
	 trivy image --severity HIGH,CRITICAL --exit-code 1 local/notification-service:test | tee Testes_de_Vulnerabilidade/trivy-notification.txt; \
	 trivy image --severity HIGH,CRITICAL --exit-code 1 local/scheduler-service:test | tee Testes_de_Vulnerabilidade/trivy-scheduler.txt; \
	 @echo "=== SCANS FINALIZADOS ==="

	@echo "=== SCANS FINALIZADOS ==="


