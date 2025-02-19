import math
from datetime import datetime


def formatted_time(time: str) -> str:
    """
    return a formmatted date and time 
    """
    dt = datetime.fromisoformat(time)
    formatted_dt = dt.strftime("%B %d, %Y at %I:%M %p")
    return formatted_dt

def remove_tax(amount: int, tax_rate: float) -> int:
    """
    removing tax and ceil the floating points ex -> 111.76 -> 111
    """
    taxed_amount = math.floor(amount - (amount * tax_rate))
    return taxed_amount
