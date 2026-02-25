.PHONY: help build up down logs clean security

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
	docker compose build

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f

clean:
	docker compose down -v --rmi all --remove-orphans

security:
	@echo "=== A CRIAR PASTA DE RELATÓRIOS ==="
	mkdir -p Testes_de_Vulnerabilidade

	@echo "=== BANDIT (CODE SECURITY) ==="
	bandit -r services -ll -f txt -o Testes_de_Vulnerabilidade/bandit-result.txt

	@echo "=== PIP AUDIT (DEPENDENCIES) ==="
	pip-audit -r requirements.txt -f json -o Testes_de_Vulnerabilidade/pip-audit-report.json
	pip-audit -r requirements.txt 2>&1 | tee Testes_de_Vulnerabilidade/pip-audit-result.txt >/dev/null
	pip-audit -r services/webapp/requirements-lock.txt 2>&1 | tee -a Testes_de_Vulnerabilidade/pip-audit-result.txt >/dev/null

	@echo "=== TRIVY IMAGE SCAN ==="
	trivy image --severity HIGH,CRITICAL --exit-code 1 local/webapp:test | tee Testes_de_Vulnerabilidade/trivy-webapp.txt
	trivy image --severity HIGH,CRITICAL --exit-code 1 local/surf-data-service:test | tee Testes_de_Vulnerabilidade/trivy-surf-data.txt
	trivy image --severity HIGH,CRITICAL --exit-code 1 local/notification-service:test | tee Testes_de_Vulnerabilidade/trivy-notification.txt
	trivy image --severity HIGH,CRITICAL --exit-code 1 local/scheduler-service:test | tee Testes_de_Vulnerabilidade/trivy-scheduler.txt

	@echo "=== SCANS FINALIZADOS ==="


