import re
import time

import requests
from fastapi import HTTPException, status
from loguru import logger

from infra.env import (
    DOMYLAND_AUTH_EMAIL,
    DOMYLAND_AUTH_PASSWORD,
    DOMYLAND_AUTH_TENANT_NAME,
)
from infra.order_classification import WAIT_TIME_IN_SEC
from llm.chain.order_multi_classification.order_multi_classification_chain import (
    get_order_class,
)
from model.order_classification.order_classification_history_model import (
    get_saved_record_by_order_id,
    save_order_classification_record,
)
from repository.order_classification.order_classification_config_repository import (
    get_default_config,
    DEFAULT_CONFIG_ID,
)
from scheme.order_classification.order_classification_config_scheme import (
    RulesWithParams,
    ResponsibleUserWithAddresses,
)
from scheme.order_classification.order_classification_history_scheme import (
    OrderClassificationRecord,
)
from scheme.order_classification.order_classification_scheme import (
    AlertTypeID,
    OrderClassificationRequest,
    OrderDetails,
    OrderStatusID,
    SummaryTitle,
    SummaryType,
)

DOMYLAND_API_BASE_URL = "https://sud-api.domyland.ru"
DOMYLAND_APP_NAME = "Datastep"

# "Администрация" - DEPT ID 38
RESPONSIBLE_DEPT_ID = 38

# DataStep AI User ID - 15698
AI_USER_ID = 15698

# Message to mark AI processed orders (in internal chat)
ORDER_PROCESSED_BY_AI_MESSAGE = "ИИ классифицировал эту заявку как аварийную"


def normalize_resident_request_string(query: str) -> str:
    # Remove \n symbols
    removed_line_breaks_query = query.replace("\n", " ")

    # Remove photos
    removed_photos_query = removed_line_breaks_query.replace("Прикрепите фото:", " ")

    # Remove urls
    removed_urls_query = re.sub(r"http\S+", " ", removed_photos_query)

    # Replace multiple spaces with one
    fixed_spaces_query = re.sub(r"\s+", " ", removed_urls_query)

    return fixed_spaces_query


def _get_domyland_headers(auth_token: str | None = None):
    if auth_token is None:
        return {
            "AppName": DOMYLAND_APP_NAME,
        }

    return {
        "AppName": DOMYLAND_APP_NAME,
        "Authorization": auth_token,
    }


def _get_auth_token() -> str:
    req_body = {
        "email": DOMYLAND_AUTH_EMAIL,
        "password": DOMYLAND_AUTH_PASSWORD,
        "tenantName": DOMYLAND_AUTH_TENANT_NAME,
    }

    response = requests.post(
        url=f"{DOMYLAND_API_BASE_URL}/auth",
        json=req_body,
        headers=_get_domyland_headers(),
    )

    if not response.ok:
        raise HTTPException(
            status_code=response.status_code,
            detail=f"Domyland Auth: {response.text}",
        )

    auth_token = response.json()["token"]
    return auth_token


def _get_order_details_by_id(order_id: int) -> OrderDetails:
    # Authorize in Domyland API
    auth_token = _get_auth_token()

    # Update order status
    response = requests.get(
        url=f"{DOMYLAND_API_BASE_URL}/initial-data/dispatcher/order-info/{order_id}",
        headers=_get_domyland_headers(auth_token),
    )
    response_data = response.json()
    # logger.debug(f"Order {order_id} details:\n{response_data}")

    if not response.ok:
        raise HTTPException(
            status_code=response.status_code,
            detail=f"OrderDetails GET: {response_data}",
        )

    order_details = OrderDetails(**response_data)
    return order_details


# def _update_order_status(
#     order_id: int,
#     customer_id: int,
#     place_id: int,
#     event_id: int,
#     building_id: int,
#     order_data: list[OrderFormUpdate],
# ):
#     # Authorize in Domyland API
#     auth_token = _get_auth_token()
#
#     order_data_dict = [data.dict() for data in order_data]
#
#     req_body = {
#         "customerId": customer_id,
#         "placeId": place_id,
#         "eventId": event_id,
#         "buildingId": building_id,
#         "orderData": order_data_dict,
#         # serviceTypeId == 1 is Аварийная заявка
#         "serviceTypeId": 1,
#     }
#
#     # Update order status
#     response = requests.put(
#         url=f"{DOMYLAND_API_BASE_URL}/orders/{order_id}",
#         json=req_body,
#         headers=_get_domyland_headers(auth_token),
#     )
#     response_data = response.json()
#
#     if not response.ok:
#         raise HTTPException(
#             status_code=response.status_code,
#             detail=f"Order UPDATE: {response_data}",
#         )
#
#     return response_data, req_body


def _get_responsible_user_by_order_address(
    responsible_users_list: list[ResponsibleUserWithAddresses],
    order_address: str,
) -> ResponsibleUserWithAddresses | None:
    for responsible_user in responsible_users_list:
        addresses_list = responsible_user.address_list

        # Check if responsible user addresses contains order address
        for address in addresses_list:
            if address.lower() in order_address.lower():
                return responsible_user

    return None


# def _get_order_status_details(order_id: int) -> dict:
#     # Authorize in Domyland API
#     auth_token = _get_auth_token()
#
#     # Update responsible user
#     response = requests.get(
#         url=f"{DOMYLAND_API_BASE_URL}/orders/{order_id}/status",
#         headers=_get_domyland_headers(auth_token),
#     )
#     response_data = response.json()
#
#     if not response.ok:
#         raise HTTPException(
#             status_code=response.status_code,
#             detail=f"Order status GET: {response_data}",
#         )
#
#     return response_data

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


def _update_order_status_details(
    order_id: int,
    responsible_dept_id: int,
    order_status_id: int,
    responsible_users_ids: list[int],
    inspector_users_ids: list[int],
) -> tuple[dict, dict]:
    try:
        # # Just save prev params in order status details
        # prev_order_status_details = _get_order_status_details(order_id)

        # Authorize in Domyland API
        auth_token = _get_auth_token()

        req_body = {
            # # Save all prev params from order status details (not needed to update)
            # **prev_order_status_details,
            # Update necessary params
            "responsibleDeptId": responsible_dept_id,
            "orderStatusId": order_status_id,
            "responsibleUserIds": responsible_users_ids,
            "inspectorIds": inspector_users_ids,
        }

        # Update responsible user
        response = requests.put(
            url=f"{DOMYLAND_API_BASE_URL}/orders/{order_id}/status",
            json=req_body,
            headers=_get_domyland_headers(auth_token),
        )
        response_data = response.json()

        if not response.ok:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Order status UPDATE: {response_data}",
            )

        return response_data, req_body

    except Exception as e:
        error_str = str(e)
        logger.error(
            f"Error occurred while updating order with ID {order_id}: {error_str}"
        )
        logger.error(f"Wait {WAIT_TIME_IN_SEC} sec and try again..")
        time.sleep(WAIT_TIME_IN_SEC)

        logger.error(f"Timeout passed, try update order with ID {order_id} again")
        return _update_order_status_details(
            order_id=order_id,
            responsible_dept_id=responsible_dept_id,
            order_status_id=order_status_id,
            responsible_users_ids=responsible_users_ids,
            inspector_users_ids=inspector_users_ids,
        )


def _send_message_to_internal_chat(order_id: int, message: str) -> tuple[dict, dict]:
    # Authorize in Domyland API
    auth_token = _get_auth_token()

    req_body = {
        "orderId": order_id,
        "text": message,
        "isImportant": False,
    }

    # Send message to internal chat
    response = requests.post(
        url=f"{DOMYLAND_API_BASE_URL}/order-comments",
        json=req_body,
        headers=_get_domyland_headers(auth_token),
    )
    response_data = response.json()

    if not response.ok:
        raise HTTPException(
            status_code=response.status_code,
            detail=f"Order internal chat POST: {response_data}",
        )

    return response_data, req_body


# def _get_order_emergency(
#     prompt: str,
#     client: str,
#     query: str,
# ) -> str:
#     try:
#         chain = get_order_classification_chain(
#             prompt_template=prompt,
#             client=client,
#         )
#         order_emergency: str = chain.run(query=query)
#         return order_emergency
#     except RateLimitError:
#         logger.info(f"Wait {WAIT_TIME_IN_SEC} seconds and try again")
#         time.sleep(WAIT_TIME_IN_SEC)
#         logger.info(
#             f"Timeout passed, try to classify order '{query}' of '{client}' again"
#         )

#         return _get_order_emergency(
#             prompt=prompt,
#             client=client,
#             query=query,
#         )


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
                detail=f"Order with ID {order_id} was already classified, "
                       f"history record ID {saved_record.id}",
            )

        # Check if order status is not "in progress"
        if order_status_id != OrderStatusID.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Order with ID {order_id} has status ID {order_status_id}, "
                       f"but status ID {OrderStatusID.PENDING} required",
            )

        # Check if order is new (created)
        if alert_type_id != AlertTypeID.NEW_ORDER:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Order with ID {order_id} has alert type ID {alert_type_id}, "
                       f"but status ID {AlertTypeID.NEW_ORDER} required",
            )

        config = get_default_config(
            client=client,
        )

        # Check if default config exists
        if config is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Default order classification config "
                       f"(with ID {DEFAULT_CONFIG_ID} and client '{client}') not found",
            )

        config_id = config.id
        # Is needed to classify order
        is_use_order_classification = config.is_use_order_classification
        # Is needed to update order in Domyland
        # (blocked by is_use_order_classification)
        is_use_order_updating = (
            config.is_use_order_updating
            and is_use_order_classification
        )

        # Message for response fields disabled by config
        disabled_field_msg = (
            f"skipped by order classification config with ID {config_id}"
        )

        # Get order details
        order_details = _get_order_details_by_id(order_id)
        history_record.order_details = order_details.dict()

        # Get resident query (comment)
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
        is_order_address_empty = (
            is_order_address_exists
            and not bool(order_address.strip())
        )

        if not is_order_address_exists or is_order_address_empty:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Order with ID {order_id} has no address, "
                       f"cannot find responsible UDS",
            )

        # Get classes with rules from config
        # And check if this param exists
        rules_by_classes = config.rules_by_classes

        if rules_by_classes is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Classes with rules and params in config "
                       f"with ID {config.id} not found"
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
            is_emergency = order_class.strip() == "аварийная"

        # TODO: update 'is_emergency' param usage

        # Update order emergency class in Domyland
        if is_emergency and is_use_order_classification:
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
                    detail=f"Cannot find responsible UDS for order "
                           f"with ID {order_id} and address '{order_address}'",
                )

            history_record.responsible_user_id = responsible_uds.user_id

            # Get order class params
            class_params = _get_class_params(
                rules_by_classes=rules_by_classes,
                class_name_to_find=order_class,
            )

            is_use_order_with_this_class_updating = None
            if class_params is not None:
                is_use_order_with_this_class_updating = class_params.is_use_order_updating

            is_uds_disabled = responsible_uds.is_disabled

            # Update order responsible user is enabled
            if (
                is_use_order_updating
                and is_use_order_with_this_class_updating
                and not is_uds_disabled
            ):
                response, request_body = _update_order_status_details(
                    order_id=order_id,
                    responsible_dept_id=RESPONSIBLE_DEPT_ID,
                    # Update order status to "В работе"
                    order_status_id=OrderStatusID.IN_PROGRESS,
                    # Set responsible user to UDS
                    responsible_users_ids=[int(responsible_uds.user_id)],
                    # Update order inspector to AI Account
                    inspector_users_ids=[AI_USER_ID],
                )

                # Mark order as processed by AI
                _send_message_to_internal_chat(
                    order_id=order_id,
                    message=ORDER_PROCESSED_BY_AI_MESSAGE,
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
    # Test order id - 3196509
    # Real order id - 3191519
    order_id = 3197122

    # order_details = _get_order_details_by_id(order_id)
    # logger.debug(f"Order {order_id} details: {order_details}")

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
    #
    # users_ids_list = _get_responsible_users_ids_by_order_address(order_address)
    # logger.debug(f"Responsible users IDs: {users_ids_list}")

    # config = get_default_config()
    # logger.debug(f"Order Classification config:\n{config}\n")
    #
    # responsible_uds_list = [
    #     UDS(**responsible_uds)
    #     for responsible_uds in config.responsible_users
    # ]
    # logger.debug(f"Responsible UDS list:\n{responsible_uds_list}\n")

    # df = DataFrame(responsible_uds_list)
    # df["address_list"] = df["address_list"].apply(lambda x: "\n".join(x))
    # df.to_excel(f"./ЕДС c адресам {datetime.now()}.xlsx", index=False)
