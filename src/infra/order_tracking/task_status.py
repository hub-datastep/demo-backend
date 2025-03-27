class OrderTrackingTaskStatus:
    PENDING = "Pending"
    WAITING_ACTION_TIME = "Waiting Action Time"
    TRACKING = "Tracking"
    COMPLETED = "Completed"
    FAILED = "Failed"


ORDER_TASK_NOT_TRACKING_STATUSES = [
    OrderTrackingTaskStatus.COMPLETED,
]
