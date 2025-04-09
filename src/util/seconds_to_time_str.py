# Time units and their grammatical forms
_TIME_UNITS = [
    (60 * 60 * 24 * 30, "месяц", "месяца", "месяцев"),
    (60 * 60 * 24, "день", "дня", "дней"),
    (60 * 60, "час", "часа", "часов"),
    (60, "минута", "минуты", "минут"),
    (1, "секунда", "секунды", "секунд"),
]


def seconds_to_duration_str(seconds: int | None = None) -> str | None:
    """
    Converts seconds into a human-readable str
    with appropriate time unit and grammatical form.

    Args:
        seconds (int | None): Seconds to convert. If None or 0, returns None.

    Returns:
        str | None: String representing time in largest possible unit
        (e.g., "2 часа", "1 день", "5 минут"), or None if input is None or 0.

    Examples:
        >>> seconds_to_duration_str(3600)
        "1 час"
        >>> seconds_to_duration_str(86400)
        "1 день"
        >>> seconds_to_duration_str(125)
        "2 минуты"
        >>> seconds_to_duration_str(0)
        None
        >>> seconds_to_duration_str(None)
        None
    """

    # Check if input seconds exists and not 0
    if not seconds:
        return None

    # Iterate through the predefined time units to find the largest applicable unit
    for unit_seconds, singular, dual, plural in _TIME_UNITS:
        # Calculate the number of units for the current time unit
        value = seconds // unit_seconds

        # If the value is greater than 0, determine the correct grammatical form
        if value > 0:
            # Singular form: e.g., "1 час", "1 день"
            if value % 10 == 1 and value % 100 != 11:
                return f"{value} {singular}"
            # Dual form: e.g., "2 часа", "3 дня"
            elif 2 <= value % 10 <= 4 and (value % 100 < 10 or value % 100 >= 20):
                return f"{value} {dual}"
            # Plural form: e.g., "5 часов", "11 дней"
            else:
                return f"{value} {plural}"


if __name__ == "__main__":
    test_seconds = 17511966
    print(seconds_to_duration_str(test_seconds))
