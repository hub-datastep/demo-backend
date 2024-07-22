from datetime import datetime


def get_current_month() -> int:
    now = datetime.now()
    current_month = now.month
    return int(current_month)
