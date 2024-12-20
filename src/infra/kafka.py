from ssl import create_default_context, Purpose, CERT_REQUIRED
from typing import Any

from faststream.kafka import KafkaBroker, KafkaRouter
from faststream.security import SASLPlaintext
from loguru import logger

from infra.env import KAFKA_BOOTSTRAP_SERVERS, KAFKA_USERNAME, KAFKA_PASSWORD, IS_KAFKA_WITH_SSL, DATA_FOLDER_PATH

kafka_router = KafkaRouter()

brokers_list = KAFKA_BOOTSTRAP_SERVERS.split(",")

SSL_CERT_PATH = f"{DATA_FOLDER_PATH}/ssl-certs/unistroy-ca-cert.pem"


def create_kafka_broker():
    security = None
    # Init Kafka Security if needed
    if IS_KAFKA_WITH_SSL:
        ssl_context = create_default_context(Purpose.SERVER_AUTH)
        ssl_context.check_hostname = False
        ssl_context.verify_mode = CERT_REQUIRED
        ssl_context.load_verify_locations(cafile=SSL_CERT_PATH)
        logger.debug(f"Kafka Username: {KAFKA_USERNAME}")
        logger.debug(f"Kafka Password: {KAFKA_PASSWORD}")
        security = SASLPlaintext(
            ssl_context=ssl_context,
            username=KAFKA_USERNAME,
            password=KAFKA_PASSWORD,
        )

    # Init Kafka Broker
    kafka_broker = KafkaBroker(
        brokers_list,
        security=security,
    )

    kafka_broker.include_router(router=kafka_router)

    return kafka_broker


kafka_broker = create_kafka_broker()


async def send_message_to_kafka(
    message_body: Any,
    topic: str,
):
    await kafka_broker.publish(
        message_body,
        topic=topic,
    )
