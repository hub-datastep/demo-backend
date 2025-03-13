def find_in_text(
    to_find: str,
    text: str | None = None,
) -> None | bool:
    if text is None:
        return None
    return to_find.lower() in text.lower()
