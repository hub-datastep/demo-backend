from datetime import UTC, datetime


def get_current_month() -> int:
    now = datetime.now()
    current_month = now.month
    return int(current_month)


def get_now_utc() -> datetime:
    now = datetime.now(UTC)
    return now
