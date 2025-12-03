# Modern Data Stack (Python & Open Source)

Este documento apresenta uma curadoria de ferramentas para um projeto de Engenharia, Ciência e Análise de Dados, com foco estrito em soluções Open Source e ecossistema Python.

A coluna **"Melhor Ferramenta"** reflete a tendência atual de mercado focada em performance (muitas ferramentas reescritas em Rust) e Developer Experience (DX).

## 1. Engenharia de Dados (O Pipeline Central)

| **Etapa**         | **Descrição Etapa**                                 | **Ferramenta Consolidada** | **Melhor Ferramenta (Tendência/DX)**                         | **Ferramentas Atuais Alternativas**     |
| ----------------------- | ----------------------------------------------------------- | -------------------------------- | ------------------------------------------------------------------- | --------------------------------------------- |
| **Storage**       | Persistência de dados brutos (Data Lake/Object Storage).   | **MinIO** (S3 Compatible) | **MinIO**                                                     | Ceph, Apache Ozone, Local Filesystem          |
| **Ingest**        | Coleta de dados de múltiplas fontes (EL - Extract & Load). | **Airbyte**                | **DLT (Data Load Tool)**                                     | Singer Taps,**Meltano** para Code-first |
| **Transform**     | Limpeza, modelagem e regras de negócio (T - Transform).    | **DBT Core**               | **DBT Core**                                                  | SQLMesh, Pandas, Polars, Spark                |
| **Quality**       | Validação de dados, profiling e testes de contrato.       | **Great Expectations**     | **Soda Core**(Mais leve/Simples) ou **DBT Tests**      | Pandera (Ótimo p/ Python puro), Pydantic     |
| **Load (OLAP)**   | Armazenamento para análise (Data Warehouse/Lakehouse).     | **PostgreSQL**             | **DuckDB**(Local/In-process) ou **ClickHouse**(Escala) | Apache Doris, StarRocks, Trino                |
| **Orchestration** | Agendamento, gerenciamento de dependências e fluxo.        | **Apache Airflow**         | **Dagster**(Asset-centric) ou **Prefect**              | Mage.ai, Kestra                               |

## 2. Analytics e BI (Consumo de Dados)

| **Etapa**             | **Descrição Etapa**                                            | **Ferramenta Consolidada** | **Melhor Ferramenta**                       | **Ferramentas Atuais Alternativas** |
| --------------------------- | ---------------------------------------------------------------------- | -------------------------------- | ------------------------------------------------- | ----------------------------------------- |
| **Visualization**     | Bibliotecas de plotagem de gráficos em código.                       | **Matplotlib / Seaborn**   | **Plotly**(Interativo) ou **Altair** | Bokeh, HoloViews                          |
| **Auto Report**       | Criação de relatórios estáticos ou documentos HTML/PDF.            | **Jupyter Notebooks**      | **Quarto**(Sucessor do RMarkdown p/ Python) | Papermill, Datapane                       |
| **Auto Presentation** | Conversão de análises em slides automaticamente.                     | **Jupyter + RISE**         | **Quarto**(Revealjs integration)            | Marp, Streamlit (modo slide)              |
| **Dashboards**        | Relatórios interativos e Business Intelligence para usuários finais. | **Apache Superset**        | **Streamlit**(Para Devs Python)             | Metabase (OSS version), Panel, Dash       |

## 3. Qualidade e Governança (Confiança nos Dados)

| **Etapa**      | **Descrição Etapa**                                       | **Ferramenta Consolidada**    | **Melhor Ferramenta**                      | **Ferramentas Atuais Alternativas**                     |
| -------------------- | ----------------------------------------------------------------- | ----------------------------------- | ------------------------------------------------ | ------------------------------------------------------------- |
| **Security**   | Gestão de segredos, credenciais e controle de acesso.            | **HashiCorp Vault**           | **HashiCorp Vault**                        | Bitwarden (Self-hosted), Mozilla SOPS                         |
| **Governance** | Catálogo de dados, dicionário e linhagem.                       | **Amundsen**                  | **DataHub** ou **OpenMetadata**     | Atlas, Marquez                                                |
| **Versioning** | Controle de versão para grandes volumes de dados (Git for Data). | **DVC**(Data Version Control) | **DVC**(ou**LakeFS**para Data Lakes) | Nessie, Pachyderm                                             |
| **Monitoring** | Observabilidade de pipeline e qualidade de dados.                 | **Prometheus + Grafana**      | **OpenTelemetry**(Padrão atual)           | Elementary (focado em dbt), DataDog (Proprietário mas comum) |

## 4. Software Engineering (Qualidade de Código Python)

*Nota: Esta seção foca na modernização do tooling Python, onde ferramentas escritas em Rust (como Ruff e uv) estão substituindo ferramentas legadas.*

| **Etapa**          | **Descrição Etapa**                          | **Ferramenta Consolidada**   | **Melhor Ferramenta (Performance)**        | **Ferramentas Atuais Alternativas** |
| ------------------------ | ---------------------------------------------------- | ---------------------------------- | ------------------------------------------------ | ----------------------------------------- |
| **Env Management** | Gerenciamento de dependências e ambientes virtuais. | **Pip / Virtualenv / Conda** | **uv**(Ultra-rápido) ou **Poetry** | PDM, Pipenv, Pyenv                        |
| **Linting/Fmt**    | Análise estática e formatação de código.        | **Flake8 + Black + Isort**   | **Ruff**(Substitui todos os anteriores)    | Pylint, Blue, Yapf                        |
| **Type Checking**  | Verificação estática de tipagem (Type Hints).     | **MyPy**                     | **Pyright**(Mais rápido/VSCode)           | Pyre, Pytype                              |
| **Tests**          | Execução de testes unitários e integração.      | **Pytest**                   | **Pytest**(Padrão absoluto)               | Unittest (Built-in)                       |

## 5. Deployment e Infraestrutura (DevOps/MLOps)

| **Etapa**            | **Descrição Etapa**                     | **Ferramenta Consolidada** | **Melhor Ferramenta**                                        | **Ferramentas Atuais Alternativas** |
| -------------------------- | ----------------------------------------------- | -------------------------------- | ------------------------------------------------------------------ | ----------------------------------------- |
| **Code Versioning**  | Controle de versão de código-fonte.           | **Git**                    | **Git**                                                      | Mercurial (Raro uso)                      |
| **Repo Hosting**     | Hospedagem de repositórios (Self-hosted/Open). | **GitLab**(CE)             | **GitLab** ou **Gitea**(Leve)                         | Gogs, Bitbucket (Não é OSS)             |
| **Containerization** | Empacotamento da aplicação.                   | **Docker**                 | **Docker**(ou **Podman**- daemonless)                 | LXC, Containerd                           |
| **Orchestration**    | Orquestração de containers em produção.     | **Kubernetes (K8s)**       | **K8s**(via**K3s**para leveza)                         | Docker Swarm, Nomad                       |
| **CI/CD**            | Automação de esteiras de deploy.              | **Jenkins**                | **GitLab CI**ou**GitHub Actions**(Runners self-hosted) | ArgoCD (GitOps), Drone CI                 |
| **IaC**              | Infraestrutura como código.                    | **Terraform**              | **OpenTofu**(Fork Open Source do Terraform)                  | Pulumi, Ansible                           |
| **Documentation**    | Documentação técnica do projeto e código.   | **Sphinx**                 | **MkDocs**(+ Material Theme)                                 | Docusaurus, VitePress                     |
| **API Dev**          | Framework para servir modelos ou dados via API. | **Flask / Django**         | **FastAPI**(Moderno/Async)                                   | Litestar, Sanic                           |

## Combo Sugerido

*Focado em Developer Experience (DX), velocidade (ferramentas Rust-based) e modernidade.*

* **Ingest:** DLT
* **Load:** MinIO + DuckDB
* **Transform:** DBT + Polars
* **Quality:** DBT Tests
* **Orchestration:** Dagster
* **Python Tooling:** UV + Ruff + Pytest
* **BI/Viz:** Streamlit + Plotly
* **Reports:** Quarto
* **Infra:** Git/Github + Docker + Terraform + GitHub Actions

# Prompt

Gostaria que você elaborasse tabelas em .md sobre modern data stack de um projeto python de engenharia, ciência e análise de dados, com as seguintes colunas:

* Etapa
* Descrição Etapa
* Ferramenta Consolidada
* Melhor Ferramenta
* Ferramentas Atuais Alternativas

As Etapas são as seguintes:

* Engenharia de Dados (O Pipeline Central):

  * storage - Persistência de dados brutos (Data Lake)
  * Ingest - Coleta de dados de múltiplas fontes
  * Transform - Limpeza, padronização, enriquecimento
  * Quality - Validação, profiling, testes dos dados
  * Load - Carregamento em DW/Lakehouse
  * Orquestration - Agendamento e gerenciamento de fluxo
* Analytics e BI (Consumo de Dados)

  * Visualization - Gráficos
  * Automatic Report - Criação automática de relatório em MD
  * Automatic Presentation - Criação automática de slides
  * Dashboards - Relatórios interativos
* Qualidade e Governança (Confiança nos Dados)

  * Security - Gestão de credenciais e acesso
  * Governance - Catálogo, linhagem e conformidade
  * Versioning - Controle de versão de datasets
  * Monitoring - Observabilidade e alertas
* Software Engineering (Qualidade de Código Python)

  * Environment Management - Gerenciamento de Dependência
  * Linting/Formatting - Padronização e qualidade de código
  * Type Checking - Verificação estática de tipos
  * Tests - Testes unitários e integração
* Deployment e Infraestrutura (DevOps/MLOps)

  * Code Versioning - Controle de versão de código-fonte
  * Repository Hosting - Hospedagem de repositórios e colaboração
  * Containerization - Empacotamento de aplicações em containers
  * Container Orchestration - Orquestração de containers em produção
  * CI/CD - Automação de deploy
  * IaC - Infraestrutura Cloud
  * Documentation - Documentação de código e projetos
  * API Development - Desenvolvimento de APIs REST/GraphQL

Foque em ferramentas open source. No final, gere uma tabela com os 3 melhores combos comtemplando todas as etapas citadas.
