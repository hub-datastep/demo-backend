from loguru import logger

from scheme.file.utd_card_message_scheme import UTDCardOutputMessage, UTDCardInputMessage, UTDCardStatus


def raise_utd_card_processing_exception(
    body: UTDCardInputMessage,
    error_message: str,
):
    logger.error(f"Error occurred while processing UTD Card: {error_message}")
    return UTDCardOutputMessage(
        **body.dict(),
        status=UTDCardStatus.ERROR,
        error_message=error_message,
    )
