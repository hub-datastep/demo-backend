import asyncio

from loguru import logger

from infra.kafka.brokers import kafka_broker
from middleware.kafka_middleware import with_kafka_broker_connection
from model.order_tracking.task_tracking_model import process_order_tracking_task
from repository.order_tracking.order_tracking_task_repository import (
    order_tracking_task_repository,
)

TRACKING_PERIOD_IN_SEC = 30


@with_kafka_broker_connection(kafka_broker)
async def main():
    while True:
        tasks_list = await order_tracking_task_repository.get_uncompleted()
        logger.debug(f"Tasks count: {len(tasks_list)}")

        # Process all tasks concurrently
        runs = [process_order_tracking_task(task=task) for task in tasks_list]
        await asyncio.gather(*runs)

        logger.debug(
            f"Wait {TRACKING_PERIOD_IN_SEC} seconds and check uncompleted tasks again..."
        )
        await asyncio.sleep(TRACKING_PERIOD_IN_SEC)


if __name__ == "__main__":
    asyncio.run(main())
