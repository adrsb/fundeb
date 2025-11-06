"""
Extrator para arquivos CSV de conta corrente
"""

import logging
from pathlib import Path
from typing import Any, Dict

import pandas as pd

from fundeb_analysis.extractors.base_extractor import BaseExtractor


class CSVExtractor(BaseExtractor):
    """Extrator para arquivos CSV de conta corrente"""

    def __init__(
        self,
        config_params: Dict[str, Any],
    ):
        super().__init__()
        self.read_kwargs = config_params
        self.logger.info(f"CSVExtractor inicializado com params: {self.read_kwargs}]")

    def extract(self, file_path) -> pd.DataFrame:
        """Extrai dados do CSV"""
        logging.info(f"Iniciando extração: {file_path}...")

        try:
            df = pd.read_csv(file_path, **self.read_kwargs)

            logging.info(
                f"Arquivo extraído com sucesso! {len(df)} linhas, {len(df.columns)} colunas"
            )
            return df

        except Exception as e:
            logging.error(f"Erro ao extrair CSV {file_path}: {e}")
            raise ValueError(f"Falha na extração do CSV: {e}")


# --- O BLOCO DE TESTE (SMOKE TEST) ---
if __name__ == "__main__":
    import tempfile
    from pathlib import Path
    import sys

    print("\n--- EXECUTANDO SMOKE TEST: CSVExtractor ---")

    # 1. Definir um CSV e uma configuração de teste
    # Usaremos um CSV separado por PONTO-E-VÍRGULA para tornar o teste mais real
    DUMMY_CSV_CONTENT = "id;nome;valor\n1;produto_a;10.50\n2;produto_b;20.00"

    # A configuração para LER este CSV
    DUMMY_CONFIG = {"sep": ";", "header": 0, "decimal": "."}

    # 2. Criar um diretório e ficheiro temporários
    # O 'with' garante que tudo seja apagado no final, mesmo se der erro
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir) / "smoke_test.csv"

            with open(tmp_path, "w", encoding="utf-8") as f:
                f.write(DUMMY_CSV_CONTENT)
            print(f"Arquivo de teste temporário criado em: {tmp_path}")

            # --- [TESTE 1: Instanciação] ---
            print("\n[TESTE 1: Instanciar o extrator]")
            extractor = CSVExtractor(config_params=DUMMY_CONFIG)
            print(f"  -> SUCESSO. Extrator criado: {type(extractor)}")
            assert extractor.read_kwargs == DUMMY_CONFIG

            # --- [TESTE 2: Execução do .extract()] ---
            print("\n[TESTE 2: Executar o método .extract()]")
            df = extractor.extract(str(tmp_path))
            print("  -> SUCESSO. Método .extract() executado.")

            # --- [TESTE 3: Validação do Resultado] ---
            print("\n[TESTE 3: Validar o DataFrame resultante]")

            # É um DataFrame?
            assert isinstance(df, pd.DataFrame), "O resultado NÃO é um DataFrame!"
            print("  -> É um DataFrame.")

            # Tem o número correto de linhas?
            assert len(df) == 2, f"Esperava 2 linhas, obteve {len(df)}"
            print(f"  -> Número de linhas correto (2).")

            # Tem as colunas corretas?
            expected_cols = ["id", "nome", "valor"]
            assert list(df.columns) == expected_cols, (
                f"Colunas erradas: {list(df.columns)}"
            )
            print(f"  -> Colunas corretas ({expected_cols}).")

            # O tipo de dado foi lido corretamente? (float)
            assert df["valor"].dtype == "float64", (
                f"Tipo da coluna 'valor' não é float: {df['valor'].dtype}"
            )
            print("  -> Tipo de dado (float) lido corretamente.")

    except Exception as e:
        print(f"\n--- FALHA NO SMOKE TEST ---")
        print(f"ERRO: {e}")
        sys.exit(1)  # Sair com código de erro

    print("\n--- SMOKE TEST CONCLUÍDO COM SUCESSO ---")
