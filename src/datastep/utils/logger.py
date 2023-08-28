from datetime import datetime
import logging

today = datetime.now().strftime("%m-%d-%Y_%H:%M")

logging.basicConfig(
    level=logging.ERROR,
    filename=f"../logs/{today}.log",
    filemode="a",
    format="[%(asctime)s][%(levelname)s][%(message)s]"
)
