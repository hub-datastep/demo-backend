from yake import KeywordExtractor

from util.normalize_name import normalize_name
from util.remove_adjectives import remove_adjectives

# Language for words in phrases
language = "ru"

# Определяет максимальный размер n-грамм
# Если установить в 1, yake будет извлекать только одиночные слова
# Если больше, то будет извлекать фразы
max_ngram_size = 1

# Words count to extract
numOfKeywords = 1

keyword_extractor = KeywordExtractor(
    lan=language,
    n=max_ngram_size,
    top=numOfKeywords,
)


def extract_keyword(text: str) -> str:
    normalized_text = normalize_name(text)
    normalized_text = remove_adjectives(normalized_text)

    extracted_list: list[tuple[str, float]] = keyword_extractor.extract_keywords(normalized_text)
    keyword, _ = extracted_list[0]

    return keyword
