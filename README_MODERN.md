# CACS FUNDEB Analysis

![FUNDEB Logo](https://www.gov.br/fnde/pt-br/acesso-a-informacao/acoes-e-programas/financiamento/fundeb/fundeb-home/@@collective.cover.banner/e0c58aa7-955e-4d4b-a99a-a6bfaaf50a18/@@images/81160181-a1d1-4a84-a467-2061f366a939.jpeg)

## 📋 Sobre o Projeto

O **CACS FUNDEB Analysis** é um projeto de ciência de dados moderno voltado para análise dos dados históricos de repasses de recursos financeiros do FUNDEB (Fundo de Manutenção e Desenvolvimento da Educação Básica e de Valorização dos Profissionais da Educação).

### 🎯 Objetivos

- **Previsão**: Prever os repasses do FUNDEB nos próximos 12 meses
- **Visualização**: Disponibilizar dashboards interativos para apoio à tomada de decisão
- **Automação**: Pipeline automatizado para coleta e processamento de dados
- **Qualidade**: Implementar boas práticas de desenvolvimento e arquitetura limpa

## 🏗️ Arquitetura

O projeto segue os princípios da **Clean Architecture** e **Domain-Driven Design**:

📁 cacs-fundeb-analysis/
├── 📁 src/cacs_fundeb_analysis/
│   ├── 📁 core/                    # Regras de negócio e entidades
│   ├── 📁 data/                    # Camada de dados e ETL
│   ├── 📁 services/                # Serviços de aplicação
│   ├── 📁 api/                     # APIs REST
│   └── 📁 web/                     # Interface Streamlit
├── 📁 data/
│   ├── 📁 bronze/                  # Dados brutos (raw)
│   ├── 📁 silver/                  # Dados limpos (interim)
│   ├── 📁 gold/                    # Dados processados (processed)
│   └── 📁 external/                 # Dados externos
├── 📁 tests/                       # Testes automatizados
├── 📁 docs/                        # Documentação
└── 📁 notebooks/                   # Jupyter notebooks

## 🚀 Tecnologias

### Core

- **Python 3.11+** - Linguagem principal
- **Pydantic 2.0+** - Validação de dados e configurações
- **SQLAlchemy 2.0+** - ORM para banco de dados
- **SQLModel** - Modelos SQL com Pydantic

### Data Processing

- **Pandas 2.0+** - Manipulação de dados
- **Polars 0.20+** - Processamento rápido de dados
- **PyArrow 12.0+** - Formato de dados colunar

### Machine Learning

- **Scikit-learn 1.3+** - Algoritmos de ML
- **NumPy 1.24+** - Computação numérica
- **SciPy 1.11+** - Computação científica

### Visualization & Web

- **Streamlit 1.28+** - Dashboards interativos
- **Plotly 5.17+** - Visualizações avançadas

### Development Tools

- **Pytest** - Framework de testes
- **Black** - Formatação de código
- **Ruff** - Linting rápido
- **MyPy** - Verificação de tipos
- **Pre-commit** - Hooks de qualidade

## 📦 Instalação

### Pré-requisitos

- Python 3.11 ou superior
- Git

### Instalação Local

1. **Clone o repositório:**

```bash
git clone https://github.com/seu-usuario/cacs-fundeb-analysis.git
cd cacs-fundeb-analysis
```

2. **Instale as dependências:**

```bash
pip install -e .[dev]
```

3. **Configure o ambiente:**

```bash
cp env.example .env
# Edite o arquivo .env conforme necessário
```

4. **Instale os hooks de pre-commit:**

```bash
pre-commit install
```

## 🎮 Uso

### CLI

O projeto inclui uma interface de linha de comando moderna:

```bash
# Executar pipeline completo
fundeb-pipeline --year 2025 --bimester 1

# Executar apenas extração
fundeb-extract --source data/external --destination data/bronze

# Executar apenas transformação
fundeb-transform --source data/bronze --destination data/silver

# Executar apenas carregamento
fundeb-load --source data/silver --destination data/gold

# Ver configuração atual
fundeb-config
```

### Python API

```python
from src.cacs_fundeb_analysis.core.config import settings
from src.cacs_fundeb_analysis.core.entities import FundebTransfer, TransferType, StateCode
from src.cacs_fundeb_analysis.core.logging import setup_logging, get_logger

# Configurar logging
setup_logging()
logger = get_logger(__name__)

# Criar entidade
transfer = FundebTransfer(
    state=StateCode.AP,
    municipality="Macapá",
    amount=Decimal("1000000.00"),
    transfer_date=date(2025, 1, 15),
    transfer_type=TransferType.LIQUID
)

logger.info("Transfer created", transfer_id=str(transfer.id))
```

### Streamlit Dashboard

```bash
streamlit run src/cacs_fundeb_analysis/app/app.py
```

## 🧪 Testes

Execute os testes com:

```bash
# Todos os testes
pytest

# Com cobertura
pytest --cov=src --cov-report=html

# Testes específicos
pytest tests/unit/test_entities.py -v
```

## 🔧 Desenvolvimento

### Estrutura de Commits

Seguimos o padrão [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: adicionar nova funcionalidade de previsão
fix: corrigir bug na validação de dados
docs: atualizar documentação da API
test: adicionar testes para entidades
refactor: refatorar pipeline ETL
```

### Code Quality

O projeto usa várias ferramentas para garantir qualidade:

- **Black**: Formatação automática
- **Ruff**: Linting rápido e eficiente
- **MyPy**: Verificação de tipos estática
- **Pre-commit**: Hooks automáticos

### Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -m 'feat: adicionar nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## 📊 Dados

### Fontes de Dados

- **FNDE**: Transferências FUNDEB
- **Tesouro Transparente**: Dados financeiros
- **INEP**: Dados educacionais
- **IBGE**: Dados demográficos e econômicos

### Estrutura de Dados

- **Bronze Layer**: Dados brutos extraídos das fontes
- **Silver Layer**: Dados limpos e validados
- **Gold Layer**: Dados processados e agregados

## 📈 Roadmap

### Versão 0.2.0

- [ ] Implementar modelos de ML para previsão
- [ ] Adicionar API REST completa
- [ ] Implementar cache Redis
- [ ] Adicionar monitoramento com Prometheus

### Versão 0.3.0

- [ ] Migrar para arquitetura de microsserviços
- [ ] Implementar autenticação e autorização
- [ ] Adicionar testes de integração E2E
- [ ] Implementar CI/CD completo

## 📞 Contato

- **Email**: adrian.sbar07@gmail.com
- **LinkedIn**: [Seu LinkedIn]
- **GitHub**: [Seu GitHub]

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE.txt](LICENSE.txt) para detalhes.

---

**Desenvolvido com ❤️ para melhorar a gestão dos recursos do FUNDEB**
