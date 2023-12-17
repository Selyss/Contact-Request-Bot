from datetime import datetime


def get_date() -> str:
    """m/d/y"""
    return datetime.now().strftime("%m/%d/%Y")


def get_time() -> str:
    """h:m (A/P)M"""
    return datetime.now().strftime("%-I:%M %p")


def format_footer(id: int) -> str:
    """{ID} • {DATE} • {TIME}"""
    return f"{id} • {get_date()} • {get_time()}"
