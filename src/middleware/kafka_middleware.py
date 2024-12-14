from functools import wraps

from infra.kafka import kafka_broker


# Декоратор, чтобы не прописывать руками connect/close
def with_kafka_broker_connection(func):
    @wraps(func)
    async def wrapper_func(*args, **kwargs):
        await kafka_broker.connect()
        result = await func(*args, **kwargs)
        await kafka_broker.close()
        return result

    return wrapper_func
