import logging
from typing import Any

import yaml

# 1. IMPORTAR AS DEPENDÊNCIAS DE CONFIGURAÇÃO E ESTRATÉGIAS
from fundeb.config.settings import EXTRACTORS_CONFIG_PATH, LOGGING_CONFIG_PATH
from fundeb.extractors.base_extractor import BaseExtractor
from fundeb.extractors.csv_extractor import CSVExtractor

# from fundeb_analysis.extractors.pdf_extractor import PDFExtractor
# from fundeb_analysis.extractors.excel_extractor import ExcelExtractor

# Carrega a configuração do arquivo YAML de logging
with open(LOGGING_CONFIG_PATH) as file:
    logging_config = yaml.safe_load(file)
    logging.config.dictConfig(logging_config)
    logger = logging.getLogger("my_module")


# 2. O PADRÃO REGISTRY
# ----------------------------------------
EXTRACTOR_REGISTRY: dict[str, BaseExtractor] = {
    "csv": CSVExtractor,
    # "txt": CSVExtractor,
    # "xls": ExcelExtractor,
    # "xlsx": ExcelExtractor,
    # "pdf": PDFExtractor,
}


# 3. O PADRÃO FACTORY (A CLASSE)
# ----------------------------------------
class ExtractionFactory:
    """
    Fábrica que constrói a Estratégia de extração correta
    com base no 'configs' e 'extractor_registry' fornecidos.
    """

    def __init__(
        self,
        config: dict[str, Any],
        registry: dict[str, BaseExtractor],
    ):
        """
        Inicializa a fábrica com as suas dependências (Injeção de Dependência).
        Args:
            configs: O dicionário completo carregado do extractors.yml.
            extractor_registry: O dicionário EXTRACTOR_REGISTRY que mapeia strings para classes.
        """
        self.config = config
        self.registry = registry
        print("ExtractionFactory (Hierárquica) inicializada com sucesso.")

    def create_extractor(self, module_name: str, extractor_type: str) -> BaseExtractor:
        """
        Cria a instância de extrator correta para um módulo e tipo.
        Este é o método de trabalho principal da fábrica.
        """

        # Etapa 1: Encontrar o bloco de configuração do módulo (ex: 'conta_corrente')
        try:
            module_config = self.config[module_name]
        except KeyError as err:
            # Erro claro se o módulo não estiver no YAML
            raise ValueError(
                f"Configuração não encontrada para o módulo: '{module_name}'. "
                f"Verifique se está no {EXTRACTORS_CONFIG_PATH.name}."
            ) from err

        # Etapa 2: Encontrar o bloco de configuração do tipo (ex: 'csv' dentro de 'conta_corrente')
        try:
            type_config = module_config[extractor_type]
        except KeyError as err:
            # Erro claro se o tipo não estiver dentro do módulo no YAML
            raise ValueError(
                f"Tipo de extrator '{extractor_type}' não encontrado para o módulo '{module_name}'. "
                f"Verifique a configuração desse módulo no {EXTRACTORS_CONFIG_PATH.name}."
            ) from err

        # Etapa 3: Encontrar a Classe de Extrator correspondente no nosso Registo
        try:
            ExtractorClass = self.registry[extractor_type]
        except KeyError as err:
            # Erro claro se o tipo (ex: 'pdf') estiver no YAML mas não no REGISTRY
            raise ValueError(
                f"Tipo de extrator desconhecido: '{extractor_type}'. "
                f"Ele está no YAML, mas não foi adicionado ao EXTRACTOR_REGISTRY em factory.py."
            ) from err

        # Etapa 4: Obter os parâmetros (o bloco 'params' no YAML)
        config_params = type_config.get("params", {})

        # Etapa 5: Instanciar e retornar a Estratégia
        # A MÁGICA: Passamos os parâmetros do YAML diretamente para o
        # construtor da classe de extração.
        try:
            return ExtractorClass(config_params=config_params)
        except TypeError as e:
            # Erro comum se o __init__ do extrator não aceitar 'config_params'
            print(f"Erro ao instanciar {ExtractorClass.__name__}: {e}")
            print(
                "Verifique se o __init__ do seu extrator aceita um argumento chamado 'config_params'."
            )
            raise
        except Exception as e:
            print(f"Erro inesperado ao criar o extrator {ExtractorClass.__name__}: {e}")
            raise


# 4. O PADRÃO SINGLETON (A FUNÇÃO PÚBLICA)
# ----------------------------------------

_factory_instance: ExtractionFactory | None = None


def get_extraction_factory() -> ExtractionFactory:
    """
    Função Singleton. Garante que o YAML seja lido e a Fábrica
    seja criada apenas UMA VEZ durante a execução do programa.

    Retorna:
        A instância única da ExtractionFactory.
    """
    # Valida se a instância já foi criada
    global _factory_instance
    if _factory_instance is not None:
        return _factory_instance

    # --- Primeira execução (Caso instância for None) ---
    # 1. Carregar a configuração do ficheiro YAML
    logger.debug("Criando nova instância da ExtractionFactory (Singleton)...")
    try:
        # Usa o caminho importado de settings.py
        with open(EXTRACTORS_CONFIG_PATH) as f:
            config_data = yaml.safe_load(f)
        logger.debug(
            f"Configuração de extrator carregada de {EXTRACTORS_CONFIG_PATH.name}"
        )
    except Exception as e:
        msg = f"Erro inesperado ao carregar a configuração: {e}"
        logger.debug(msg)
        raise

    # 2. Instanciar a Fábrica, injetando as dependências
    logger.debug("Criando nova instância da ExtractionFactory (Singleton)...")
    _factory_instance = ExtractionFactory(
        config=config_data,  # O dicionário carregado do YAML
        registry=EXTRACTOR_REGISTRY,  # O dicionário de classes
    )

    # 3. Retornar a nova instância
    return _factory_instance


# --- 5. BLOCO DE TESTE (SMOKE TEST) ---
if __name__ == "__main__":
    ...
