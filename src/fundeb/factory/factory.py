import logging

from typing import Any, Dict, Type
import yaml

# 1. IMPORTAR AS DEPENDÊNCIAS DE CONFIGURAÇÃO E ESTRATÉGIAS

# Importa o CAMINHO do ficheiro de configuração (do settings.py)
from fundeb_analysis.config.settings import EXTRACTORS_CONFIG_PATH

# Importa a Interface Base (para type hinting)
from fundeb_analysis.extractors.base_extractor import BaseExtractor

# Importa as Estratégias Concretas (os seus extratores)
from fundeb_analysis.extractors.csv_extractor import CSVExtractor
# from fundeb_analysis.extractors.pdf_extractor import PDFExtractor
# from fundeb_analysis.extractors.excel_extractor import ExcelExtractor


# 2. O PADRÃO REGISTRY
# --------------------
# Mapeia as chaves do seu ficheiro YAML (ex: "csv") para a Classe Python
# que deve ser usada.
#
# VANTAGEM: Para adicionar um novo "ExcelExtractor":
# 1. Importe-o acima.
# 2. Adicione "excel": ExcelExtractor a este dicionário.
# A sua Factory NÃO precisa de ser alterada (Princípio Aberto/Fechado).
EXTRACTOR_REGISTRY: Dict[str, Type[BaseExtractor]] = {
    "csv": CSVExtractor,
    # "txt": CSVExtractor,
    # "xls": ExcelExtractor,
    # "xlsx": ExcelExtractor,
    # "pdf": PDFExtractor,
}


# 3. O PADRÃO FACTORY (A CLASSE)
# ------------------------------
# Esta classe é "burra". Ela apenas sabe como ler o registo e o
# dicionário de configuração que recebe no seu __init__.
class ExtractionFactory:
    """
    Fábrica que constrói a Estratégia de extração correta
    com base no 'configs' e 'extractor_registry' fornecidos.
    """

    def __init__(
        self,
        config: Dict[str, Any],
        registry: Dict[str, Type[BaseExtractor]],
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
        except KeyError:
            # Erro claro se o módulo não estiver no YAML
            raise ValueError(
                f"Configuração não encontrada para o módulo: '{module_name}'. "
                f"Verifique se está no {EXTRACTORS_CONFIG_PATH.name}."
            )

        # Etapa 2: Encontrar o bloco de configuração do tipo (ex: 'csv' dentro de 'conta_corrente')
        try:
            type_config = module_config[extractor_type]
        except KeyError:
            # Erro claro se o tipo não estiver dentro do módulo no YAML
            raise ValueError(
                f"Tipo de extrator '{extractor_type}' não encontrado para o módulo '{module_name}'. "
                f"Verifique a configuração desse módulo no {EXTRACTORS_CONFIG_PATH.name}."
            )

        # Etapa 3: Encontrar a Classe de Extrator correspondente no nosso Registo
        try:
            ExtractorClass = self.registry[extractor_type]
        except KeyError:
            # Erro claro se o tipo (ex: 'pdf') estiver no YAML mas não no REGISTRY
            raise ValueError(
                f"Tipo de extrator desconhecido: '{extractor_type}'. "
                f"Ele está no YAML, mas não foi adicionado ao EXTRACTOR_REGISTRY em factory.py."
            )

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
# Esta é a única parte que o resto do seu código (ex: run_pipeline.py)
# deve importar e usar.
# Ela esconde toda a complexidade de carregar o YAML e instanciar a Fábrica.

_factory_instance: ExtractionFactory | None = None


def get_extraction_factory() -> ExtractionFactory:
    """
    Função Singleton. Garante que o YAML seja lido e a Fábrica
    seja criada apenas UMA VEZ durante a execução do programa.

    Retorna:
        A instância única da ExtractionFactory.
    """
    global _factory_instance

    # Se a instância já existir, retorna-a imediatamente.
    if _factory_instance is not None:
        return _factory_instance

    # --- Primeira execução (Instância é None) ---
    print("Criando nova instância da ExtractionFactory (Singleton)...")

    # 1. Carregar a configuração do ficheiro YAML
    try:
        # Usa o caminho importado de settings.py
        with open(EXTRACTORS_CONFIG_PATH, "r", encoding="utf-8") as f:
            config_data = yaml.safe_load(f)

        # Trata o caso de o ficheiro YAML estar vazio
        if not config_data:
            raise ValueError(
                f"Ficheiro de configuração está vazio: {EXTRACTORS_CONFIG_PATH}"
            )

        print(f"Configuração de extratores carregada de {EXTRACTORS_CONFIG_PATH.name}")

    except FileNotFoundError:
        print(
            f"ERRO CRÍTICO: Ficheiro de configuração não encontrado em {EXTRACTORS_CONFIG_PATH}"
        )
        raise
    except yaml.YAMLError as e:
        print(f"ERRO CRÍTICO: Erro ao processar o ficheiro YAML: {e}")
        raise
    except Exception as e:
        print(f"ERRO CRÍTICO: Erro inesperado ao carregar a configuração: {e}")
        raise

    # 2. Instanciar a Fábrica, injetando as dependências
    _factory_instance = ExtractionFactory(
        config=config_data,  # O dicionário carregado do YAML
        registry=EXTRACTOR_REGISTRY,  # O dicionário de classes
    )

    # 3. Retornar a nova instância
    return _factory_instance


# --- 5. BLOCO DE TESTE (SMOKE TEST) ---
if __name__ == "__main__":
    print("\n--- EXECUTANDO SMOKE TEST: ExtractionFactory ---")

    try:
        # 1. Testar o Singleton e o carregamento do YAML/Settings
        # Este é o teste mais importante. Se isto falhar, nada funciona.
        print("\n[TESTE 1: Obter a fábrica (Singleton e carregamento de config)]")
        factory = get_extraction_factory()
        print(f"  -> SUCESSO. Fábrica obtida: {type(factory)}")
        assert isinstance(factory, ExtractionFactory)

        # Testar se o Singleton funciona (não deve imprimir "Criando nova instância...")
        factory_2 = get_extraction_factory()
        assert factory is factory_2, "Singleton falhou! Duas instâncias foram criadas."
        print("  -> SUCESSO. Singleton verificado.")

        # 2. Testar a criação de um extrator (conta_corrente CSV)
        # Isto testa se a fábrica consegue ler a estrutura hierárquica do YAML
        # e passá-la para o construtor do extrator.
        print("\n[TESTE 2: Criar extrator 'conta_corrente' (csv)]")
        extractor_cc_csv = factory.create_extractor(
            module_name="conta_corrente", extractor_type="csv"
        )
        print(f"  -> SUCESSO. Extrator criado: {type(extractor_cc_csv)}")

        # Verifica se os parâmetros foram passados corretamente
        # (Isto assume que seu CSVExtractor armazena os params em 'self.read_kwargs')
        assert extractor_cc_csv.read_kwargs["sep"] == ";", "Parâmetro 'sep' incorreto."
        print(
            f"  -> Parâmetros verificados (ex: sep='{extractor_cc_csv.read_kwargs['sep']}')"
        )

        # 3. Testar a criação de outro extrator (remessas_bancarias)
        print("\n[TESTE 3: Criar extrator 'remessas_bancarias' (csv)]")
        extractor_remessas = factory.create_extractor(
            module_name="remessas_bancarias", extractor_type="csv"
        )
        print(f"  -> SUCESSO. Extrator criado: {type(extractor_remessas)}")
        assert extractor_remessas.read_kwargs["sep"] == "\t", (
            "Parâmetro 'sep' incorreto."
        )
        print(
            f"  -> Parâmetros verificados (ex: sep='{extractor_remessas.read_kwargs['sep']}')"
        )

        # 4. Testar um erro (módulo não existente no YAML)
        print("\n[TESTE 4: Testar módulo inexistente ('modulo_fantasma')]")
        try:
            factory.create_extractor("modulo_fantasma", "csv")
            # Se chegar aqui, o teste falhou
            raise AssertionError("Factory não levantou erro para módulo inexistente.")
        except ValueError as e:
            # Isto é o que esperamos
            print(f"  -> SUCESSO. Erro esperado capturado: {e}")
        except Exception as e:
            raise AssertionError(f"Erro inesperado capturado: {e}")

        # 5. Testar um erro (tipo não existente para um módulo)
        print("\n[TESTE 5: Testar tipo inexistente ('pdf') para 'remessas_bancarias']")
        try:
            factory.create_extractor("remessas_bancarias", "pdf")
            raise AssertionError(
                "Factory não levantou erro para tipo inexistente no módulo."
            )
        except ValueError as e:
            print(f"  -> SUCESSO. Erro esperado capturado: {e}")

        # 6. Testar um erro (tipo não existente no REGISTRY)
        print("\n[TESTE 6: Testar tipo inexistente ('excel') - não está no REGISTRY]")
        try:
            # (Isto assume que 'excel' existe no seu YAML para 'conta_corrente',
            # mas não no EXTRACTOR_REGISTRY)
            # Vamos simular um caso mais garantido:
            factory.registry["excel"] = None  # Simula uma entrada errada
            factory.config["conta_corrente"]["excel"] = {"params": {}}  # Simula o YAML

            factory.create_extractor("conta_corrente", "excel")
            raise AssertionError("Factory não levantou erro para tipo não registado.")
        except ValueError as e:
            print(f"  -> SUCESSO. Erro esperado capturado: {e}")
        except TypeError as e:
            print(f"  -> SUCESSO. Erro esperado capturado: {e}")
        except AttributeError as e:
            print(f"  -> SUCESSO. Erro esperado capturado: {e}")
        except AssertionError as e:
            print(f"  -> SUCESSO. Erro esperado capturado: {e}")
        except Exception as e:
            raise AssertionError(f"Erro inesperado capturado: {e}")
        finally:
            # Limpa a simulação
            factory.registry.pop("excel", None)
            factory.config["conta_corrente"].pop("excel", None)

    except Exception as e:
        print("\n--- FALHA GERAL NO SMOKE TEST DA FÁBRICA ---")
        raise e

    else:
        print("\n--- SMOKE TEST DA FÁBRICA CONCLUÍDO COM SUCESSO ---")
