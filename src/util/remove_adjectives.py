import re

ADJECTIVES_PATTERN = r'\b\w+(?:ый|ий|ой|ая|яя|ое|ее|ые|ие|их|ых|им|ым|ей|ею|ою|ую|ому|ему|ыми|ими|его|ого|ей|ой|ую|ою)\b'


def remove_adjectives(text: str) -> str:
    return re.sub(ADJECTIVES_PATTERN, "", text).strip()
