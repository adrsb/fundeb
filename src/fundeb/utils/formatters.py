from datetime import datetime, timedelta

def parse_date(date_str: str, fmt: str = "%d/%m/%Y") -> datetime:
    """
    Converte string para datetime.
    """
    return datetime.strptime(date_str, fmt)

def now_str(fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Retorna a data/hora atual como string formatada.
    """
    return datetime.now().strftime(fmt)

def month_range(start: datetime, end: datetime):
    """
    Gera lista de meses entre duas datas.
    """
    current = start
    while current <= end:
        yield current
        current += timedelta(days=30)

def format_currency(value: float, symbol: str = "R$") -> str:
    """
    Formata um número como valor monetário.
    """
    return f"{symbol} {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def format_percentage(value: float, decimals: int = 2) -> str:
    """
    Formata um número como porcentagem.
    """
    return f"{value:.{decimals}%}"
