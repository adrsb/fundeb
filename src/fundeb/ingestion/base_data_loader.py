from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

from fundeb.config.settings import settings


logger = settings.get_logger()


class BaseDataLoader(ABC):
    """Classe base responsável pela carga de dados de ficheiros."""

    def __init__(self, extractors_config_path: Path):
        logger.debug("Inicializando Extractor...")
        self.extractors_config_path = extractors_config_path
        self.params_kwargs: dict[str, Any] = {}
        logger.info(f"Origem dos parâmetros: {extractors_config_path}")
        logger.debug("Inicialização de Extractor... Concluída.")

    @staticmethod
    def validate_file(file_path: str | Path) -> Path:
        """Valida caminho completo do arquivo
        Args:
            validated_file_path (str | Path): Caminho completo do arquivo
        Returns:
            Path: Caminho completo do arquivo validado
        """
        logger.debug("Iniciando validação do Arquivo...")
        logger.info(f"Arquivo: {file_path}")
        try:
            validated_file_path = Path(file_path)
            if not validated_file_path.exists():
                msg = f"Arquivo não encontrado: {validated_file_path}"
                logger.error(msg)
                raise FileNotFoundError(msg)
            if not validated_file_path.is_file():
                msg = f"File path não é um arquivo: {validated_file_path}"
                logger.error(msg)
                raise TypeError(msg)
            if validated_file_path.stat().st_size == 0:
                msg = f"Arquivo vazio: {validated_file_path}"
                logger.error(msg)
                raise ValueError(msg)
        except Exception as e:
            msg = f"Erro inesperado: {e}"
            logger.error(msg)
            raise e
        logger.debug("Validação do Arquivo... Concluída.")
        return validated_file_path

    def get_params(
        self,
        module: str,
        file_extension: str,
        encoding: str = "utf-8",
    ) -> dict[str, Any]:
        logger.debug("Iniciando captura de parâmetros...")
        extractors_config_path: Path = self.extractors_config_path
        with open(extractors_config_path, encoding=encoding) as file:
            config = yaml.safe_load(file.read())
            params = config[module][file_extension]["params"]
        logger.info(f"Parâmetros: {params}")
        self.params_kwargs = params
        logger.debug("Captura de parâmetros... Concluída.")
        return self.params_kwargs

    @staticmethod
    @abstractmethod
    def load_data(file_path: Path) -> pd.DataFrame:
        """Carrega dados de um arquivo.
        Args:
            file_path (Path): Caminho completo do arquivo
        Returns:
            pd.DataFrame: DataFrame dos dados brutos
        """
        pass

    @staticmethod
    @abstractmethod
    def validate_schema(df: pd.DataFrame, file_path: Path, module: str) -> None:
        """Valida se o DataFrame está com o schema esperado
        Args:
            df (pd.DataFrame): DataFrame a ser validado
            file_path (Path): Path do arquivo
            module (str): Nome do módulo
        Returns:
            bool: True se o schema estiver correto, False caso contrário
        Raises:
            ValueError: Se o schema não estiver conforme esperado
        """
        pass

    @staticmethod
    def add_metadata(file_path: Path, df: pd.DataFrame) -> pd.DataFrame:
        """Adiciona colunas de metadados ao Dataframe validado
        Args:
            file_path (Path): Caminho completo do arquivo
            df (pd.DataFrame): DataFrame validado
        Returns:
            pd.DataFrame: Dataframe com metadados
        """
        logger.debug("Extraindo de metadados...")
        stat = file_path.stat()
        logger.info(f"Metadados: {stat}...")

        logger.debug("Iniciando adição de metadados...")
        df["FILE_NAME"] = file_path.name
        df["FILE_SIZE"] = f"{round(stat.st_size / (1024 * 1024), 3)} MB"  # MB
        df["LAST_MODIFIED"] = datetime.fromtimestamp(stat.st_mtime)
        df["LAST_PROCESSING"] = datetime.now()
        logger.debug("Metadados adicionados com sucesso.")
        return df

    @staticmethod
    def save_to_bronze(df: pd.DataFrame, file_path: Path, destiny_dir: Path) -> None:
        """Armazena dados extraídos e validados com seus metadados em arquivo .parquet
        Args:
            file_path (Path): Caminho completo do arquivo de origem
            df (pd.DataFrame): Dataframe com metadados
            destiny_dir (str | Path): Caminho do diretório de destino
        """
        logger.debug("Iniciando arquivamento do DataFrame em Parquet...")
        destiny_dir.mkdir(parents=True, exist_ok=True)
        file_name = f"{file_path.stem}.parquet"
        df.to_parquet(destiny_dir / file_name)
        logger.info(f"Diretório de Destino: {destiny_dir / file_name}")
        logger.debug("DataFrame salvo com sucesso!")

    def run_flow(
        self,
        file_path: str | Path,
        source: str,
        origin: str,
        module: str,
        file_extension: str,
    ) -> pd.DataFrame:
        """Executa fluxo completo como pipeline
        Args:
            file_path: Caminho completo do arquivo
        Returns:
            pd.DataFrame: DataFrame
        """
        logger.debug("Iniciando pipeline...")
        validated_file_path = self.validate_file(file_path)
        file_extension = (validated_file_path.suffix).replace(".", "")
        self.get_params(module=module, file_extension=file_extension)
        df = self.load_data(validated_file_path)
        self.validate_schema(df, file_path=validated_file_path, module=module)
        df = self.add_metadata(validated_file_path, df)
        destiny_dir = settings.bronze_dir / source / origin / module
        self.save_to_bronze(df, validated_file_path, destiny_dir=destiny_dir)
        logger.debug("Execução da pipeline... Concluída.")
        return df


if __name__ == "__main__":
    print("Base Extractor Module")
