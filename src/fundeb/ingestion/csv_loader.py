"""
Extrator para arquivos CSV de conta corrente
"""

from typing import Any

import great_expectations as gx
import pandas as pd

from fundeb.ingestion.loader import DataLoader
from fundeb.config.settings import settings, logger


class CSVExtractor(DataLoader):
    """Extrator para arquivos CSV de conta corrente"""

    def __init__(
        self,
        config_params: dict[str, Any],
    ):
        super().__init__()
        self.logger.debug("Inicializando CSVExtractor...")
        self.read_kwargs = config_params
        self.logger.info(f"Parâmetros: {self.read_kwargs}")
        self.logger.debug("Inicialização de CSVExtractor... Concluída.")

    def extract(self, file_path) -> pd.DataFrame:
        """Extrai dados do CSV"""
        self.logger.debug("Iniciando extração do CSV...")
        self.logger.info(f"Arquivo: {file_path}")
        try:
            df = pd.read_csv(file_path, **self.read_kwargs)
            self.logger.info(f"Dados: {len(df)} linhas, {len(df.columns)} colunas")
            self.logger.debug("Extração do CSV... Concluída.")
        except Exception as e:
            msg = f"Erro ao tentar ler o arquivo CSV: {e}"
            self.logger.exception(msg)
            raise
        return df

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
    import yaml

    from fundeb.config.settings import EXTRACTORS_CONFIG_PATH

    with open(EXTRACTORS_CONFIG_PATH, encoding="utf-8") as f:
        config = yaml.safe_load(f.read())
    config_params = config["conta_corrente"]["csv"]["params"]

    extractor = CSVExtractor(config_params=config_params)

    test_file = (
        r"C:\Users\adrsb\OneDrive\Documentos\Projects\FundebProject\data\raw"
        r"\external\bb\conta_corrente\csv\EXTRATO_BANCARIO_CC_AP_MACAPA_2025_01.csv"
    )
    df = extractor.extract(test_file)

    # print(extractor.validate_schema(df))
