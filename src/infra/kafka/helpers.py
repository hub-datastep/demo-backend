from pathlib import Path
from ssl import CERT_REQUIRED, Purpose, create_default_context
from typing import Any

from faststream.kafka import KafkaBroker
from faststream.security import SASLPlaintext

from scheme.kafka.broker_settings_scheme import KafkaBrokerSettings


def _get_broker_security_settings(settings: KafkaBrokerSettings) -> SASLPlaintext:
    ssl_context = None
    if settings.is_use_ssl and settings.ssl_cert_file_path:
        if not Path(settings.ssl_cert_file_path).exists():
            raise FileNotFoundError(
                f"SSL certfile at path '{settings.ssl_cert_file_path}' not found"
            )

        ssl_context = create_default_context(Purpose.SERVER_AUTH)
        ssl_context.check_hostname = False
        ssl_context.verify_mode = CERT_REQUIRED
        ssl_context.load_verify_locations(cafile=settings.ssl_cert_file_path)

    security = SASLPlaintext(
        ssl_context=ssl_context,
        use_ssl=settings.is_use_ssl,
        username=settings.username,
        password=settings.password,
    )
    return security


def create_kafka_broker(settings: KafkaBrokerSettings) -> KafkaBroker:
    security: SASLPlaintext | None = None
    if settings.is_use_ssl:
        security = _get_broker_security_settings(settings=settings)

    broker = KafkaBroker(
        settings.servers_list,
        security=security,
    )
    return broker


async def send_message_to_kafka(
    broker: KafkaBroker,
    message_body: Any,
    topic: str,
    key: str | None = None,
):
    # Convert key to bytes if key defined
    b_key: bytes | None = None
    if key:
        b_key = key.encode()

    await broker.publish(
        message_body,
        topic=topic,
        key=b_key,
    )
