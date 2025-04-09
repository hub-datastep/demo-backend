import asyncio
import traceback

from fastapi import HTTPException
from faststream import FastStream
from loguru import logger

from infra.domyland.chat import send_message_to_resident_chat
from infra.env import env
from infra.kafka.brokers import kafka_broker
from infra.llm_clients_credentials import Client
from infra.order_notification import ActionLogName
from model.order_notification.order_notification_logs_model import (
    check_if_action_was_unsuccessful,
    get_saved_log_record_by_order_id,
    update_order_notification_log_record,
)
from scheme.kafka.send_message_consumer_scheme import MessageSendRequest
from util.json_serializing import serialize_obj, serialize_objs_list

app = FastStream(
    kafka_broker,
    title="Order Chat Message Sending",
)

_SETTINGS = {
    "group_id": env.KAFKA_ORDERS_CONSUMERS_GROUP,
    # Получать 1 сообщение (False) или несколько сразу (True)
    "batch": True,
    # Кол-во обрабатываемых сообщений за раз
    "max_records": 100,
    # Если нет смещения, читать только последнее сообщение
    "auto_offset_reset": "latest",
}

_CLIENT = Client.VYSOTA if env.IS_DEV_ENV else None

WAIT_TIME_IN_SEC = 30


@kafka_broker.subscriber(
    env.KAFKA_ORDER_CHAT_MESSAGE_SENDING_TOPIC,
    **_SETTINGS,
)
async def order_chat_message_send_consumer(
    messages_list: list[MessageSendRequest],
):
    try:
        logger.debug(f"Messages batch ({len(messages_list)} items):\n{messages_list}")

        logger.debug(f"Wait {WAIT_TIME_IN_SEC} seconds, before process request")
        await asyncio.sleep(WAIT_TIME_IN_SEC)
        logger.debug(f"Timeout passed, so processing request")

        # If no messages, just exit
        if not messages_list:
            return

        # Collecting unique messages list to send resident
        messages_to_send: dict[str, MessageSendRequest] = {}
        for message in messages_list:
            order_id = message.order_id
            if str(order_id) not in list(messages_to_send.keys()):
                messages_to_send.update({f"{order_id}": message})

        # Send messages to residents orders chats
        for _, message in messages_to_send.items():
            order_id = message.order_id

            # Check if order was already classified
            saved_log_record = get_saved_log_record_by_order_id(
                order_id=order_id,
                client=_CLIENT,
            )
            is_saved_log_record_exists = saved_log_record is not None
            # Check if was error
            if is_saved_log_record_exists:
                was_error = check_if_action_was_unsuccessful(
                    action_name=ActionLogName.SEND_MESSAGE_TO_RESIDENT,
                    log_record=saved_log_record,
                )
                if was_error:
                    logger.error(
                        f"Order with ID {order_id} finished "
                        f"with error (log record ID {saved_log_record.id}), "
                        f"so do not send message to resident"
                    )
                    continue

            message_text = message.message_text
            files_to_send = message.files

            logger.debug(f"Message for Order with ID {order_id}")
            logger.debug(f"Message text:\n{message_text}")
            logger.debug(f"Files to send:\n{files_to_send}")

            # Send message to Resident
            send_message_to_resident_response, send_message_to_resident_request_body = (
                send_message_to_resident_chat(
                    order_id=order_id,
                    text=message_text,
                    files=files_to_send,
                )
            )
            action_log = {
                "action": ActionLogName.SEND_MESSAGE_TO_RESIDENT,
                "metadata": {
                    "message_text": message_text,
                    "message_files": serialize_objs_list(files_to_send),
                    "request_body": serialize_obj(
                        send_message_to_resident_request_body
                    ),
                    "response": serialize_obj(send_message_to_resident_response),
                },
            }

            # Try to update action logs
            if is_saved_log_record_exists:
                for i, log_record in enumerate(saved_log_record.actions_logs):
                    # Check action name
                    log_action_name: str | None = log_record.get("action")
                    if (
                        log_action_name
                        and log_action_name.strip().lower()
                        != ActionLogName.SEND_MESSAGE_TO_RESIDENT.strip().lower()
                    ):
                        saved_log_record.actions_logs[i] = action_log
                        update_order_notification_log_record(
                            log_record=saved_log_record,
                            client=_CLIENT,
                        )
                        break

    except (HTTPException, Exception) as error:
        # Получаем текст ошибки из атрибута detail для HTTPException
        if isinstance(error, HTTPException):
            comment = error.detail
        # Для других исключений используем str(error)
        else:
            logger.error(traceback.format_exc())
            comment = str(error)

        # Print error to logs
        logger.error(comment)


if __name__ == "__main__":
    asyncio.run(app.run())
