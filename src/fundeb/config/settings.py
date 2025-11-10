from pathlib import Path
from dotenv import load_dotenv

# Carrega variáveis de um ficheiro .env na raiz do projeto (se existir)
load_dotenv()

# --- 1. Caminhos Principais (Core Paths) ---
PROJECT_ROOT = Path(__file__).resolve().parents[3]

# --- 2. Caminhos da Arquitetura Medallion (Data Lake) ---

# O diretório principal que armazena todos os dados do "lago"
DATA_LAKE_DIR = PROJECT_ROOT / "data"

# Onde os ficheiros originais (CSV, PDF) são colocados para ingestão
DATA_RAW_DIR = DATA_LAKE_DIR / "raw"

# Camada BRONZE: Dados crus, imutáveis, em formato aberto (Parquet)
DATA_BRONZE_DIR = DATA_LAKE_DIR / "bronze"

# Camada SILVER: Dados limpos, validados, unidos
DATA_SILVER_DIR = DATA_LAKE_DIR / "silver"

# Camada GOLD: Dados agregados, prontos para consumo (BI/ML)
DATA_GOLD_DIR = DATA_LAKE_DIR / "gold"


# --- 3. Caminhos de Fontes e Configurações ---

# Caminho para o projeto dbt que fará as transformações
DBT_PROJECT_DIR = PROJECT_ROOT / "dbt_transform"

# Caminho para o projeto dbt que fará as transformações
LOGS_PROJECT_DIR = PROJECT_ROOT / "data" / "logs"

# Caminho para o ficheiro YAML que define OS PARÂMETROS dos extratores
# A factory.py irá importar esta variável para saber qual ficheiro ler.
EXTRACTORS_CONFIG_PATH = PROJECT_ROOT / "src" / "fundeb" / "config" / "extractors.yaml"
# Caminho para o ficheiro YAML que define OS PARÂMETROS dos loggers
LOGGING_CONFIG_PATH = PROJECT_ROOT / "src" / "fundeb" / "config" / "logging.yaml"


# --- 4. Configurações do Data Warehouse (DuckDB) ---

# O ficheiro físico da base de dados DuckDB
# É uma boa prática colocá-lo dentro do data lake
DUCKDB_PATH = DATA_LAKE_DIR / "finance_warehouse.db"


# --- 5. Mapeamentos Estáticos do Pipeline ---

# Mapeia extensões de ficheiro para os 'tipos' de extrator definidos no extractors.yml
# O seu orquestrador (run_pipeline.py) usará isto para decidir
# qual 'extractor_type' pedir à fábrica.
FILE_EXTENSION_MAP = {
    ".csv": "csv",
    ".txt": "csv",  # Ficheiros .txt podem ser tratados como CSV (ex: delimitados por tab)
    ".xlsx": "excel",  # Exemplo de como adicionar suporte a Excel
    ".xls": "excel",
    ".pdf": "pdf",
}


# --- 6. Configurações de Ambiente (Exemplos) ---

# Exemplo de como carregar segredos ou configurações do ambiente
# Use isto para senhas, chaves de API, etc., NUNCA as coloque diretamente aqui.
# MEU_USUARIO_API = os.getenv("MINHA_API_USER")
# MINHA_SENHA_API = os.getenv("MINHA_API_PASSWORD")


# --- 7. Utilitário de Setup ---
# Garante que os diretórios de dados existam quando este módulo for importado
def _create_data_dirs():
    """Cria os diretórios da arquitetura Medallion se não existirem."""
    print("Verificando estrutura de diretórios...")
    for path in [
        DATA_RAW_DIR,
        DATA_BRONZE_DIR,
        DATA_SILVER_DIR,
        DATA_GOLD_DIR,
        LOGS_PROJECT_DIR,
    ]:
        path.mkdir(parents=True, exist_ok=True)


# Executa a criação dos diretórios na primeira vez que settings.py é importado
_create_data_dirs()


# --- 8. Exportação de Configurações ---
class Settings:
    """Classe para agrupar todas as configurações."""

    def __init__(self):
        self.paths = {
            "BASE_DIR": PROJECT_ROOT,
            "DATA_LAKE_DIR": DATA_LAKE_DIR,
            "DATA_RAW_DIR": DATA_RAW_DIR,
            "DATA_BRONZE_DIR": DATA_BRONZE_DIR,
            "DATA_SILVER_DIR": DATA_SILVER_DIR,
            "DATA_GOLD_DIR": DATA_GOLD_DIR,
            "DBT_PROJECT_DIR": DBT_PROJECT_DIR,
            "EXTRACTORS_CONFIG_PATH": EXTRACTORS_CONFIG_PATH,
            "DUCKDB_PATH": DUCKDB_PATH,
        }
        self.file_extension_map = FILE_EXTENSION_MAP

    def to_dict(self):
        """Retorna todas as configurações como um dicionário."""
        return {
            "paths": self.paths,
            "file_extension_map": self.file_extension_map,
        }


# Exporta uma instância global de configurações
settings = Settings()

if __name__ == "__main__":
    print("Configurações do Projeto Fundeb Analysis:")
    for key, value in settings.to_dict().items():
        print(f"{key}: {value}")
