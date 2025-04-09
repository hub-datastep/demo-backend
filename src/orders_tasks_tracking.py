import asyncio

from loguru import logger

from infra.kafka.brokers import kafka_broker
from middleware.kafka_middleware import with_kafka_broker_connection
from model.order_tracking.task_tracking_model import process_order_tracking_task
from repository.order_tracking.order_tracking_task_repository import (
    order_tracking_task_repository,
)

_WAIT_TIME_IN_SEC = 30

_CHUNK_SIZE = 100


@with_kafka_broker_connection(kafka_broker)
async def main():
    while True:
        tasks_list = await order_tracking_task_repository.get_uncompleted()
        tasks_count = len(tasks_list)
        logger.debug(f"Tasks count: {tasks_count}")

        # Process tasks in chunks
        for i in range(0, tasks_count, _CHUNK_SIZE):
            tasks_chunk = tasks_list[i : i + _CHUNK_SIZE]
            runs = [process_order_tracking_task(task=task) for task in tasks_chunk]
            await asyncio.gather(*runs)

        logger.debug(
            f"Wait {_WAIT_TIME_IN_SEC} seconds and check uncompleted tasks again..."
        )
        await asyncio.sleep(_WAIT_TIME_IN_SEC)


if __name__ == "__main__":
    asyncio.run(main())
