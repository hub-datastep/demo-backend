from datetime import UTC, date, datetime


def get_current_month() -> int:
    now = datetime.now()
    current_month = now.month
    return int(current_month)


def get_now_utc() -> datetime:
    now = datetime.now(UTC)
    return now


def get_weekday_by_date(dt: datetime | date) -> str:
    weekday = dt.strftime("%A")
    return weekday
