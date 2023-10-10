# TODO: придумать, как перенести из конфига строку подключения к базе в более безопасное время

import json
import os

from dotenv import load_dotenv

load_dotenv()

config_name = os.getenv("CONFIG")

dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, f"./{config_name}.json")

with open(filename, "r", encoding="utf-8") as file:
    config = json.load(file)
