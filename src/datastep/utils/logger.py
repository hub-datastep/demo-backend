from datetime import datetime
import logging

today = datetime.now().strftime("%m-%d-%Y")

logging.basicConfig(
    level=logging.INFO,
    filename=f"{today}.log",
    filemode="a",
    format="%(asctime)s %(levelname)s %(message)s"
)
