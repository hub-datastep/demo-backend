import traceback
from asyncio import iscoroutinefunction
from functools import wraps

from fastapi import HTTPException
from loguru import logger


def handle_errors(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            if iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            return result

        except (HTTPException, Exception) as error:
            if isinstance(error, HTTPException):
                status_code = error.status_code
                logger.debug(f"Status Code: {status_code}")

                comment = error.detail
            else:
                logger.debug(f"{traceback.format_exc()}")
                comment = str(error)

            logger.error(comment)

    return wrapper
