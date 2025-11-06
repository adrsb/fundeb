"""
Interface base para extractors (Strategy Pattern)
"""

from abc import ABC, abstractmethod
from datetime import datetime
import logging
from pathlib import Path

import pandas as pd


class BaseExtractor(ABC):
    """Interface base para extractors"""

    # Lógica de inicialização compartilhada (logger)
    def __init__(self):
        self.logger = logging.getLogger("extractor")
        self.logger.info("Extrator para criado.")

    # Validação de entrada do arquivo
    def validate_file(self, file_path: str | Path) -> None:
        """
        Valida o arquivo de entrada
        Args:
            file_path: Caminho completo do arquivo a ser validado
        Raises:
            FileNotFoundError: Arquivo não encontrado
            ValueError: Path não é um arquivo
            ValueError: Arquivo vazio
        """
        if isinstance(file_path, str):
            file_path = Path(file_path)

        logging.info(f"Iniciando validação do Arquivo: {file_path}")

        if not file_path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")

        if not file_path.is_file():
            raise ValueError(f"Path não é um arquivo: {file_path}")

        if file_path.stat().st_size == 0:
            raise ValueError(f"Arquivo vazio: {file_path}")

        logging.info("Arquivo Validado.")

    # Extração dos dados do arquivo
    @abstractmethod
    def extract(self, file_path: str | Path) -> pd.DataFrame:
        """
        Extrai dados do arquivo
        Args:
            file_path (str | Path): Caminho completo do arquivo a ser extraído
        Returns:
            pd.DataFrame: DataFrame com os dados extraídos
        """
        pass

    # Validação dos dados extraídos
    def validate_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Valida os dados extraídos
        Args:
            df (pd.DataFrame): DataFrame com os dados extraídos
        Raises:
            ValueError: Dados extraídos estão vazios
        Returns:
            pd.DataFrame: DataFrame validado
        """

        logging.info("Iniciando validação dos dados extraídos")

        if df.empty:
            raise ValueError("Dados extraídos estão vazios")

        logging.info("Dados extraídos validados com sucesso.")
        return df

    # Adição de metadados
    def add_metadata(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Adiciona colunas de metadados ao Dataframe
        Args:
            df (pd.DataFrame): DataFrame bruto extraído
        Returns:
            pd.DataFrame: Dataframe extraído com metadados
        """
        logging.info("Iniciando adição de metadados")

        stat = self.file_path.stat()

        # df["file_path"] = str(self.file_path)
        df["file_name"] = self.file_path.name
        # df["file_extension"] = self.file_path.suffix
        df["file_mb_size"] = round(stat.st_size / (1024 * 1024), 3)
        df["modified_time"] = datetime.fromtimestamp(stat.st_mtime)
        df["processing_time"] = datetime.now()

        logging.info("Metadados adicionados com sucesso.")
        return df

    # Salvar em arquivo Parquet
    def save(self, df: pd.DataFrame, destiny_dir: str | Path) -> None:
        """
        Armazena dados extraídos e validados com seus metadados em arquivo parquet
        Args:
            df (pd.DataFrame): Dataframe extraído com metadados
            destiny_dir (str | Path): Caminho do diretório de destino
        """
        if not isinstance(destiny_dir, Path):
            destiny_dir = Path(destiny_dir)
        destiny_dir.mkdir(parents=True, exist_ok=True)
        df.to_parquet(destiny_dir / f"{self.file_path.stem}.parquet")


if __name__ == "__main__":
    print("Base Extractor Module")
