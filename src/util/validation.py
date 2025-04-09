def is_exists_and_not_empty(text: str | None = None) -> bool:
    """
    Check if string exists (not None) and not empty.
    """

    is_exists = text is not None
    is_empty = is_exists and not bool(text.strip())
    return is_exists and not is_empty


def value_or_empty_str(value: str | None) -> str:
    """
    Returns empty str if value is None.
    Otherwise, returns value as-is.
    """

    if value is None:
        return ""

    return value
