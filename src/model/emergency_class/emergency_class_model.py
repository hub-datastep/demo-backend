import re

from fastapi import HTTPException, status

from datastep.chains.emergency_class_chain import get_emergency_class_chain
from scheme.emergency_class.emergency_class_scheme import EmergencyClassRequest, SummaryType, SummaryTitle


def _normalize_resident_request_string(query: str) -> str:
    # Remove \n symbols
    removed_line_breaks_query = query.replace("\n", " ")

    # Remove photos
    removed_photos_query = removed_line_breaks_query.replace("Прикрепите фото:", " ")

    # Remove urls
    removed_urls_query = re.sub(r"http\S+", " ", removed_photos_query)

    # Replace multiple spaces with one
    fixed_spaces_query = re.sub(r"\s+", " ", removed_urls_query)

    return fixed_spaces_query


def get_emergency_class(body: EmergencyClassRequest) -> str:
    order_query: str | None = None
    for summary in body.data.summary:
        if summary.type == SummaryType.TEXT and summary.title == SummaryTitle.COMMENT:
            order_query = summary.value

    if order_query is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="В заявке отсутствует комментарий для определения её аварийности.",
        )

    normalized_query = _normalize_resident_request_string(order_query)
    chain = get_emergency_class_chain()
    answer: str = chain.run(query=normalized_query)
    return answer
