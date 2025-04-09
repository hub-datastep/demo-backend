from datetime import datetime


def timestamp_to_datetime_str(
    timestamp: int | None = None,
) -> str | None:
    # Check if timestamp exists
    if timestamp is None:
        return None

    # Ensure the timestamp is positive
    timestamp = abs(timestamp)

    # Convert timestamp to datetime object
    dt = datetime.fromtimestamp(timestamp)

    # Format datetime by pattern
    formated_datetime = dt.strftime("%d.%m.%Y %H:%M")

    return formated_datetime
