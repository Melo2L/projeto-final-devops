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

# ==============================
# SECURITY SCANS
# ==============================
security:
	@echo "=== A CRIAR PASTA DE RELATÓRIOS ==="
	mkdir -p Testes_de_Vulnerabilidade

	@echo "=== BANDIT (CODE SECURITY) ==="
	bandit -r services -ll -f txt -o Testes_de_Vulnerabilidade/bandit-result.txt

	@echo "=== PIP AUDIT (DEPENDENCIES) ==="
	@echo "Security policy: ignore only protobuf GHSA-7gcm-g887-7qv7 (documented exception)" > Testes_de_Vulnerabilidade/pip-audit-result.txt
	@echo "Command: pip-audit -r requirements.txt --ignore-vuln GHSA-7gcm-g887-7qv7" >> Testes_de_Vulnerabilidade/pip-audit-result.txt
	@echo "----" >> Testes_de_Vulnerabilidade/pip-audit-result.txt
	pip-audit -r requirements.txt --ignore-vuln GHSA-7gcm-g887-7qv7 >> Testes_de_Vulnerabilidade/pip-audit-result.txt



	@echo "=== TRIVY IMAGE SCAN ==="
	trivy image --severity CRITICAL,HIGH --ignore-unfixed --exit-code 1 projeto_final_devops_alisson_melo-gateway \
	| tee Testes_de_Vulnerabilidade/trivy-gateway.txt

	trivy image --severity CRITICAL,HIGH --ignore-unfixed --exit-code 1 projeto_final_devops_alisson_melo-surf-data-service \
	| tee Testes_de_Vulnerabilidade/trivy-surf-data.txt

	trivy image --severity CRITICAL,HIGH --ignore-unfixed --exit-code 1 projeto_final_devops_alisson_melo-notification-service \
	| tee Testes_de_Vulnerabilidade/trivy-notification.txt

	trivy image --severity CRITICAL,HIGH --ignore-unfixed --exit-code 1 projeto_final_devops_alisson_melo-scheduler-service \
	| tee Testes_de_Vulnerabilidade/trivy-scheduler.txt

	@echo "=== SCANS FINALIZADOS ==="

