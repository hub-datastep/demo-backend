import asyncio
from faststream import FastStream
from loguru import logger

from infra.env import (
    UNISTROY_MAPPING_INPUT_TOPIC,
    UNISTROY_KAFKA_CONSUMERS_GROUP,
    UNISTROY_MAPPING_LINK_OUTPUT_TOPIC,
)
from infra.kafka import kafka_broker, send_message_to_kafka
from model.mapping import mapping_with_parsing_model
from scheme.file.utd_card_message_scheme import UTDCardInputMessage

app = FastStream(
    kafka_broker,
    title="Mapping with Parsing",
)

KAFKA_DEFAULT_SETTINGS = {
    "group_id": UNISTROY_KAFKA_CONSUMERS_GROUP,
    # Получать 1 сообщение (False) или несколько сразу (True)
    "batch": False,
    # Кол-во обрабатываемых сообщений за раз
    "max_records": 1,
    "auto_offset_reset": "earliest",
}


# Unistroy UTD PDF files Mapping Subscriber
# Gets messages from topic
@kafka_broker.subscriber(
    UNISTROY_MAPPING_INPUT_TOPIC,
    **KAFKA_DEFAULT_SETTINGS,
)
async def unistroy_mapping_with_parsing_consumer(body: UTDCardInputMessage):
    logger.debug(f"Unistroy Kafka Request (input message):\n{body}")

    # Run mapping with parsing and wait results
    output_messages_list = mapping_with_parsing_model.parse_and_map_utd_card(body=body)

    async for output_message in output_messages_list:
        logger.debug(
            f"Unistroy Kafka Response (check-results message):\n{output_message}"
        )

        # Send message to Unistroy Kafka link-topic with url to check results
        await send_message_to_kafka(
            message_body=output_message.dict(),
            topic=UNISTROY_MAPPING_LINK_OUTPUT_TOPIC,
        )


if __name__ == "__main__":
    asyncio.run(app.run())
