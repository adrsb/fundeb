"""
Interface base para extractors (Strategy Pattern)
"""

import logging
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path

import pandas as pd
import yaml

from fundeb.config.settings import LOGGING_CONFIG_PATH

with open(LOGGING_CONFIG_PATH, encoding="utf-8") as file:
    logging_config = yaml.safe_load(file)
logging.config.dictConfig(logging_config)


class BaseExtractor(ABC):
    """Interface base para os extractors"""

    # Lógica de inicialização compartilhada (logger)
    def __init__(self):
        self.logger = logging.getLogger("my_module")
        self.logger.debug("Extrator para criado.")

    # Validação de entrada do arquivo
    def validate_file(self, file_path: str | Path) -> None:
        """
        Valida o arquivo de entrada
        Args:
            file_path: Caminho completo do arquivo a ser validado
        Raises:
            TypeError: Path deve ser str ou Path
            TypeError: Path não é um arquivo
            FileNotFoundError: Arquivo não encontrado
            ValueError: Arquivo vazio
        """
        self.logger.debug(f"Iniciando validação do Arquivo: {file_path}")

        file_path = Path(file_path)

        if isinstance(file_path, (str, Path)) is False:
            msg = f"O file_path deve ser str ou Path, não {type(file_path)}"
            self.logger.error(msg)
            raise TypeError(msg)
        if not file_path.is_file():
            msg = f"Path não é um arquivo: {file_path}"
            self.logger.error(msg)
            raise TypeError(msg)
        if not file_path.exists():
            msg = f"Arquivo não encontrado: {file_path}"
            self.logger.error(msg)
            raise FileNotFoundError(msg)
        if file_path.stat().st_size == 0:
            msg = f"Arquivo vazio: {file_path}"
            self.logger.error(msg)
            raise ValueError(msg)

        self.logger.info("Arquivo Validado com sucesso.")

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

    @abstractmethod
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

    # Adição de metadados
    def add_metadata(self, file_path: str | Path, df: pd.DataFrame) -> pd.DataFrame:
        """
        Adiciona colunas de metadados ao Dataframe
        Args:
            file_path (str | Path):
                Caminho completo do arquivo para extração de metadados
            df (pd.DataFrame): DataFrame bruto extraído
        Returns:
            pd.DataFrame: Dataframe extraído com metadados
        """
        logging.debug("Iniciando extração de metadados")

        stat = file_path.stat()

        logging.debug("Iniciando adição de metadados")
        # df["file_path"] = str(file_path)
        df["file_name"] = file_path.name
        # df["file_extension"] = file_path.suffix
        df["file_mb_size"] = round(stat.st_size / (1024 * 1024), 3)
        df["last_modified_time"] = datetime.fromtimestamp(stat.st_mtime)
        df["processing_time"] = datetime.now()

        logging.info("Metadados adicionados com sucesso.")
        return df

    # Salvar em arquivo Parquet
    def save(
        self, df: pd.DataFrame, file_path: str | Path, destiny_dir: str | Path
    ) -> None:
        """
        Armazena dados extraídos e validados com seus metadados em arquivo parquet
        Args:
            file_path (str | Path): Caminho completo do arquivo de origem
            df (pd.DataFrame): Dataframe extraído com metadados
            destiny_dir (str | Path): Caminho do diretório de destino
        """
        destiny_dir = Path(destiny_dir)
        destiny_dir.mkdir(parents=True, exist_ok=True)
        df.to_parquet(destiny_dir / f"{file_path.stem}.parquet")

    # Execução do mini fluxo completo
    def run_flow(self, file_path: str | Path) -> pd.DataFrame:
        """
        Extrai, adiciona metadados, valida o schema e retorna o DataFrame
        Args:
            file_path: Caminho do arquivo a ser processado
        Returns:
            pd.DataFrame: DataFrame processado e validado com metadados
        """
        self.validate_file(file_path)
        df = self.extract(file_path)
        self.validate_schema(df)
        df = self.add_metadata(file_path, df)
        return df


if __name__ == "__main__":
    print("Base Extractor Module")
