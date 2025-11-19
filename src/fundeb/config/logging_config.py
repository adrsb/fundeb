# core/logging_config.py
import sys
from loguru import logger
from fundeb.config.settings import get_settings

settings = get_settings()


def configure_logging():
    # 1. Remove o handler padrão (que joga tudo no stderr)
    logger.remove()

    # 2. Adiciona Log no Console (Colorido e conciso)
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="DEBUG",
    )

    # 3. Adiciona Log em Arquivo (Rotação e Retenção para Engenharia de Dados)
    # rotation="10 MB": Cria novo arquivo quando atingir 10MB
    # retention="10 days": Apaga logs mais velhos que 10 dias
    # compression="zip": Comprime logs antigos para economizar espaço
    log_file = settings.logs_dir / "logs.log"

    logger.add(
        log_file,
        rotation="1 MB",
        retention="1 days",
        compression="zip",
        level="DEBUG",  # No arquivo guardamos mais detalhes
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    )


if __name__ == "__main__":
    logger.debug("Configurando logging...")
    configure_logging()
    logger.debug("Configurando logging... Concluído.")
    logger.info(f"Logs serão salvos em: {settings.logs_dir}")
