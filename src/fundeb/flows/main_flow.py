import pandas as pd
from pathlib import Path
from typing import List, Dict, Any
import subprocess  # Para executar o dbt

# --- 1. Importações do Prefect ---
from prefect import flow, task
from prefect.tasks import task_input_hash  # Para cache
from datetime import timedelta

# --- 2. Importar os nossos Módulos Internos ---
# (Nada muda aqui)
from src.factory.factory import get_extraction_factory
from src.config.settings import (
    DATA_SOURCE_DIR,
    DATA_BRONZE_DIR,
    FILE_EXTENSION_MAP,
    DBT_PROJECT_DIR,
)
from src.utils.file_discovery import find_files_by_pattern

# --- 3. Definição das Regras de Descoberta ---
# (Nada muda aqui)
DISCOVERY_RULES = [
    # ... (as mesmas regras de antes) ...
    {"module_base": "conta_corrente", "pattern": "EXTRATO_BANCARIO_CC*.csv"},
    {"module_base": "conta_investimentos", "pattern": "INVEST_MES_*.csv"},
]

# --- 4. Transformar Funções em Tasks ---


# A nossa função de descoberta agora é uma "Task" do Prefect.
# Usamos 'cache_key_fn' para que ela só re-execute se as regras mudarem.
@task(
    name="1. Gerar Lista de Tarefas",
    cache_key_fn=task_input_hash,
    cache_expiration=timedelta(minutes=10),
)
def generate_task_list() -> List[Dict[str, Any]]:
    """Gera dinamicamente a lista de tarefas de ficheiros a processar."""
    print("Iniciando descoberta dinâmica de arquivos...")
    tasks_to_run = []

    for rule in DISCOVERY_RULES:
        module = rule["module_base"]
        pattern = rule["pattern"]

        files = find_files_by_pattern(
            base_dir=DATA_SOURCE_DIR, module_name=module, file_pattern=pattern
        )

        for file_path in files:
            task = {
                "module_base": module,
                "file_path": file_path,
                "filename": file_path.name,
            }
            tasks_to_run.append(task)

    print(f"Descoberta concluída. {len(tasks_to_run)} arquivos encontrados.")
    return tasks_to_run


# A lógica de processar UM ficheiro torna-se uma Task.
# Esta é a magia! Podemos adicionar retentativas.
@task(
    name="2. Processar Ficheiro Individual",
    retries=2,  # <--- MÁGICA: Tenta novamente 2x se falhar
    retry_delay_seconds=10,
)
def process_file_task(task_info: Dict[str, Any]):
    """
    Task para executar o Extract-Load (EL) de um único ficheiro
    para a camada Bronze.
    """
    module_name = task_info["module_base"]
    file_path = task_info["file_path"]
    filename = task_info["filename"]

    print(f"\n--- Processando: {filename} (Módulo: {module_name}) ---")

    try:
        # 1. Obter a Fábrica (Singleton, seguro para tasks paralelas)
        factory = get_extraction_factory()

        # 2. Determinar tipo de extrator
        file_extension = file_path.suffix.lower()
        extractor_type = FILE_EXTENSION_MAP.get(file_extension)

        if not extractor_type:
            raise ValueError(
                f"Extensão '{file_extension}' não mapeada em FILE_EXTENSION_MAP."
            )

        # 3. (E)xtract - Construir e executar o extrator
        extractor = factory.create_extractor(
            module_name=module_name, extractor_type=extractor_type
        )
        data = extractor.extract(str(file_path))

        # 4. (L)oad - Salvar na Camada Bronze
        output_filename = f"{module_name}_{file_path.stem}.parquet"
        output_path = DATA_BRONZE_DIR / output_filename

        data.to_parquet(output_path, index=False, engine="pyarrow")

        print(f"  -> SUCESSO! {len(data)} linhas salvas em {output_path.name}")
        return {"status": "success", "file": filename, "rows": len(data)}

    except Exception as e:
        print(f"  -> FALHA ao processar {filename}: {e}")
        # Levanta a exceção para que o Prefect saiba que falhou (e pode tentar de novo)
        raise


@task(name="3. Executar Transformação (dbt)")
def run_dbt_transformation():
    """
    Task para disparar o dbt build, transformando
    Bronze -> Silver -> Gold.
    """
    print("\n--- Iniciando transformação dbt ---")
    try:
        # Executa o 'dbt build' dentro do diretório do projeto dbt
        result = subprocess.run(
            ["dbt", "build"],
            cwd=DBT_PROJECT_DIR,  # <--- Importante: define o diretório de trabalho
            check=True,
            capture_output=True,
            text=True,
        )
        print("Saída do dbt:\n", result.stdout)
        print("--- Transformação dbt concluída com sucesso ---")
        return {"status": "success"}
    except subprocess.CalledProcessError as e:
        print("--- FALHA NA TRANSFORMAÇÃO DBT ---")
        print("Erro:\n", e.stderr)
        raise
    except FileNotFoundError:
        print("--- FALHA NA TRANSFORMAÇÃO DBT ---")
        print("Erro: 'dbt' não encontrado. Está instalado e no PATH?")
        raise


# --- 5. O Flow (O Orquestrador) ---
# Esta função substitui o nosso 'main()'
@flow(name="Pipeline ELT Financeiro (Bronze & dbt)")
def financial_elt_flow():
    """
    Orquestra o pipeline completo:
    1. Descobre os ficheiros a processar.
    2. Executa a extração e carga (EL) para a camada Bronze EM PARALELO.
    3. Após SUCESSO, dispara a transformação (T) com dbt.
    """
    print("Iniciando o Flow 'Pipeline ELT Financeiro'...")

    # Etapa 1: Descobrir ficheiros
    tasks_to_process = generate_task_list()

    if not tasks_to_process:
        print("Nenhum ficheiro novo encontrado. Flow concluído.")
        return

    # Etapa 2: Processar ficheiros
    # .map() executa a 'process_file_task' para CADA item na lista.
    # O Prefect irá executá-los EM PARALELO (conforme os limites do seu worker)
    extraction_results = process_file_task.map(tasks_to_process)

    # Etapa 3: Executar dbt
    # Esta task só começa DEPOIS que todas as tasks de 'extraction_results'
    # terminarem com sucesso (gestão de dependências!)
    dbt_results = run_dbt_transformation(wait_for=[extraction_results])

    print("--- Flow 'Pipeline ELT Financeiro' concluído ---")
    return dbt_results


# --- Ponto de Entrada para Execução ---
if __name__ == "__main__":
    # Você pode executar isto localmente para testar:
    # python -m src.flows.run_prefect_flow
    financial_elt_flow()

    # Para produção, você "serviria" este flow com o Prefect:
    # prefect server start
    # prefect deploy
