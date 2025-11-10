"""
Extrator para arquivos CSV de conta corrente
"""

from pathlib import Path
from typing import Any

import pandas as pd

from fundeb.extractors.base_extractor import BaseExtractor


class CSVExtractor(BaseExtractor):
    """Extrator para arquivos CSV de conta corrente"""

    def __init__(
        self,
        config_params: dict[str, Any],
    ):
        super().__init__()
        self.logger.debug("inicializando CSVExtractor...")
        self.read_kwargs = config_params
        self.logger.debug(f"CSVExtractor inicializado com params: {self.read_kwargs}]")

    def extract(self, file_path) -> pd.DataFrame:
        """Extrai dados do CSV"""
        self.logger.info(f"Iniciando extração: {file_path}...")

        try:
            df = pd.read_csv(file_path, **self.read_kwargs)

            self.logger.info(
                f"Arquivo extraído com sucesso! "
                f"{len(df)} linhas, {len(df.columns)} colunas"
            )
            return df

        except Exception as e:
            msg = f"Erro ao extrair CSV {file_path}: {e}"
            self.logger.error(msg)
            raise ValueError(msg) from e

    def validate_schema(self, df: pd.DataFrame) -> bool:
        """
        Valida se o DataFrame está com o schema esperado
        Args:
            df (pd.DataFrame): DataFrame a ser validado
        Returns:
            bool: True se o schema estiver correto, False caso contrário
        Raises:
            ValueError: Se o schema não estiver conforme esperado
        """
        pass


# --- O BLOCO DE TESTE (SMOKE TEST) ---
if __name__ == "__main__":
    import logging

    import yaml

    from fundeb.config.settings import EXTRACTORS_CONFIG_PATH, LOGGING_CONFIG_PATH

    # Carrega a configuração do arquivo YAML de logging
    with open(LOGGING_CONFIG_PATH) as file:
        logging_config = yaml.safe_load(file)
    logging.config.dictConfig(logging_config)
    logger = logging.getLogger("my_module")

    # Carrega a configuração do arquivo YAML de extractors
    logger.debug("Iniciando teste do CSVExtractor...")

    with open(EXTRACTORS_CONFIG_PATH) as f:
        config = yaml.safe_load(f.read())
    config_params = config["conta_corrente"]["csv"]["params"]
    logger.debug(f"Parâmetros carregados: {config_params}")

    logger.debug("Inicializando CSVExtractor...")
    extractor = CSVExtractor(config_params=config_params)

    logger.debug("Inicializando Extração...")
    test_file = (
        r"C:\Users\adrsb\OneDrive\Documentos\Projects\FundebProject\data\raw"
        r"\external\bb\conta_corrente\csv\EXTRATO_BANCARIO_CC_AP_MACAPA_2025_01.csv"
    )
    df = extractor.extract(test_file)

    logger.info(f"DataFrame extraído:\n{df.head()}")
