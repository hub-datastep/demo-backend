import os
import json

from dotenv import load_dotenv

load_dotenv()

config_name = os.getenv("CONFIG")

with open(f"config/{config_name}.json", "r") as file:
    config = json.load(file)
