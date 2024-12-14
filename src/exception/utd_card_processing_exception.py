from model.file.utd.parsing_job import MappingWithParsingStatus
from scheme.parsing.parsing_scheme import UTDCardOutputMessage, UTDCardInputMessage


def raise_utd_card_processing_exception(
    body: UTDCardInputMessage,
    text: str,
):
    return UTDCardOutputMessage(
        **body.dict(),
        status=MappingWithParsingStatus.ERROR,
        error_message=text,
    )
