import re


def normalize_name(text: str) -> str:
    text = text.lower()
    # deleting newlines and line-breaks
    text = re.sub(
        '\-\s\r\n\s{1,}|\-\s\r\n|\r\n',
        '',
        text
    )
    # deleting symbols
    text = re.sub(
        '[.,:;_%©?*,!@#$%^&()\d]|[+=]|[[]|[]]|[/]|"|\s{2,}|-',
        ' ',
        text
    )
    text = ' '.join(word for word in text.split() if len(word) > 2)

    return text
