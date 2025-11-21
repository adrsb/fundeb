from pathlib import Path
from typing import Any

import pandas as pd
from prefect import flow, task
from prefect.assets import materialize
from prefect.logging import get_logger

from fundeb.config.settings import settings
from fundeb.ingestion.base_data_loader import BaseDataLoader
from fundeb.ingestion.factory import ExtractionFactory, get_extraction_factory
from fundeb.utils.file_discovery import recursive_list_file_paths


logger = get_logger()


@task(name="Get Factory")
def get_factory_instance_task() -> ExtractionFactory:
    """Instancia a factory

    Returns:
        ExtractionFactory: Factory
    """
    factory_instance = get_extraction_factory()
    return factory_instance


@task(name="Get Extractor")
def get_extractor_instance_task(
    factory_instance,
    module_name: str,
    file_extension: str,
) -> BaseDataLoader:
    """Instancia o extrator

    Args:
        factory_instance (_type_): Instancia da Factory
        module_name (str, optional): Nome do módulo. Defaults to "conta_corrente".
        file_extension (str, optional): Extensão do arquivo. Defaults to "csv".

    Returns:
        BaseDataLoader: Extrator
    """
    extractor_instance = factory_instance.create_extractor(module_name, file_extension)
    return extractor_instance


@task(name="Get Params")
def get_extractor_params_task(
    extractor_instance: BaseDataLoader,
    module_name: str,
    file_extension: str,
) -> dict[str, Any]:
    """_summary_

    Args:
        extractor_instance (BaseDataLoader): _description_
        module_name (str, optional): _description_. Defaults to "conta_corrente".
        file_extension (str, optional): _description_. Defaults to "csv".

    Returns:
        dict[str, Any]: _description_
    """
    params = extractor_instance.get_params(module_name, file_extension)
    return params


@task(name="Get File Paths")
def get_file_paths_task(
    base_directory: Path,
    pattern: str,
) -> list[Path]:
    """Função recursiva para listar arquivos

    Args:
        base_directory (Path, optional): Diretório base para encontrar os arquivos.
            Defaults to settings.raw_dir
        pattern (str, optional): Extensão do arquivo. Defaults to "*.csv"

    Returns:
        list[Path]: Lista de caminhos dos arquivos encontrados
    """
    base_directory = base_directory / "external" / "bb" / "conta_corrente"
    pattern = "*.csv"
    file_paths = recursive_list_file_paths(base_directory, pattern)
    if not file_paths:
        raise FileNotFoundError(
            f"Nenhum arquivo encontrado em {base_directory} com padrão {pattern}"
        )
    return file_paths


@task(name="Validate File Path")
def validate_file_path_task(
    file_path: Path,
    extractor_instance: BaseDataLoader,
) -> Path:
    result = extractor_instance.validate_file(file_path)
    return result


@materialize(
    "file://data//raw//external//bb//conta_corrente//csv",
    name="Load Raw Data",
)
def load_data_task(
    file_path: Path,
    extractor_instance: BaseDataLoader,
) -> pd.DataFrame:
    df = extractor_instance.load_data(file_path)
    return df


@task(name="Validate Data Schema")
def validate_schemas_task(
    df: pd.DataFrame,
    file_path: Path,
    module: str,
    extractor_instance: BaseDataLoader,
) -> None:
    extractor_instance.validate_schema(df, file_path, module)


@materialize(
    "file://data//raw//external//bb//conta_corrente//csv",
    name="Add File Metadata",
)
def add_metadata_task(
    df: pd.DataFrame,
    file_path: Path,
    extractor_instance: BaseDataLoader,
) -> pd.DataFrame:
    df_with_metadata = extractor_instance.add_metadata(file_path, df)
    return df_with_metadata


@task(name="Save Raw Data")
def save_to_bronze_task(
    df: pd.DataFrame,
    file_path: Path,
    destiny_dir: Path,
    extractor_instance: BaseDataLoader,
):
    extractor_instance.save_to_bronze(df, file_path, destiny_dir)


@flow(name="Csv Current Account Sequencial Flow")
def run_current_account_sequencial_flow(
    base_dir: Path = settings.raw_dir,
    source: str = "external",
    origin: str = "bb",
    module: str = "conta_corrente",
    extension: str = "csv",
    destiny_dir: Path = settings.bronze_dir,
):
    print("Inicializando Flow...")
    factory_instance = get_factory_instance_task()
    extractor_instance = get_extractor_instance_task(
        factory_instance, module_name=module, file_extension=extension
    )
    get_extractor_params_task(
        extractor_instance=extractor_instance,
        module_name=module,
        file_extension=extension,
    )
    file_extension = "." + extension
    file_paths = get_file_paths_task(base_directory=base_dir, pattern=file_extension)
    destiny_dir = destiny_dir / source / origin / module
    # Execução sequencial
    for file_path in file_paths:
        validated_file_path = validate_file_path_task(
            file_path=file_path, extractor_instance=extractor_instance
        )
        df = load_data_task(validated_file_path, extractor_instance)
        validate_schemas_task(df, validated_file_path, module, extractor_instance)
        df_with_metadata = add_metadata_task(
            df, validated_file_path, extractor_instance
        )
        save_to_bronze_task(
            df_with_metadata, validated_file_path, destiny_dir, extractor_instance
        )
    print("Flow... Concluído.")


@flow(name="Csv Current Account Concurrently Flow")
def run_current_account_concurrently_flow(
    base_dir: Path = settings.raw_dir,
    source: str = "external",
    origin: str = "bb",
    module: str = "conta_corrente",
    extension: str = "csv",
    destiny_dir: Path = settings.bronze_dir,
):
    print("Inicializando Flow...")
    factory_instance = get_factory_instance_task()
    extractor_instance = get_extractor_instance_task(
        factory_instance, module_name=module, file_extension=extension
    )
    get_extractor_params_task(
        extractor_instance=extractor_instance,
        module_name=module,
        file_extension=extension,
    )
    file_extension = "." + extension
    file_paths = get_file_paths_task(base_directory=base_dir, pattern=file_extension)
    destiny_dir = destiny_dir / source / origin / module
    # Execução simultânea
    validate_file_paths = validate_file_path_task.map(
        file_path=file_paths, extractor_instance=extractor_instance
    )
    validate_file_paths.wait()
    dfs = load_data_task.map(validate_file_paths, extractor_instance)
    dfs.wait()
    validate_schemas_task.map(
        dfs, validate_file_paths, module, extractor_instance
    ).wait()
    dfs_with_metadata = add_metadata_task.map(
        dfs, validate_file_paths, extractor_instance
    )
    dfs_with_metadata.wait()
    save_to_bronze_task.map(
        df=dfs_with_metadata,
        file_path=validate_file_paths,
        destiny_dir=destiny_dir,
        extractor_instance=extractor_instance,
    ).wait()
    display(dfs_with_metadata[0].result().head())  # type: ignore # noqa: F821


if __name__ == "__main__":
    # run_current_account_sequencial_flow()
    run_current_account_concurrently_flow()
