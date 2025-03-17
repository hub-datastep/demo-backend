from functools import wraps

from faststream.kafka import KafkaBroker


# Декоратор, чтобы не прописывать руками connect/close
def with_kafka_broker_connection(broker: KafkaBroker):
    def decorator(func):
        @wraps(func)
        async def wrapper_func(*args, **kwargs):
            await broker.connect()
            result = await func(*args, **kwargs)
            await broker.close()
            return result

        return wrapper_func

    return decorator
