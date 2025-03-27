import time
import traceback

from fastapi import HTTPException
from loguru import logger
from sqlmodel import Session

from infra.database import engine
from model.order_tracking.task_tracking_model import process_order_tracking_task
from repository.order_tracking import order_tracking_task_repository

if __name__ == "__main__":
    while True:
        try:
            with Session(engine) as session:
                tasks_list = order_tracking_task_repository.get_uncompleted(
                    session=session,
                )
                # logger.debug(f"Tasks list: {tasks_list}")
                logger.debug(f"Tasks count: {len(tasks_list)}")

                for task in tasks_list:
                    result = process_order_tracking_task(
                        session=session,
                        task=task,
                    )
                    print(result)

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

        time.sleep(30)
