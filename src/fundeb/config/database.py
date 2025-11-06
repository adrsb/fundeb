"""
Configurações centralizadas do projeto.
"""

from dataclasses import dataclass
import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()


@dataclass(frozen=True)
class DatabaseConfig:
    """Configuração de banco de dados."""

    HOST: str = os.getenv("DB_HOST", "localhost")
    PORT: int = int(os.getenv("DB_PORT", "5432"))
    DATABASE: str = os.getenv("DB_NAME", "FUNDEB")
    USER: str = os.getenv("DB_USER", "duckdb")
    PASSWORD: str = os.getenv("DB_PASSWORD", "")

    @property
    def connection_string(self) -> str:
        """Retorna string de conexão."""
        return f"postgresql://{self.USER}:{self.PASSWORD}@{self.HOST}:{self.PORT}/{self.DATABASE}"


# ============================================================================
# INSTÂNCIAS GLOBAIS (usar em todo o projeto)
# ============================================================================
database = DatabaseConfig()


# ============================================================================
# EXPORT
# ============================================================================
__all__ = [
    "DatabaseConfig",
    "database",
]

# ============================================================================
# MAIN (execução direta do script)
# ============================================================================
if __name__ == "__main__":
    print(f"HOST: {database.HOST}")
    print(f"PORT: {database.PORT}")
    print(f"DATABASE: {database.DATABASE}")
    print(f"USER: {database.USER}")
