class OrderTrackingTaskAction:
    # Order API Actions
    FETCH_ORDER_DETAILS = "Fetch Order Details"

    # Send Message Actions
    SEND_NEW_ORDER_MESSAGE = "Send New Order Message"
    SEND_SLA_PING_MESSAGE = "Send SLA Ping-Message"


TIME_DEPENDENT_ACTIONS = [OrderTrackingTaskAction.SEND_SLA_PING_MESSAGE]
