import asyncio
import traceback

from fastapi import HTTPException, status
from loguru import logger

from infra.domyland.chats import get_message_template, request_send_message_to_resident
from infra.domyland.constants import (
    AI_USER_ID,
    CLEANING_RESULT_KEYPHRASE,
    RESPONSIBLE_DEPT_ID,
    TRANSFER_ACCOUNT_ID,
    AlertTypeID,
    MessageTemplateName,
    OrderStatusID,
)
from infra.domyland.orders import (
    get_order_details_by_id,
    get_query_from_order_details,
    update_order_status_details,
)
from infra.llm_clients_credentials import Service, get_llm_by_client_credentials
from infra.order_notification import ActionLogName
from llm.chain.cleaning_result_comment.cleaning_result_message_chain import (
    get_cleaning_results_message,
    get_cleaning_results_message_chain,
)
from model.order_classification.order_classification_config_model import (
    get_order_classification_default_config,
)
from model.order_notification.order_notification_logs_model import (
    check_if_action_was_unsuccessful,
    get_saved_log_record_by_order_id,
    save_order_notification_log_record,
)
from scheme.order_classification.order_classification_config_scheme import (
    MessageTemplate,
    ResponsibleUser,
)
from scheme.order_classification.order_classification_scheme import MessageFileToSend
from scheme.order_notification.order_notification_logs_scheme import (
    OrderNotificationLog,
)
from scheme.order_notification.order_notification_scheme import (
    OrderNotificationRequestBody,
)
from util.json_serializing import serialize_obj, serialize_objs_list
from util.order_messages import find_in_text


def _get_responsible_users_by_order_class(
    responsible_users: list[ResponsibleUser],
    order_class: str,
) -> list[ResponsibleUser]:
    """
    Filter Responsible Users list by Order Class.
    """

    filtered_users = []

    for user in responsible_users:
        if user.order_class == order_class and not user.is_disabled:
            filtered_users.append(user)

    return filtered_users


def process_event(
    body: OrderNotificationRequestBody,
    client: str | None = None,
) -> OrderNotificationLog:
    alert_type_id = body.alertTypeId

    order_id = body.data.orderId
    order_status_id = body.data.orderStatusId

    log_record = OrderNotificationLog(
        input_request_body=serialize_obj(body),
        order_id=order_id,
        order_status_id=order_status_id,
        actions_logs=[],
    )

    try:
        # Check if order was already classified
        saved_log_record = get_saved_log_record_by_order_id(
            order_id=order_id,
            client=client,
        )
        is_saved_log_record_exists = saved_log_record is not None
        if is_saved_log_record_exists:
            was_error = check_if_action_was_unsuccessful(
                action_name=ActionLogName.SEND_MESSAGE_TO_RESIDENT,
                log_record=saved_log_record,
            )
            if not was_error:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=(
                        f"Event 'order_status_updated' for Order with ID {order_id} "
                        "was already processed, "
                        f"log record ID {saved_log_record.id}"
                    ),
                )

        # Check if event type is "order status updated"
        if alert_type_id != AlertTypeID.ORDER_STATUS_UPDATED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Order with ID {order_id} has alert type ID {alert_type_id}, "
                    f"but status ID {AlertTypeID.ORDER_STATUS_UPDATED} required"
                ),
            )

        config = get_order_classification_default_config(
            client=client,
        )
        config_id = config.id
        skipped_action_text = f"skipped by config with ID {config_id}"

        # Get order details
        order_details = get_order_details_by_id(order_id=order_id)
        log_record.order_details = serialize_obj(order_details)

        # Get resident order query
        order_query = get_query_from_order_details(order_details=order_details)
        is_query_exists = order_query is not None and order_query.strip() != ""
        log_record.order_query = order_query

        # Check if order status is "pending" ("Ожидание")
        is_order_in_pending_status = order_status_id == OrderStatusID.PENDING

        # Check if order responsible users include "Александр Специалист"
        # or include cleaning account
        is_transfer_account_in_responsible_users = False
        is_cleaning_account_in_responsible_users = False
        order_responsible_users = order_details.order.responsibleUsers
        for user in order_responsible_users:
            if user.id == TRANSFER_ACCOUNT_ID:
                is_transfer_account_in_responsible_users = True
                break
            if user.fullName and "клининг" in user.fullName.lower():
                is_cleaning_account_in_responsible_users = True
                break

        # Check if order status comment exists
        order_status_comment = order_details.order.orderStatusComment
        is_status_comment_exists = (
            order_status_comment is not None and order_status_comment.strip() != ""
        )
        log_record.order_status_comment = order_status_comment

        # Check in order history if cleaning account was in responsible users
        is_cleaning_account_was_in_responsible_users = False
        order_history = order_details.order.statusHistory
        for record in order_history:
            for user in record.responsibleUsers:
                if user.fullName and "клининг" in user.fullName.lower():
                    is_cleaning_account_was_in_responsible_users = True
                    break

        # Check if cleaning-order is finished
        is_cleaning_order_finished = (
            is_order_in_pending_status
            and is_query_exists
            and (
                is_cleaning_account_in_responsible_users
                or is_cleaning_account_was_in_responsible_users
            )
            and (is_transfer_account_in_responsible_users or is_status_comment_exists)
        )
        log_record.actions_logs.append(
            {
                "action": ActionLogName.VALIDATE_EVENT,
                "metadata": {
                    "is_order_in_pending_status": is_order_in_pending_status,
                    "is_query_exists": is_query_exists,
                    "is_cleaning_account_in_responsible_users": is_cleaning_account_in_responsible_users,
                    "is_cleaning_account_was_in_responsible_users": is_cleaning_account_was_in_responsible_users,
                    "is_transfer_account_in_responsible_users": is_transfer_account_in_responsible_users,
                    "is_status_comment_exists": is_status_comment_exists,
                    "is_cleaning_order_finished": is_cleaning_order_finished,
                },
            }
        )

        # Check if event is valid (is finished cleaning-order)
        if not is_cleaning_order_finished:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Event is not valid",
            )

        llm = get_llm_by_client_credentials(
            client=client,
            service=Service.ORDER_CLASSIFICATION,
        )
        chain = get_cleaning_results_message_chain(llm=llm)

        # Generate message with LLM for resident about cleaning results
        llm_response = get_cleaning_results_message(
            chain=chain,
            order_query=order_query,
            order_status_comment=order_status_comment,
        )
        log_record.message_llm_response = serialize_obj(llm_response)
        cleaning_results_text = llm_response.message
        is_results_text_exists = (
            cleaning_results_text is not None and cleaning_results_text.strip() != ""
        )

        # Check if text from LLM exists and can be sent
        if not is_results_text_exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"LLM message is empty and cannot be sent",
            )

        # Get order pinned files from Responsible Users
        order_files = order_details.order.files
        is_files_exists = order_files is not None and len(order_files) > 0

        files_to_send: list[MessageFileToSend] | None = None
        if is_files_exists:
            files_to_send = [
                MessageFileToSend(fileName=file.name) for file in order_files
            ]

        # Get template from config
        templates_list = [
            MessageTemplate(**template) for template in config.messages_templates
        ]
        template_name = MessageTemplateName.CLEANING_RESULTS
        message_template = get_message_template(
            templates_list=templates_list,
            template_name=template_name,
        )

        # Check if template exists and enabled
        if not message_template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    f"Message template with name '{template_name}' "
                    "not found or disabled or empty"
                ),
            )

        # Combine message text
        message_text = message_template.text
        message_text = message_text.format(
            cleaning_results_text=cleaning_results_text,
        )

        # Check if need send message
        is_use_send_message = config.is_use_send_message
        if is_use_send_message:
            # Get Order Chat and Messages in it
            order_chat = order_details.order.chat
            is_chat_exists = order_chat is not None

            order_chat_messages = order_chat.items if is_chat_exists else None
            is_messages_exists_in_chat = (
                order_chat_messages is not None and len(order_chat_messages) > 0
            )

            # Check if operators not answered yet
            is_operator_answered: bool | None = None
            if is_messages_exists_in_chat:
                for message in order_chat_messages:
                    # Find answer-message by keyphrase
                    is_message_answer = find_in_text(
                        text=message.text,
                        to_find=CLEANING_RESULT_KEYPHRASE,
                    )
                    if is_message_answer:
                        is_operator_answered = True
                        break

            # If not answered to resident, send message
            if not is_operator_answered:
                # Send message to resident to show that order is processing

                asyncio.run(
                    request_send_message_to_resident(
                        order_id=order_id,
                        message_text=message_text,
                        files=files_to_send,
                    )
                )
                # Fill logs just to save any logs from action
                logs_text = "request to send message successfully sent to kafka"
                send_message_to_resident_response = logs_text
                send_message_to_resident_request_body = logs_text
                log_record.actions_logs.append(
                    {
                        "action": ActionLogName.SEND_MESSAGE_TO_RESIDENT,
                        "metadata": {
                            "message_text": message_text,
                            "message_files": serialize_objs_list(files_to_send),
                            "request_body": send_message_to_resident_request_body,
                            "response": send_message_to_resident_response,
                        },
                    }
                )
            # Else skip message sending
            else:
                action_comment = (
                    f"Message not sent, operators already answered to resident"
                )
                log_record.actions_logs.append(
                    {
                        "action": ActionLogName.SEND_MESSAGE_TO_RESIDENT,
                        "metadata": {
                            "message_text": message_text,
                            "request_body": action_comment,
                            "response": action_comment,
                        },
                    }
                )
        else:
            log_record.actions_logs.append(
                {
                    "action": ActionLogName.SEND_MESSAGE_TO_RESIDENT,
                    "metadata": {
                        "message_text": message_text,
                        "request_body": skipped_action_text,
                        "response": skipped_action_text,
                    },
                }
            )

        # Update Order status to "Completed"
        is_use_order_updating = config.is_use_order_updating
        if is_use_order_updating:
            responsible_users_ids_list = [user.id for user in order_responsible_users]
            update_order_status_response, update_order_status_request_body = (
                update_order_status_details(
                    order_id=order_id,
                    responsible_dept_id=RESPONSIBLE_DEPT_ID,
                    # Set status to "Выполнено"
                    order_status_id=OrderStatusID.COMPLETED,
                    # Set responsible user to UDS
                    responsible_users_ids=responsible_users_ids_list,
                    # Update order inspector to AI Account
                    inspector_users_ids=[AI_USER_ID],
                )
            )
            log_record.actions_logs.append(
                {
                    "action": ActionLogName.UPDATE_ORDER_STATUS,
                    "metadata": {
                        "request_body": update_order_status_request_body,
                        "response": update_order_status_response,
                    },
                }
            )
        else:
            log_record.actions_logs.append(
                {
                    "action": ActionLogName.UPDATE_ORDER_STATUS,
                    "metadata": {
                        "request_body": skipped_action_text,
                        "response": skipped_action_text,
                    },
                }
            )

    except (HTTPException, Exception) as error:
        log_record.is_error = True

        # Получаем текст ошибки из атрибута detail для HTTPException
        if isinstance(error, HTTPException):
            comment = error.detail
        # Для других исключений используем str(error)
        else:
            logger.error(traceback.format_exc())
            comment = str(error)
        log_record.comment = comment

        # Print error to logs
        logger.error(comment)

    # logger.debug(f"Order Notification Log:\n{log_record}")
    log_record = save_order_notification_log_record(
        log_record=log_record,
        client=client,
    )

    return log_record
