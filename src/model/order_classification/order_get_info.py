from datetime import datetime
from pathlib import Path
import json

from loguru import logger

from infra.env import env
from util.json_serializing import serialize_obj


def get_order_details(body: dict, url: str) -> None:
    now = datetime.now()
    log_entry = serialize_obj(
        {
            "event_url": url,
            "request_body": body,
            "timestamp": now.isoformat(),
        }
    )
    logger.debug(log_entry)

    try:
        now_date = now.date()
        log_file_path = (
            f"{env.DATA_FOLDER_PATH}/orders-logs/orders-logs-{now_date}.json"
        )

        # Add log to file
        if Path(log_file_path).exists():
            # Save log
            with open(log_file_path, "r") as log_file:
                logs = json.load(log_file)
            with open(log_file_path, "w") as log_file:
                logs.append(log_entry)
                json.dump(logs, log_file, ensure_ascii=False)

        # Create full path & log file & add log to it
        else:
            # Create logs folder
            Path(log_file_path).parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            # Save log
            with open(log_file_path, "w") as log_file:
                json.dump([log_entry], log_file, ensure_ascii=False)
    except Exception:
        logger.error("Cannot save this log to JSON")
