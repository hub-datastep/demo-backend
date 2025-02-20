from loguru import logger
from fastapi.encoders import jsonable_encoder

def get_order_details(r):
    body_json = jsonable_encoder(r  )
    logger.info(f"VYSOTA_WEBHOOK_LOGS: {body_json}")

    return