from rq.job import JobStatus

from scheme.parsing.parsing_scheme import UTDCardOutputMessage, UTDCardInputMessage


def raise_utd_card_processing_exception(
    body: UTDCardInputMessage,
    text: str,
):
    return UTDCardOutputMessage(
        **body.dict(),
        status=JobStatus.FAILED,
        error_message=text,
    )
