"""
Arquivo de configuração utilizando Pydantic Settings para gerenciar
as variáveis de ambiente do projeto.
"""  # config/settings.py

import logging
import logging.config
import yaml
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    # --- Metadados do Projeto ---
    app_name: str = "Fundeb Data Project"
    app_env: str = Field(
        default="development", description="Ambiente: development, staging, production"
    )

    # --- Banco de Dados ---
    db_connection_string: str

    # --- Credenciais ---
    google_ai_api_key: str | None = None  # Exemplo de chave API opcional

    # --- Caminhos de Arquivos ---
    project_root: Path = Path(__file__).resolve().parents[3]
    data_dir: Path = project_root / "data"
    raw_dir: Path = data_dir / "raw"
    bronze_dir: Path = data_dir / "bronze"
    silver_dir: Path = data_dir / "silver"
    gold_dir: Path = data_dir / "gold"
    logs_dir: Path = data_dir / "logs"
    extractors_config_path: Path = (
        project_root / "src" / "fundeb" / "config" / "extractors_config.yaml"
    )
    logging_config_path: Path = (
        project_root / "src" / "fundeb" / "config" / "log_config.yaml"
    )

    # --- Configurações do Pipeline (Com Defaults) ---
    retry_attempts: int = Field(
        default=3, ge=1, le=10
    )  # ge=greater or equal (validação)
    retry_delay_seconds: int = 10
    batch_size: int = 500

    # Configuração do Pydantic para ler o .env
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",  # Ignora variáveis extras no .env que não estão aqui
    )

    def model_post_init(self, __context):
        # Cria os diretórios se eles não existirem
        # parents=True: cria pastas pai se necessário (ex: cria 'data' antes de 'output')
        # exist_ok=True: não dá erro se a pasta já existir
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.bronze_dir.mkdir(parents=True, exist_ok=True)
        self.silver_dir.mkdir(parents=True, exist_ok=True)
        self.gold_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)

    # O lru_cache (de functools) garante que a classe Settings seja instanciada apenas uma vez.
    # As chamadas subsequentes retornam o objeto em cache.
    @staticmethod
    @lru_cache()
    def get_logger(name: str = "fundeb_logger") -> logging.Logger:
        with open(settings.logging_config_path, encoding="utf-8") as file:
            logging_config = yaml.safe_load(file)
        logging.config.dictConfig(logging_config)
        return logging.getLogger(name)


# --- Implementação Singleton ---
# O lru_cache (de functools) garante que a classe Settings seja instanciada apenas uma vez.
# As chamadas subsequentes retornam o objeto em cache.
@lru_cache()
def get_settings() -> Settings:
    return Settings()  # type: ignore


settings = get_settings()

logger = settings.get_logger()

if __name__ == "__main__":
    # Testa a configuração carregada
    logger.debug("Carregando Configurações...")
    logger.debug("Carregando Configurações... Concluído.")
    print("#", 88 * "-")
    logger.info(f"App Name: {settings.app_name}")
    logger.info(f"Environment: {settings.app_env}")
    logger.info(f"DB Connection: {settings.db_connection_string}")
    logger.info(f"Google ai api key: {settings.google_ai_api_key}")
    logger.info(f"Root path: {settings.project_root}")
    logger.info(f"Data path: {settings.data_dir}")
    logger.info(f"Raw path: {settings.raw_dir}")
    logger.info(f"Bronze path: {settings.bronze_dir}")
    logger.info(f"Silver path: {settings.silver_dir}")
    logger.info(f"Gold path: {settings.gold_dir}")
    logger.info(f"logs path: {settings.logs_dir}")
