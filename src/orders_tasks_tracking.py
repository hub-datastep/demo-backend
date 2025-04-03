import time

from loguru import logger

from model.order_tracking.task_tracking_model import process_order_tracking_task
from repository.order_tracking import order_tracking_task_repository

if __name__ == "__main__":
    while True:
        tasks_list = order_tracking_task_repository.get_uncompleted()
        logger.debug(f"Tasks count: {len(tasks_list)}")

        for task in tasks_list:
            result = process_order_tracking_task(
                task=task,
            )
            print(result)

        time.sleep(30)
