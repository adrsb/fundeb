# CACS FUNDEB Analysis

![FUNDEB Logo](https://www.gov.br/fnde/pt-br/acesso-a-informacao/acoes-e-programas/financiamento/fundeb/fundeb-home/@@collective.cover.banner/e0c58aa7-955e-4d4b-a99a-a6bfaaf50a18/@@images/81160181-a1d1-4a84-a467-2061f366a939.jpeg)

## 🎯 Visão Geral

O **CACS FUNDEB Analysis** é um projeto moderno de ciência de dados voltado para análise dos dados históricos de repasses de recursos financeiros do FUNDEB (Fundo de Manutenção e Desenvolvimento da Educação Básica e de Valorização dos Profissionais da Educação).

### Principais Características

- **🔮 Previsão**: Modelos de ML para prever repasses dos próximos 12 meses
- **📊 Visualização**: Dashboards interativos com Streamlit
- **🔄 Pipeline ETL**: Processamento automatizado de dados
- **🏗️ Arquitetura Limpa**: Seguindo princípios de Clean Architecture
- **✅ Qualidade**: Testes automatizados e ferramentas de qualidade de código
- **📚 Documentação**: Documentação completa e atualizada

### Tecnologias Principais

- **Python 3.11+** com Pydantic 2.0+
- **Pandas & Polars** para processamento de dados
- **Scikit-learn** para machine learning
- **Streamlit** para dashboards
- **SQLAlchemy 2.0** para persistência de dados

## 🚀 Início Rápido

### Instalação

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/cacs-fundeb-analysis.git
cd cacs-fundeb-analysis

# Instale as dependências
pip install -e .[dev]

# Configure o ambiente
cp env.example .env
```

### Uso Básico

```bash
# Executar pipeline completo
fundeb-pipeline --year 2025 --bimester 1

# Iniciar dashboard
streamlit run src/cacs_fundeb_analysis/app/app.py

# Ver configuração
fundeb-config
```

## 📖 Documentação

- [Instalação](installation.md) - Guia completo de instalação
- [Início Rápido](quickstart.md) - Primeiros passos
- [Referência da API](api.md) - Documentação da API
- [Contribuindo](contributing.md) - Como contribuir
- [Changelog](changelog.md) - Histórico de mudanças

## 🤝 Contribuindo

Contribuições são bem-vindas! Veja nosso [guia de contribuição](contributing.md) para mais detalhes.

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE.txt](../LICENSE.txt) para detalhes.

---

**Desenvolvido com ❤️ para melhorar a gestão dos recursos do FUNDEB**






