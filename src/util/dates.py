from datetime import UTC, date, datetime, time


def get_current_month() -> int:
    now = datetime.now()
    current_month = now.month
    return int(current_month)


def get_now_utc() -> datetime:
    now = datetime.now(UTC)
    return now


def as_utc(dt: datetime | time) -> datetime | time:
    dt_utc = dt.replace(tzinfo=UTC)
    return dt_utc


def get_weekday_by_date(dt: datetime | date) -> str:
    weekday = dt.strftime("%A")
    return weekday
