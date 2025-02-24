from loguru import logger
from fastapi.encoders import jsonable_encoder

def get_order_details(r, url):
    body_json = jsonable_encoder(r)
    logger.info(f"{url}: {body_json}")

    return