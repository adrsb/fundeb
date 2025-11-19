from datetime import timedelta
from prefect import flow, task, get_run_logger
from pydantic import ValidationError

# Importação dos nossos módulos de Design Patterns
from config.settings import get_settings
from ingestion.loader_factory import LoaderFactory
from processing.strategies import SoftCleaning, AggressiveCleaning
from integration.adapters import LegacyFinancialSystem, DataFrameToLegacyAdapter

# Carrega configurações (Singleton implícito)
settings = get_settings()

# -----------------------------------------------------------------------------
# TASKS (Unidades de Trabalho)
# -----------------------------------------------------------------------------

@task(
    name="Ingestão de Dados",
    description="Lê ficheiros de diversas fontes usando Factory Pattern",
    retries=settings.retry_attempts,
    retry_delay_seconds=settings.retry_delay_seconds,
    tags=["extraction", "io"]
)
def task_ingest_data(file_name: str):
    # O get_run_logger() obtém o logger específico desta execução de task
    logger = get_run_logger()
    
    full_path = settings.input_path / file_name
    file_type = file_name.split('.')[-1]
    
    logger.info(f"📥 A iniciar ingestão do ficheiro: {full_path}")

    try:
        # FACTORY PATTERN: Decide qual loader usar
        loader = LoaderFactory.get_loader(file_type)
        df = loader.load(str(full_path))
        
        logger.info(f"✅ Ingestão concluída. Registos lidos: {len(df)}")
        return df
        
    except FileNotFoundError:
        logger.error(f"❌ Ficheiro não encontrado: {full_path}")
        raise # Levanta erro para o Prefect marcar como falha e tentar retry
    except Exception as e:
        logger.error(f"❌ Erro inesperado na ingestão: {e}")
        raise

@task(
    name="Processamento de Dados",
    description="Aplica regras de negócio usando Strategy Pattern",
    tags=["transformation", "compute"]
)
def task_process_data(df, strategy_name: str):
    logger = get_run_logger()
    logger.info(f"⚙️ A aplicar estratégia de limpeza: '{strategy_name}'")

    # STRATEGY PATTERN: Seleção da estratégia
    if strategy_name == "aggressive":
        strategy = AggressiveCleaning()
    else:
        strategy = SoftCleaning()

    df_clean = strategy.clean(df)
    
    # Exemplo de log útil para debugging na UI
    missing_data = df_clean.isnull().sum().sum()
    logger.info(f"✅ Processamento finalizado. Valores nulos restantes: {missing_data}")
    
    return df_clean

@task(
    name="Carga para Legado",
    description="Adapta e envia dados para API Legada",
    tags=["load", "api"]
)
def task_export_data(df):
    logger = get_run_logger()
    logger.info("📤 A preparar adaptador para sistema legado...")

    # ADAPTER PATTERN: Conecta o mundo novo (Pandas) ao velho (Dicts)
    legacy_system = LegacyFinancialSystem()
    adapter = DataFrameToLegacyAdapter(legacy_system)
    
    try:
        adapter.save_dataframe(df)
        logger.info("✅ Carga efetuada com sucesso no sistema externo.")
    except Exception as e:
        logger.error(f"❌ Falha na API do sistema legado: {e}")
        raise

# -----------------------------------------------------------------------------
# FLOW (A Orquestração)
# -----------------------------------------------------------------------------

@flow(
    name="ETL Financeiro Master",
    description="Pipeline principal de ingestão e carga financeira",
    log_prints=True # Captura qualquer print() esquecido como log INFO
)
def financial_etl_flow(file_name: str = "dados.csv", strategy: str = "soft"):
    logger = get_run_logger()
    
    logger.info("-" * 40)
    logger.info(f"🚀 A iniciar Flow: {settings.app_name}")
    logger.info(f"🌍 Ambiente: {settings.app_env}")
    logger.info("-" * 40)

    # 1. Extração
    raw_data = task_ingest_data(file_name)

    # 2. Transformação
    clean_data = task_process_data(raw_data, strategy)

    # 3. Carga
    task_export_data(clean_data)
    
    logger.info("🏁 Flow finalizado com sucesso!")

# -----------------------------------------------------------------------------
# Execução Local (Para testes de desenvolvimento)
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    # Simula ficheiros existirem para o teste não falhar imediatamente
    import pandas as pd
    (settings.input_path / "dados.csv").touch()
    
    # Executa o flow
    financial_etl_flow(file_name="dados.csv", strategy="aggressive")