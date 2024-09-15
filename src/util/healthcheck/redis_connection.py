from fastapi import HTTPException, status
from redis.exceptions import ConnectionError

from infra.redis_queue import get_redis_connection


def check_redis_connection():
    try:
        redis = get_redis_connection()
        redis.ping()
    except ConnectionError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"{e}",
        )
