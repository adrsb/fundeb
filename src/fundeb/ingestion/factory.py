# 1. IMPORTAR AS DEPENDÊNCIAS DE CONFIGURAÇÃO E ESTRATÉGIAS
from pathlib import Path

from fundeb.ingestion.base_data_loader import BaseDataLoader
from fundeb.ingestion.csv_loader import CsvLoader
from fundeb.config.settings import settings

# from fundeb_analysis.extractors.pdf_extractor import PDFExtractor
# from fundeb_analysis.extractors.excel_extractor import ExcelExtractor


logger = settings.get_logger()

# 1. O PADRÃO DE REGISTO DE EXTRATORES
# ----------------------------------------
EXTRACTORS_MAP: dict[str, type[BaseDataLoader]] = {
    "csv": CsvLoader,
    "txt": CsvLoader,
    # "xls": xlsExtractor,
    # "xlsx": xlsxExtractor,
    # "pdf": PDFExtractor,
}


# 2. O PADRÃO FACTORY (A CLASSE)
# ----------------------------------------
class ExtractionFactory:
    """
    Fábrica que constrói a Estratégia de extração correta
    com base no 'configs' e 'extractor_registry' fornecidos.
    """

    def __init__(
        self,
        configs_path: Path,
        extractors_map: dict[str, type[BaseDataLoader]],
    ) -> None:
        """
        Inicializa a fábrica com as suas dependências (Injeção de Dependência).
        Args:
            configs_path: O dicionário completo carregado do extractors.yml.
            extractors_map: O dicionário EXTRACTOR_REGISTRY que mapeia strings para classes.
        """
        logger.debug("Iniciando Loader Factory...")
        self.configs_path = configs_path
        self.extractors_map = extractors_map
        logger.debug("Iniciando Loader Factory... Concluída.")

    def get_extractors_map(self) -> dict[str, type[BaseDataLoader]]:
        """
        Retorna o dicionário de tipos de extratores registrados.
        Útil para depuração e inspeção.
        """
        logger.debug("Inspecionando o mapeamento de extratores...")
        for ext, extractor_cls in self.extractors_map.items():
            logger.info(f"Extensão: {ext} => Extrator: {extractor_cls.__name__}")
        logger.debug("Inspeção do mapeamento de extratores... Concluído.")
        return self.extractors_map

    def create_extractor(self, module_name: str, file_extension: str) -> BaseDataLoader:
        """
        Cria a instância de extrator correta para um módulo e tipo.
        Este é o método de trabalho principal da fábrica.
        """

        # Etapa 1: Encontrar a Classe de Extrator correspondente a extensão do ficheiro
        try:
            logger.debug(
                "Buscando a Classe de Extrator correspondente à extensão do ficheiro..."
            )
            ExtractorClass = self.extractors_map[file_extension]
            logger.info(f"Classe de Extrator: {ExtractorClass.__name__}")
            logger.debug(
                "Busca da Classe de Extrator correspondente à extensão do ficheiro... Concluído."
            )
        except Exception as e:
            msg = f"Erro inesperado ao tentar encontrar a Classe de Extrator correspondente a extensão do ficheiro: {e}"
            logger.exception(msg)
            raise e

        # Etapa 2: Instanciar a Estratégia
        try:
            ExtractorClass = ExtractorClass(self.configs_path)
        except Exception as e:
            msg = f"Erro inesperado ao carregar a Estratégia: {e}"
            logger.exception(msg)
            raise e

        return ExtractorClass


def get_extraction_factory() -> ExtractionFactory:
    """
    Função Singleton. Garante que o YAML seja lido e a Fábrica
    seja criada apenas UMA VEZ durante a execução do programa.

    Retorna:
        A instância única da ExtractionFactory.
    """

    # --- Primeira execução (Caso instância for None) ---
    # 1. Instanciar a Fábrica, injetando as dependências
    print("#" + "-" * 88)
    _factory_instance = ExtractionFactory(
        configs_path=settings.extractors_config_path,  # O caminho do arquivo YAML de configurações dos extratores
        extractors_map=EXTRACTORS_MAP,  # O mapeamento de classes de extratores por extensão
    )
    print("#" + "-" * 88)

    # 2. Inspecionar o mapeamento de extratores
    print("#" + "-" * 88)
    _factory_instance.get_extractors_map()
    print("#" + "-" * 88)

    return _factory_instance


# --- 5. BLOCO DE TESTE (SMOKE TEST) ---
if __name__ == "__main__":
    factory_instance = get_extraction_factory()

    # 3. Testar a criação de um extrator (ex: 'conta_corrente' + 'csv')
    print("#" + "-" * 88)
    extractor_instance = factory_instance.create_extractor(
        module_name="conta_corrente", file_extension="csv"
    )
    print("#" + "-" * 88)

    print("#" + "-" * 88)
    file_path = (
        r"C:\Users\adrsb\OneDrive\Documentos\Projects\FundebProject\data\raw"
        r"\external\bb\conta_corrente\csv\EXTRATO_BANCARIO_CC_AP_MACAPA_2025_01.csv"
    )
    df = extractor_instance.run_flow(
        file_path,
        source="external",
        origin="bb",
        module="conta_corrente",
        file_extension="csv",
    )
    print("#" + "-" * 88)

    display(df.head())  # type: ignore # noqa: F821
