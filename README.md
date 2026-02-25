# Projeto Final DevOps Engineer

**Alisson Melo**

**Repositório GitHub:** https://github.com/Melo2L/projeto-final-devops (Privado)

------------------------------------------------------------------------

## Introdução

Este projeto consiste no desenvolvimento da plataforma **SurfPulse**, uma aplicação web baseada em microserviços Python, integrada a uma arquitetura DevOps completa.

A aplicação foi containerizada com Docker e automatizada através de um pipeline CI/CD com GitHub Actions, permitindo:

- Build automatizado
- Testes automatizados
- Análise de segurança (DevSecOps)
- Scan de imagens
- Deploy progressivo entre ambientes

Além da funcionalidade da aplicação, o foco principal foi demonstrar a implementação prática de:

- Microserviços
- Docker Compose
- CI/CD
- DevSecOps
- Observabilidade
- Gestão de ambientes (DEV, STG, PRD)

------------------------------------------------------------------------

## Objetivo da Aplicação

Esta aplicação tem como objetivo fornecer previsões meteorológicas
relevantes para atividades relacionadas com o surf, como vento, ondas e
temperatura, através da integração com uma API externa.

Os utilizadores podem consultar estas informações para apoiar decisões
operacionais ou desportivas. Paralelamente, o projeto demonstra a
implementação prática de um ambiente DevOps completo com microserviços,
CI/CD automatizado e monitorização.

------------------------------------------------------------------------

## HLD -- High Level Design


<p align="center">
  <img src="/20260225-HLD-ProjetoFinal-DevOps.drawio.png" width="1000"/>
</p>

Este  HLD apresenta a arquitetura geral da plataforma SurfPulse baseada em microsserviços conteinerizados, evidenciando a separação entre webapp, serviços internos de dados, notificações e agendamento. O acesso do utilizador ocorre através de um ponto de entrada público, que encaminha requisições para o webapp-service, responsável pela orquestração das chamadas internas e integração com a API externa Open-Meteo.

Fluxo Geral:

User  
→ Internet  
→ Docker Port Publishing (:5000)  
→ webapp-service  
→ Serviços internos  
→ API externa (Open-Meteo)

O ponto de entrada da aplicação é o **webapp-service**, exposto através do Docker Port Publishing na porta 5000.

O Webapp orquestra chamadas internas para:

- surf-data-service
- notification-service
- scheduler-service

A API externa Open-Meteo é consumida exclusivamente pelo surf-data-service via HTTPS.

A observabilidade com Jaeger está ativa apenas no ambiente DEV.

O pipeline CI/CD automatiza a promoção da aplicação entre ambientes.

Ambientes:

## DEV
- Ambiente de desenvolvimento
- Observabilidade ativa com Jaeger
- ENABLE_OTEL=true
- Utilizado para debugging e tracing

## STG
- Ambiente de validação intermédia
- Estruturalmente igual ao PRD
- Sem Jaeger
- ENABLE_OTEL=false

## PRD
- Ambiente final
- Execução automática do scheduler
- Sem observabilidade ativa
- Ambiente estável para entrega de valor

------------------------------------------------------------------------

## Arquitetura

A aplicação segue uma arquitetura baseada em microserviços
containerizados utilizando Docker.

O webapp atua como ponto central de acesso às APIs, encaminhando os
pedidos para os serviços internos.

O serviço de dados integra uma API meteorológica externa para recolha de
informações relevantes sobre vento, ondas e temperatura. O serviço de
notificações processa relatórios automatizados destinados aos
utilizadores finais.

A observabilidade é assegurada através do Jaeger com OpenTelemetry.

Ambientes:

-   DEV -- desenvolvimento e testes\
-   STG -- validação intermédia\
-   PRD -- produção

------------------------------------------------------------------------

## Pipeline CI/CD

Pipeline implementado com GitHub Actions.

Etapas:

1. Quality Gate
- pytest
- Bandit (SAST)
- pip-audit

Bloqueia pipeline se HIGH/CRITICAL.

2. Build Images
- Build das imagens Docker
- Tag com APP_TAG

3. Scan de Segurança
- Trivy para análise das imagens

4. Deploy Automático
- Deploy DEV
- Deploy STG
- Deploy PRD

Deploy realizado com:

docker compose up -d

A atualização ocorre através de pull da nova imagem e recriação dos containers.


------------------------------------------------------------------------

##  Pré-requisitos do Ambiente

Antes de executar o projeto, certifique-se de que possui:

* **Sistema Operacional:** Linux, macOS ou Windows (WSL recomendado)
* **Docker:** >= 24.x
* **Docker Compose:** >= v2.x (`docker compose`)
* **Python:** **3.10+** (recomendado **Python 3.11**)
* **Git** instalado

Verifique versões:

```bash
docker --version
docker compose version
python3 --version
git --version
```

------------------------------------------------------------------------

## Configuração do Ambiente Python (do zero)

Caso esteja a configurar o ambiente pela primeira vez:

Criar ambiente virtual:

```bash
python3 -m venv .venv
```

Ativar ambiente virtual:

Linux / macOS:

```bash
source .venv/bin/activate
```

Windows (PowerShell):

```powershell
.venv\Scripts\Activate.ps1
```

Instalar dependências de desenvolvimento:

```bash
pip install --upgrade pip
pip install -r requirements-dev.txt
```

Isso instalará ferramentas usadas no projeto, incluindo:

* **Bandit** → análise de segurança do código
* **pip-audit** → verificação de vulnerabilidades em dependências
* Ferramentas de teste e qualidade

------------------------------------------------------------------------

## Análise de Segurança (Makefile)

Para executar verificações de segurança:

```bash
make security
```

Isso executa:

* `bandit` → análise estática do código Python
* `pip-audit` → auditoria das dependências (todos os requirements)

Os relatórios serão gerados em:

```
Testes_de_Vulnerabilidade/
```

------------------------------------------------------------------------

## Execução com Docker

Ambiente padrão:

```bash
make up
```

Ambiente de desenvolvimento (DEV):

```bash
make dev
```

Ambiente de staging:

```bash
make stg
```

Isso garante:

* Containers atualizados
* Nginx ativo nas portas **80 e 443**
* Configuração consistente entre ambientes

Para parar os containers:

```bash
make down
```

Limpeza completa:

```bash
make clean
```

------------------------------------------------------------------------

## Acesso à aplicação

Após subir os containers:

* HTTP → http://localhost
* HTTPS → https://localhost
  *(certificado self-signed do Nginx)*

------------------------------------------------------------------------

## 📝 Observações

* O Nginx é utilizado como **reverse proxy padrão** em todos os ambientes.
* Certificados SSL locais são apenas para desenvolvimento.
* O projeto foi testado principalmente em **Linux Ubuntu 22.04+**.


------------------------------------------------------------------------
## Endpoint Principal

Exemplo:

curl http://localhost:5000/report

Fluxo executado:

1. webapp recebe requisição
2. surf-data-service consulta Open-Meteo
3. dados retornam ao webapp
4. notification-service gera relatório
5. resposta enviada ao utilizador

------------------------------------------------------------------------

## Execução Automática (PRD)

No ambiente PRD, o scheduler-service executa chamadas internas periódicas:

scheduler → webapp → notification-service
Gerando relatórios automáticos.

------------------------------------------------------------------------

## Testes

Testes automatizados executados na pipeline:

- Unit tests
- Smoke tests
- Security checks

Garantem estabilidade antes da promoção entre ambientes.

------------------------------------------------------------------------

## DevSecOps

A segurança foi integrada diretamente ao pipeline.

Ferramentas utilizadas:

- Bandit (SAST)
- pip-audit (dependências)
- Trivy (scan de imagens Docker)

Práticas implementadas:

- Comunicação interna protegida com INTERNAL_TOKEN
- Separação lógica de serviços
- Validação contínua no CI/CD
- Bloqueio para vulnerabilidades HIGH/CRITICAL


Prints dos testes na pasta Prints.

------------------------------------------------------------------------

## Monitoramento

A observabilidade com Jaeger e OpenTelemetry está ativa apenas no ambiente DEV.

Permite:

- Tracing distribuído
- Identificação de gargalos
- Debugging de chamadas internas

Interface padrão:

http://localhost:16686

------------------------------------------------------------------------

## Erros e Ajustes Durante o Projeto

Ocorreram desafios relacionados com Docker, CI/CD e integração de
serviços. Foram resolvidos através de ajustes na pipeline, Dockerfiles e
compose files.

Deixei prints dos erros e ajustes no arquivo README.pdf.
------------------------------------------------------------------------

## Limpeza e Destruição da Infraestrutura

Comandos utilizados:

docker compose down\
docker compose down -v\
docker system prune -af

------------------------------------------------------------------------

## Conclusão

O projeto demonstra a implementação prática de:

- Microserviços Python
- Docker Compose
- CI/CD automatizado
- DevSecOps
- Gestão de ambientes
- Observabilidade (DEV)

A arquitetura permite evolução futura e escalabilidade horizontal.

------------------------------------------------------------------------

## Fontes

-   Docker Docs\
-   GitHub Actions Docs\
-   OpenTelemetry Docs\
-   Jaeger Docs\
-   StackOverflow\
-   ChatGPT
    Deepseek
    Reddit
