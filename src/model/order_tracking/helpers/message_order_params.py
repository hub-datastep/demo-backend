from infra.domyland.order import (
    get_address_from_order_details,
    get_address_with_apartment_from_order_details,
    get_crm_order_url,
    get_query_from_order_details,
)
from scheme.order_classification.order_classification_scheme import (
    OrderDetails,
    OrderResponsibleUser,
)
from scheme.order_tracking.message_order_params_schema import MessageOrderParams
from util.dates import get_now_utc
from util.datetimes_formats import timestamp_to_datetime_str
from util.seconds_to_time_str import seconds_to_duration_str
from util.validation import value_or_empty_str


def get_order_params_for_message(
    order_details: OrderDetails,
) -> MessageOrderParams:
    """
    Extracts and formats Order params for Telegram message.

    See `MessageOrderParams` to find out returned params.
    """

    order = order_details.order
    order_id = order.id

    crm_url = get_crm_order_url(order_id=order_id)

    address: str = get_address_from_order_details(order_details=order_details)

    address_with_apartment: str | None = get_address_with_apartment_from_order_details(
        order_details=order_details,
        # Optional, so not raise error
        raise_error_if_not_found=False,
    )

    service_title: str = order.serviceTitle

    query: str | None = get_query_from_order_details(
        order_details=order_details,
        # Optional, so not raise error
        raise_error_if_not_found=False,
    )

    created_at_timestamp = order.createdAt
    created_at_str = timestamp_to_datetime_str(created_at_timestamp)

    responsible_users: list[OrderResponsibleUser] = order.responsibleUsers
    responsible_users_full_names = [
        value_or_empty_str(user.fullName) for user in responsible_users
    ]

    current_datetime = get_now_utc()
    current_timestamp = int(current_datetime.timestamp())
    sla_solve_timestamp = order.solveTimeSLA
    sla_left_time_in_sec: int | None = None
    if sla_solve_timestamp:
        sla_left_time_in_sec = sla_solve_timestamp - current_timestamp

    sla_time_text: str = ""
    if sla_left_time_in_sec is not None:
        sla_time_str = seconds_to_duration_str(seconds=abs(sla_left_time_in_sec))
        if sla_left_time_in_sec > 0:
            sla_time_text = sla_time_str
        else:
            sla_time_text = f"просрочен на {sla_time_str}"

    return (
        order_id,
        crm_url,
        value_or_empty_str(address),
        value_or_empty_str(address_with_apartment),
        value_or_empty_str(service_title),
        value_or_empty_str(query),
        value_or_empty_str(created_at_str),
        responsible_users_full_names,
        sla_solve_timestamp,
        sla_left_time_in_sec,
        sla_time_text,
    )
