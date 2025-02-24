from loguru import logger
from fastapi.encoders import jsonable_encoder
from datetime import datetime

# Получаем текущую дату и время для имени файла
current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
log_filename = f"order_logs_{current_time}.log"

# Настроим логгер с кастомным форматом
order_logger = logger.bind(function="get_order_details")
order_logger.add(log_filename, 
                 level="INFO",        # Уровень логирования
                 format="{time:YYYY-MM-DD HH:mm:ss} | {message}")  # Убираем лишнюю информацию

def get_order_details(r, url):
    body_json = jsonable_encoder(r)
    # Логи из этой функции будут идти только в файл с датой и временем
    order_logger.info(f"WEBHOOK | {url}: {body_json}")
    return
