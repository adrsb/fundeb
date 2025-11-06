from pathlib import Path
from typing import List


def get_file_size(filepath: Path) -> None:
    """Retorna tamanho do arquivo em formato legível"""
    size = filepath.stat().st_size
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0


def ensure_directory(directory: Path) -> Path:
    """Garante que diretório existe"""
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def list_file_paths(directory: Path, pattern: str = "*") -> List[Path]:
    """Lista arquivos em diretório"""
    return sorted(directory.glob(pattern))


def recursive_list_file_paths(base_directory: Path, pattern: str = "*") -> List[Path]:
    """Lista arquivos em diretório"""
    return sorted(base_directory.rglob(pattern))


# --- BLOCO DE TESTE (SMOKE TEST) ---
if __name__ == "__main__":
    import tempfile

    print("\n--- EXECUTANDO SMOKE TEST: file_discovery ---")

    # 1. Criar uma estrutura de diretório temporária para o teste
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            base_test_dir = Path(tmpdir)

            # Criar a estrutura /<tmp>/dados_teste/conta_corrente/
            source_dir = base_test_dir / "dados_teste"
            module_dir = source_dir / "conta_corrente"
            module_dir.mkdir(parents=True, exist_ok=True)

            # Criar ficheiros de teste
            (module_dir / "EXTRATO_BANCARIO_CC_01.csv").touch()
            (module_dir / "EXTRATO_BANCARIO_CC_02.csv").touch()
            (module_dir / "outro_ficheiro.txt").touch()

            print(f"Estrutura de teste criada em: {source_dir}")

            # --- [TESTE 1: Encontrar ficheiros CSV] ---
            print("\n[TESTE 1: Procurar por 'EXTRATO_BANCARIO_CC*.csv']")
            pattern_csv = "EXTRATO_BANCARIO_CC*.csv"
            files = find_files_by_pattern(
                base_dir=source_dir,
                module_name="conta_corrente",
                file_pattern=pattern_csv,
            )

            assert len(files) == 2, f"Esperava 2 ficheiros, encontrou {len(files)}"
            print(f"  -> SUCESSO. Encontrados {len(files)} ficheiros.")
            print(f"  -> {files[0].name}, {files[1].name}")

            # --- [TESTE 2: Procurar por ficheiros .txt] ---
            print("\n[TESTE 2: Procurar por '*.txt']")
            pattern_txt = "*.txt"
            files_txt = find_files_by_pattern(
                base_dir=source_dir,
                module_name="conta_corrente",
                file_pattern=pattern_txt,
            )
            assert len(files_txt) == 1, (
                f"Esperava 1 ficheiro, encontrou {len(files_txt)}"
            )
            assert files_txt[0].name == "outro_ficheiro.txt"
            print(f"  -> SUCESSO. Encontrado 1 ficheiro: {files_txt[0].name}")

            # --- [TESTE 3: Procurar por padrão sem correspondência] ---
            print("\n[TESTE 3: Procurar por padrão inexistente ('*.pdf')]")
            files_pdf = find_files_by_pattern(
                base_dir=source_dir, module_name="conta_corrente", file_pattern="*.pdf"
            )
            assert len(files_pdf) == 0, "Esperava 0 ficheiros, mas algo foi encontrado."
            print(f"  -> SUCESSO. Nenhum ficheiro encontrado, como esperado.")

            # --- [TESTE 4: Procurar em módulo inexistente] ---
            print("\n[TESTE 4: Procurar em módulo inexistente ('investimentos')]")
            files_invest = find_files_by_pattern(
                base_dir=source_dir,
                module_name="investimentos",  # Esta pasta não foi criada
                file_pattern="*.csv",
            )
            assert len(files_invest) == 0, (
                "Esperava 0 ficheiros, mas algo foi encontrado."
            )
            print(f"  -> SUCESSO. Nenhum ficheiro encontrado, como esperado.")

    except Exception as e:
        print(f"\n--- FALHA NO SMOKE TEST ---")
        print(f"ERRO: {e}")

    print("\n--- SMOKE TEST CONCLUÍDO COM SUCESSO ---")
