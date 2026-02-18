# Projeto Final DevOps Engineer

**Alisson Melo**

**Repositório GitHub:** https://github.com/Melo2L/projeto-final-devops (Público)

------------------------------------------------------------------------

## Introdução

Este projeto consiste no desenvolvimento de uma aplicação web baseada em
microserviços em Python, integrada num ambiente DevOps completo. A
aplicação foi containerizada com Docker e automatizada através de
pipelines de CI/CD, permitindo build, testes e deploy contínuos.

Além da funcionalidade da aplicação, o foco principal foi a
implementação da infraestrutura DevOps, incluindo automação de
deployment, observabilidade, monitorização e gestão de ambientes
distintos (DEV, STG e PRD).

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
  <img src="20260214-HLD-ProjetoFinal-DevOps.drawio.png" width="1000"/>
</p>

O meu HLD apresenta a arquitetura geral da plataforma SurfPulse baseada em microsserviços conteinerizados, evidenciando a separação entre gateway, serviços internos de dados, notificações e agendamento. O acesso do utilizador ocorre através de um ponto de entrada público (Load Balancer), que encaminha requisições para o gateway-service, responsável pela orquestração das chamadas internas e integração com a API externa Open-Meteo. 

A solução inclui observabilidade com Jaeger para rastreamento distribuído das requisições e monitorização do sistema. O agendamento automático é representado por um scheduler integrado a um serviço de triggering equivalente ao EventBridge. 

A versão em PDF foi incluída para melhor visualização durante a avaliação.
------------------------------------------------------------------------

## Arquitetura

A aplicação segue uma arquitetura baseada em microserviços
containerizados utilizando Docker.

O gateway atua como ponto central de acesso às APIs, encaminhando os
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

Pipeline implementado com GitHub Actions:

-   Quality Gate: **pytest** (unit/integration tests)
-   DevSecOps: **Bandit (SAST)** + **pip-audit (dependências)**
-   Build automático dos containers
-   Smoke tests automáticos (curl)
-   Deploy progressivo DEV → STG → PRD

Em PRD é gerado automaticamente um relatório diário através do fluxo:

scheduler → gateway → notification-service.

------------------------------------------------------------------------

## Ambientes DEV / STG / PRD

-   DEV: validação rápida\
-   STG: ambiente semelhante à produção\
-   PRD: entrega final para utilizadores

Em produção o sistema gera relatórios meteorológicos automáticos
formatados para e-mail e WhatsApp (simulação académica).

------------------------------------------------------------------------

## Modelo de Notificação

### WhatsApp (modelo)

Também deixei no arquivo README.pdf.

------------------------------------------------------------------------

### Email (modelo)

Também deixei no arquivo README.pdf.

------------------------------------------------------------------------

## Testes

Foram implementados smoke tests automáticos na pipeline para validar
endpoints críticos antes do deployment.

------------------------------------------------------------------------

------------------------------------------------------------------------

## DevSecOps (Testes de Vulnerabilidades)

De acordo com o módulo 8, o pipeline inclui validações automáticas de segurança:

- **Bandit (SAST)**: analisa o código Python (más práticas, padrões inseguros).
- **pip-audit**: verifica vulnerabilidades conhecidas nas dependências (requirements).

Execução local (opcional):

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

pytest -q
bandit -r services -ll -ii
pip-audit -r requirements.txt
```

Prints dos testes na pasta Prints.


## Monitoramento

Monitorização realizada com Jaeger + OpenTelemetry para tracing
distribuído entre microserviços.

Interface típica:

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

O projeto permitiu consolidar conhecimentos práticos em:

-   Docker e containerização\
-   CI/CD com GitHub Actions\
-   Microserviços Python\
-   Observabilidade\
-   Automação de deploy

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