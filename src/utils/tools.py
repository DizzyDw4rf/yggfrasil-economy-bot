from datetime import datetime


def formatted_time(time) -> str:
    dt = datetime.fromisoformat(time)
    formatted_dt = dt.strftime("%B %d, %Y at %I:%M %p")
    return formatted_dt
