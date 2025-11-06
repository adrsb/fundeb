import pandas as pd
from pathlib import Path
from typing import List, Dict, Any

# --- 1. Importar os nossos Módulos Internos ---

# A Fábrica Singleton para construir os nossos extratores
from fundeb_analysis.factory.factory import get_extraction_factory

# Os caminhos (onde ler, onde salvar) e o mapa de extensões
from fundeb_analysis.config.settings import (
    DATA_SOURCE_DIR,  # Diretório de onde lemos (ex: .../dados_fonte)
    DATA_BRONZE_DIR,  # Diretório onde salvamos (ex: .../data/bronze)
    FILE_EXTENSION_MAP,  # O mapa {".csv": "csv", ".pdf": "pdf", ...}
)

# A nossa função auxiliar para descobrir ficheiros
from fundeb_analysis.utils.file_discovery import find_files_by_pattern


# --- 2. Definição das Regras de Descoberta ---
# Define O QUE o pipeline deve procurar e a que módulo pertence.
# O `module_base` deve corresponder a uma chave no seu `extractors.yml`.
# O `pattern` é um padrão "glob" para encontrar ficheiros.
DISCOVERY_RULES = [
    {"module_base": "conta_corrente", "pattern": "EXTRATO_BANCARIO_CC*.csv"},
    {
        "module_base": "conta_corrente",
        "pattern": "EXTRATO_CC*.pdf",
        # (Isto só funcionará se tiver um PDFExtractor e o registar na factory)
    },
    {"module_base": "conta_investimentos", "pattern": "INVEST_MES_*.csv"},
    {
        "module_base": "remessas_bancarias",
        "pattern": "*.txt",  # Exemplo para ficheiros .txt
    },
]


def generate_task_list() -> List[Dict[str, Any]]:
    """
    Gera dinamicamente a lista de tarefas de ficheiros a processar
    usando as DISCOVERY_RULES e o utilitário find_files_by_pattern.

    Cada tarefa é um dicionário contendo o módulo e o caminho completo do ficheiro.
    """
    print("Iniciando descoberta dinâmica de ficheiros...")
    tasks_to_run = []

    for rule in DISCOVERY_RULES:
        module = rule["module_base"]
        pattern = rule["pattern"]

        # Chama a nossa função utilitária
        # Procura em DATA_SOURCE_DIR / <module_name> / <pattern>
        files = find_files_by_pattern(
            base_dir=DATA_SOURCE_DIR, module_name=module, file_pattern=pattern
        )

        for file_path in files:
            # Cria uma tarefa para cada ficheiro encontrado
            task = {
                "module_base": module,
                "file_path": file_path,  # O objeto Path completo
                "filename": file_path.name,
            }
            tasks_to_run.append(task)

    print(
        f"Descoberta concluída. {len(tasks_to_run)} arquivos encontrados para processamento."
    )
    return tasks_to_run


def main():
    """
    Ponto de entrada principal do pipeline de extração (Orquestrador).
    Executa o processo de Extract-Load (EL) para a camada Bronze.
    """
    print("Iniciando pipeline de extração (Camada Bronze)...")

    # --- Etapa 1: Inicializar a Fábrica ---
    try:
        # get_extraction_factory() é um Singleton.
        # Na primeira chamada, ele lê o YAML e cria a instância.
        factory = get_extraction_factory()
    except Exception as e:
        print(f"ERRO CRÍTICO: Falha ao inicializar a ExtractionFactory: {e}")
        print("Verifique os ficheiros settings.py e extractors.yml. Encerrando.")
        return  # Não podemos continuar se a fábrica falhar

    # --- Etapa 2: Gerar a Lista de Tarefas ---
    TASKS = generate_task_list()

    if not TASKS:
        print("Nenhum ficheiro para processar. Encerrando.")
        return

    print(f"\n--- Iniciando processamento de {len(TASKS)} tarefas ---")

    successful_tasks = 0
    failed_tasks = 0

    # --- Etapa 3: Executar cada Tarefa (Loop Principal) ---
    for task in TASKS:
        module_name = task["module_base"]
        file_path = task["file_path"]
        filename = task["filename"]

        print(f"\n--- Processando Tarefa ---")
        print(f"  Módulo:    {module_name}")
        print(f"  Arquivo:   {filename}")

        try:
            # --- Lógica de Orquestração ---
            # 1. Determinar o tipo de extrator a partir da extensão do ficheiro
            file_extension = file_path.suffix.lower()  # ex: ".csv"

            # 2. Usar o mapa de settings.py para encontrar o tipo (ex: "csv")
            extractor_type = FILE_EXTENSION_MAP.get(file_extension)

            if not extractor_type:
                # Se for um tipo de ficheiro que não conhecemos (ex: .zip, .md)
                print(
                    f"  AVISO: Extensão '{file_extension}' não mapeada em FILE_EXTENSION_MAP. Pulando."
                )
                failed_tasks += 1
                continue

            # --- Etapa E (Extract) ---
            # 3. Pedir à Fábrica para construir o Extrator
            # A fábrica encontra os parâmetros corretos no YAML
            extractor = factory.create_extractor(
                module_name=module_name, extractor_type=extractor_type
            )

            # 4. Executar a Estratégia (Extração)
            # O orquestrador não sabe *como* extrair, apenas chama .extract()
            data = extractor.extract(str(file_path))  # .extract() espera uma string

            # --- Etapa L (Load) ---
            # 5. Salvar os dados na Camada Bronze (como Parquet)
            # Criamos um nome de ficheiro único para a camada bronze
            output_filename = f"{module_name}_{file_path.stem}.parquet"
            output_path = DATA_BRONZE_DIR / output_filename

            data.to_parquet(output_path, index=False, engine="pyarrow")

            print(f"  SUCESSO! {len(data)} linhas extraídas.")
            print(f"  Salvo na camada Bronze em: {output_path.name}")
            successful_tasks += 1

        except ValueError as ve:
            # Erro de configuração (ex: "pdf" não está no YAML para "conta_corrente")
            print(f"  FALHA DE CONFIGURAÇÃO: {ve}")
            failed_tasks += 1
        except FileNotFoundError:
            # Ficheiro foi descoberto mas não encontrado durante a extração
            print(
                f"  FALHA DE ARQUIVO: Ficheiro de origem não encontrado em {file_path}"
            )
            failed_tasks += 1
        except pd.errors.EmptyDataError:
            # Erro comum do Pandas se o CSV estiver vazio
            print(f"  FALHA DE DADOS: O ficheiro está vazio. {filename}")
            failed_tasks += 1
        except Exception as e:
            # Outros erros (ex: erro de parsing do Pandas, permissões de escrita)
            print(f"  FALHA INESPERADA na extração: {e}")
            failed_tasks += 1

    # --- Etapa 4: Resumo Final ---
    print("\n--- Pipeline de extração concluído ---")
    print(f"  Tarefas bem-sucedidas: {successful_tasks}")
    print(f"  Tarefas falhadas:      {failed_tasks}")


# --- 5. Ponto de Entrada para Execução ---
if __name__ == "__main__":
    # Este ficheiro foi desenhado para ser executado como um módulo
    # a partir da raiz do projeto, para que as importações 'src.' funcionem.
    #
    # No seu terminal, a partir da pasta 'projeto_financeiro/', execute:
    # python -m src.flows.run_pipeline
    #
    main()
