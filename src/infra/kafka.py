import ssl
from functools import wraps
from pathlib import Path

from faststream.kafka import KafkaBroker, KafkaRouter
from faststream.security import SASLPlaintext

from infra.env import KAFKA_BOOTSTRAP_SERVERS, KAFKA_USERNAME, KAFKA_PASSWORD, KAFKA_WITH_SSL


def create_broker():
    kafka_router = KafkaRouter()

    brokers = KAFKA_BOOTSTRAP_SERVERS.split(",")

    if KAFKA_WITH_SSL:
        ssl_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_REQUIRED
        # NOTE: Путь до сертификата. Возможно, есть смысл хранить в env или поменять с корня проекта
        path_to_cert = (Path(__file__).parent / ".." / ".." / "ca-cert.pem").resolve()
        ssl_context.load_verify_locations(cafile=path_to_cert)
        security = SASLPlaintext(
            ssl_context=ssl_context, username=KAFKA_USERNAME, password=KAFKA_PASSWORD
        )
        kafka_broker = KafkaBroker(brokers, security=security)
    else:
        kafka_broker = KafkaBroker(brokers)

    kafka_broker.include_router(router=kafka_router)

    return kafka_broker


def with_broker_connection(func):
    """
    Декоратор, чтобы не прописывать руками connect/close
    """

    @wraps(func)
    async def wrapper_func(*args, **kwargs):
        await broker.connect()
        result = await func(*args, **kwargs)
        await broker.close()
        return result

    return wrapper_func


broker = create_broker()
