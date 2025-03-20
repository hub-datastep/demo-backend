import re
import traceback

from fastapi import HTTPException, status
from loguru import logger

from infra.domyland.chats import (
    get_message_template,
    send_message_to_internal_chat,
    send_message_to_resident_chat,
)
from infra.domyland.constants import (
    AI_USER_ID,
    INITIAL_MESSAGE_KEYPHRASE,
    ORDER_PROCESSED_BY_AI_MESSAGE,
    RESPONSIBLE_DEPT_ID,
    AlertTypeID,
    MessageTemplateName,
    OrderClass,
    OrderStatusID,
)
from infra.domyland.orders import get_order_details_by_id, update_order_status_details
from llm.chain.order_multi_classification.order_multi_classification_chain import (
    get_order_class,
)
from model.order_classification.order_classification_config_model import (
    get_order_classification_default_config,
)
from model.order_classification.order_classification_history_model import (
    get_saved_record_by_order_id,
    save_order_classification_record,
)
from model.order_notification.order_sla_ping_model import start_order_sla_tracking
from scheme.order_classification.order_classification_config_scheme import (
    MessageTemplate,
    ResponsibleUserWithAddresses,
    RulesWithParams,
)
from scheme.order_classification.order_classification_history_scheme import (
    OrderClassificationRecord,
)
from scheme.order_classification.order_classification_scheme import (
    OrderClassificationRequest,
    SummaryTitle,
    SummaryType,
)
from util.order_messages import find_in_text


def normalize_resident_request_string(query: str) -> str:
    """
    Убирает из текста заявки лишние части:
    - Переносы строк.
    - Секцию для фото.
    - Ссылки.
    - Лишние пробелы.
    """

    # Remove \n symbols
    removed_line_breaks_query = query.replace("\n", " ")

    # Remove photos
    removed_photos_query = removed_line_breaks_query.replace("Прикрепите фото:", " ")

    # Remove urls
    removed_urls_query = re.sub(r"http\S+", " ", removed_photos_query)

    # Replace multiple spaces with one
    fixed_spaces_query = re.sub(r"\s+", " ", removed_urls_query)

    return fixed_spaces_query


def _get_responsible_user_by_order_address(
    responsible_users_list: list[ResponsibleUserWithAddresses],
    order_address: str,
) -> ResponsibleUserWithAddresses | None:
    """
    Ищет в списке Исполнителя, у которого есть нужный адрес.
    """

    for responsible_user in responsible_users_list:
        addresses_list = responsible_user.address_list

        # Check if responsible user addresses contains order address
        for address in addresses_list:
            if address.lower() in order_address.lower():
                return responsible_user

    return None


def _get_class_params(
    rules_by_classes: dict,
    class_name_to_find: str,
) -> RulesWithParams | None:
    for class_name, params in rules_by_classes.items():
        class_name = class_name.lower().strip()
        class_name_to_find = class_name_to_find.lower().strip()

        if class_name == class_name_to_find:
            return RulesWithParams(**params)

    return None


def classify_order(
    body: OrderClassificationRequest,
    client: str | None = None,
) -> OrderClassificationRecord:
    alert_id = body.alertId
    alert_type_id = body.alertTypeId
    alert_timestamp = body.timestamp

    order_id = body.data.orderId
    order_status_id = body.data.orderStatusId

    # Init order classification history record to save later
    history_record = OrderClassificationRecord(
        alert_id=alert_id,
        alert_type_id=alert_type_id,
        alert_timestamp=alert_timestamp,
        order_id=order_id,
        order_status_id=order_status_id,
    )

    try:
        # Check if order was already classified
        saved_record = get_saved_record_by_order_id(
            order_id=order_id,
            client=client,
        )
        is_saved_record_exists = saved_record is not None
        if is_saved_record_exists:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    f"Order with ID {order_id} was already classified, "
                    f"history record ID {saved_record.id}"
                ),
            )

        # Check if order status is "pending" ("Ожидание")
        if order_status_id != OrderStatusID.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Order with ID {order_id} has status ID {order_status_id}, "
                    f"but status ID {OrderStatusID.PENDING} required"
                ),
            )

        # Check if event type is "new order"
        if alert_type_id != AlertTypeID.NEW_ORDER:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Order with ID {order_id} has alert type ID {alert_type_id}, "
                    f"but status ID {AlertTypeID.NEW_ORDER} required"
                ),
            )

        config = get_order_classification_default_config(client=client)

        config_id = config.id
        # Is needed to classify order
        is_use_order_classification = config.is_use_order_classification
        # Is needed to update order in Domyland
        # (blocked by is_use_order_classification)
        is_use_order_updating = (
            config.is_use_order_updating and is_use_order_classification
        )

        # Message for response fields disabled by config
        disabled_field_msg = (
            f"skipped by order classification config with ID {config_id}"
        )

        # Get order details
        order_details = get_order_details_by_id(order_id=order_id)
        history_record.order_details = order_details.dict()

        # TODO: use get_query_from_order_details instead
        # Get resident order query
        order_query: str | None = None
        for order_form in order_details.service.orderForm:
            if (
                order_form.type == SummaryType.TEXT
                and order_form.title == SummaryTitle.COMMENT
            ):
                order_query = order_form.value
        # logger.debug(f"Order {order_id} query: '{order_query}'")
        history_record.order_query = order_query

        # Check if resident comment exists and not empty if enabled
        is_order_query_exists = order_query is not None
        is_order_query_empty = is_order_query_exists and not bool(order_query.strip())

        if not is_order_query_exists or is_order_query_empty:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Order with ID {order_id} has no comment, cannot classify order",
            )

        # Get resident address (object)
        order_address: str | None = None
        for summary in order_details.order.summary:
            if summary.title == SummaryTitle.OBJECT:
                order_address = summary.value
        # logger.debug(f"Order {order_id} address: '{order_address}'")
        history_record.order_address = order_address

        # Check if resident address exists and not empty if enabled
        is_order_address_exists = order_address is not None
        is_order_address_empty = is_order_address_exists and not bool(
            order_address.strip()
        )

        if not is_order_address_exists or is_order_address_empty:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=(
                    f"Order with ID {order_id} has no address, "
                    f"cannot find responsible UDS"
                ),
            )

        # Get classes with rules from config and check if this param exists
        rules_by_classes = config.rules_by_classes

        if rules_by_classes is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    f"Classes with rules and params in config "
                    f"with ID {config.id} not found"
                ),
            )

        # Run LLM to classify order
        if is_use_order_classification:
            # Normalize order query for LLM chain
            normalized_query = normalize_resident_request_string(order_query)

            llm_response = get_order_class(
                order_query=normalized_query,
                rules_by_classes=rules_by_classes,
                client=client,
                # verbose=True,
            )
            order_class = llm_response.most_relevant_class_response.order_class.lower()
            query_summary = llm_response.query_summary

            # Save order query summary as normalized
            history_record.order_normalized_query = query_summary
            # Save full LLM response
            history_record.llm_response = llm_response.dict()
        else:
            order_class = disabled_field_msg
        history_record.order_class = order_class

        # TODO: decide what to do with every class
        is_emergency = None
        if is_use_order_classification:
            is_emergency = (
                order_class.lower().strip() == OrderClass.EMERGENCY.lower().strip()
            )

        # TODO: update 'is_emergency' param usage

        # Update order emergency class in Domyland
        if is_emergency and is_use_order_classification:
            # Check if responsible users is set in config
            if config.responsible_users is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Responsible users is not set in config with ID {config_id}",
                )

            # Get responsible UDS user id
            uds_list = [
                ResponsibleUserWithAddresses(**uds_data)
                for uds_data in config.responsible_users
            ]
            responsible_uds = _get_responsible_user_by_order_address(
                responsible_users_list=uds_list,
                order_address=order_address,
            )

            # Check if responsible UDS is found
            if responsible_uds is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=(
                        f"Cannot find responsible UDS for order "
                        f"with ID {order_id} and address '{order_address}'"
                    ),
                )

            history_record.responsible_user_id = responsible_uds.user_id

            # Get order class params
            class_params = _get_class_params(
                rules_by_classes=rules_by_classes,
                class_name_to_find=order_class,
            )

            is_use_order_with_this_class_updating = None
            if class_params is not None:
                is_use_order_with_this_class_updating = (
                    class_params.is_use_order_updating
                )

            is_uds_disabled = responsible_uds.is_disabled

            # Update order responsible user if enabled
            # And send message
            if (
                is_use_order_updating
                and is_use_order_with_this_class_updating
                and not is_uds_disabled
            ):
                response, request_body = update_order_status_details(
                    order_id=order_id,
                    responsible_dept_id=RESPONSIBLE_DEPT_ID,
                    # Update order status to "В работе"
                    order_status_id=OrderStatusID.IN_PROGRESS,
                    # Set responsible user to UDS
                    responsible_users_ids=[int(responsible_uds.user_id)],
                    # Update order inspector to AI Account
                    inspector_users_ids=[AI_USER_ID],
                )

                # Get template from config
                templates_list = [
                    MessageTemplate(**template)
                    for template in config.messages_templates
                ]

                # Start tracking Order SLA and ping Responsible Users
                start_order_sla_tracking(
                    order_id=order_id,
                    responsible_users_list=[responsible_uds],
                    messages_templates=templates_list,
                )

                # Mark order as processed by AI
                send_message_to_internal_chat(
                    order_id=order_id,
                    message=ORDER_PROCESSED_BY_AI_MESSAGE,
                )

                # Send initial message to resident chat in order if enabled
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
                                to_find=INITIAL_MESSAGE_KEYPHRASE,
                            )
                            if is_message_answer:
                                is_operator_answered = True
                                break

                    # If not answered to resident, send message
                    if not is_operator_answered:
                        template_name = MessageTemplateName.INITIAL
                        message_template = get_message_template(
                            templates_list=templates_list,
                            template_name=template_name,
                        )

                        # Send message to resident to show that order is processing
                        message_text = message_template.text
                        send_message_to_resident_chat(
                            order_id=order_id,
                            text=message_text,
                        )
                    # Else skip message sending
                    else:
                        history_record.comment = (
                            "Message not sent, operators already answered to resident"
                        )
                else:
                    history_record.comment = (
                        f"Message not sent, disabled by config with ID {config_id}"
                    )

            # If skip order updating, set required fields with message with reason
            else:
                request_body = {"result": disabled_field_msg}
                response = {"result": disabled_field_msg}

                # Message if skipped by class params
                if not is_use_order_with_this_class_updating:
                    updated_disabled_field_msg = (
                        f"{disabled_field_msg}; by params of class '{order_class}'"
                    )

                    request_body = {"result": updated_disabled_field_msg}
                    response = {"result": updated_disabled_field_msg}

                # Message if skipped by responsible user
                elif is_uds_disabled:
                    updated_disabled_field_msg = (
                        f"{disabled_field_msg}; "
                        f"by responsible user with ID '{responsible_uds.user_id}'"
                    )

                    request_body = {"result": updated_disabled_field_msg}
                    response = {"result": updated_disabled_field_msg}

            history_record.order_update_request = request_body
            history_record.order_update_response = response
        # else:
        #     if not is_use_order_classification:
        #         result = {"result": disabled_field_msg}
        #         history_record.order_update_request = result
        #         history_record.order_update_response = result

    except (HTTPException, Exception) as error:
        history_record.is_error = True

        # Получаем текст ошибки из атрибута detail для HTTPException
        if isinstance(error, HTTPException):
            comment = error.detail
        # Для других исключений используем str(error)
        else:
            logger.error(traceback.format_exc())
            comment = str(error)
        history_record.comment = comment

        # Print error to logs
        logger.error(comment)

    # logger.debug(f"History record:\n{history_record}")
    history_record = save_order_classification_record(
        record=history_record,
        client=client,
    )

    return history_record


if __name__ == "__main__":
    # Test orders IDs
    # order_id = 3197122
    # order_id = 3196509
    # Test orders with chat IDs
    order_id = 3301805
    # Real orders IDs
    # order_id = 3191519

    # order_query: str | None = None
    # for order_form in order_details.service.orderForm:
    #     if (
    #         order_form.type == SummaryType.TEXT
    #         and order_form.title == SummaryTitle.COMMENT
    #     ):
    #         order_query = order_form.value
    # print(f"Order query: {order_query}")

    # order_address = None
    # for summary in order_details.order.summary:
    #     if summary.title == SummaryTitle.OBJECT:
    #         order_address = summary.value
    # logger.debug(f"Order {order_id} address: {order_address}")

    # users_ids_list = _get_responsible_users_ids_by_order_address(order_address)
    # logger.debug(f"Responsible users IDs: {users_ids_list}")

    # config = get_order_classification_default_config()
    # logger.debug(f"Order Classification config:\n{config}\n")

    # responsible_uds_list = [
    #     UDS(**responsible_uds)
    #     for responsible_uds in config.responsible_users
    # ]
    # logger.debug(f"Responsible UDS list:\n{responsible_uds_list}\n")

    # df = DataFrame(responsible_uds_list)
    # df["address_list"] = df["address_list"].apply(lambda x: "\n".join(x))
    # df.to_excel(f"./ЕДС c адресам {datetime.now()}.xlsx", index=False)

    # try:
    #     # Get template from config
    #     templates_list = [
    #         MessageTemplate(**template) for template in config.messages_templates
    #     ]
    #     logger.debug(f"Messages Templates: {templates_list}")
    #     template_name = MessageTemplateName.INITIAL
    #     message_template = get_message_template(
    #         templates_list=templates_list,
    #         template_name=template_name,
    #     )

    #     # Check if template exists and enabled
    #     if not message_template:
    #         raise HTTPException(
    #             status_code=status.HTTP_404_NOT_FOUND,
    #             detail=(
    #                 f"Message template with name '{template_name}' "
    #                 "not found or disabled or empty"
    #             ),
    #         )

    #     # Send message to resident to show that order is processing
    #     message_text = message_template.text
    #     send_message_to_resident_chat(
    #         order_id=order_id,
    #         text=message_text,
    #     )
    # except HTTPException as e:
    #     logger.error(f"{e.detail}")
