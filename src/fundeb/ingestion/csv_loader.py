"""
Extrator para arquivos CSV
"""

from pathlib import Path
from typing import Any

import pandas as pd

from fundeb.ingestion.base_data_loader import BaseDataLoader
from fundeb.config.settings import settings


logger = settings.get_logger()


class CsvLoader(BaseDataLoader):
    """Extrator de arquivos CSV"""

    def __init__(self, extractors_config_path: Path):
        super().__init__(extractors_config_path)

    def load_data(self, file_path: Path) -> pd.DataFrame:
        """Extrai dados do CSV"""
        try:
            logger.debug("Iniciando extração do CSV...")
            logger.info(f"Arquivo: {file_path}")
            df: pd.DataFrame = pd.read_csv(file_path, **self.params_kwargs)
            logger.info(f"Dados: {len(df)} linhas, {len(df.columns)} colunas")
            logger.debug("Iniciando extração do CSV... Concluída.")
        except Exception as e:
            msg = f"Erro ao tentar ler o arquivo CSV: {e}"
            logger.exception(msg)
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
    extractor = CsvLoader(extractors_config_path=settings.extractors_config_path)
    file_path_test = (
        r"C:\Users\adrsb\OneDrive\Documentos\Projects\FundebProject\data\raw"
        r"\external\bb\conta_corrente\csv\EXTRATO_BANCARIO_CC_AP_MACAPA_2025_01.csv"
    )
    df = extractor.run_flow(
        file_path_test,
        source="external",
        origin="bb",
        module="conta_corrente",
        file_extension="csv",
    )

    # display(df.head(3))
