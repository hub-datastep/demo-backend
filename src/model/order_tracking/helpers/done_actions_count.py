from scheme.order_tracking.order_tracking_task_scheme import OrderTrackingTaskActinLog


def get_done_actions_count(
    action_name: str,
    logs_list: list[OrderTrackingTaskActinLog],
) -> int:
    """
    Get successfully done action by logs names.
    """

    # Count actions from logs
    count: int = 0
    for log in logs_list:
        # Check if log name matches and was successful
        if log.name == action_name and not log.is_error:
            count += 1

    return count
