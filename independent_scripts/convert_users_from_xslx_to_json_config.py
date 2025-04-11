# скрипт для перегонки таблички в конфиг юзеров
# ссылка на табличку https://docs.google.com/spreadsheets/d/1Empd-IZTw1Cy1xX2sD8p3TltN6Ga5PmXNCQzJJJAXBk/edit?gid=745753749#gid=745753749&fvid=53746111
# конфиг юзеров (таблица order_claasification_config -> responsible users) 

import pandas as pd
import json

# === НАСТРОЙКИ ===

EXCEL_FILE = "Чаты пилота.xlsx"  # Имя файла
SHEET_NAME = "ЖК Царская площадь"  # Название листа
OUTPUT_FILE = "responsible_users.json"  # Имя выходного JSON-файла

# === ШАБЛОНЫ ===

# Расписания по номеру
work_schedule_templates = {
    1: {
        "monday": {"start_at": "09:00", "finish_at": "18:00", "is_disabled": False},
        "tuesday": {"start_at": "09:00", "finish_at": "18:00", "is_disabled": False},
        "wednesday": {"start_at": "09:00", "finish_at": "18:00", "is_disabled": False},
        "thursday": {"start_at": "09:00", "finish_at": "18:00", "is_disabled": False},
        "friday": {"start_at": "09:00", "finish_at": "16:45", "is_disabled": False},
        "saturday": None,
        "sunday": None,
        "excluded": []
    },
    2: {
        "monday": None,
        "tuesday": {"start_at": "10:00", "finish_at": "19:00", "is_disabled": False},
        "wednesday": {"start_at": "10:00", "finish_at": "19:00", "is_disabled": False},
        "thursday": {"start_at": "10:00", "finish_at": "19:00", "is_disabled": False},
        "friday": {"start_at": "10:00", "finish_at": "19:00", "is_disabled": False},
        "saturday": {"start_at": "10:00", "finish_at": "16:00", "is_disabled": False},
        "sunday": None,
        "excluded": []
    },
    3: {
        "monday": {"start_at": "00:00", "finish_at": "23:59", "is_disabled": False},
        "tuesday": {"start_at": "00:00", "finish_at": "23:59", "is_disabled": False},
        "wednesday": {"start_at": "00:00", "finish_at": "23:59", "is_disabled": False},
        "thursday": {"start_at": "00:00", "finish_at": "23:59", "is_disabled": False},
        "friday": {"start_at": "00:00", "finish_at": "23:59", "is_disabled": False},
        "saturday": {"start_at": "00:00", "finish_at": "23:59", "is_disabled": False},
        "sunday": {"start_at": "00:00", "finish_at": "23:59", "is_disabled": False},
        "excluded": []
    }
}

# Данные общего чата
default_chat = {
    "name": "[prod] ЖК Царская Площадь",
    "chat_id": "-1002682849473"
}

# Адреса по умолчанию
default_address_list = [
    "Ленинградский пр-кт, 29/1",
    "Ленинградский пр-кт, 29/2",
    "Ленинградский пр-кт, 29/3",
    "Ленинградский пр-кт, 29/4",
    "Ленинградский пр-кт, 29/5"
]

# === ФУНКЦИЯ КОНВЕРТАЦИИ ===

def map_row_to_user(row):
    def safe_get(key):
        val = row.get(key)
        return None if pd.isna(val) else val

    # Определяем work_schedule по номеру
    schedule_num = safe_get("№ Часы работы")
    work_schedule = work_schedule_templates.get(int(schedule_num)) if schedule_num in [1, 2, 3] else None

    # Чистим thread_id
    thread_id = safe_get("Номер топика в ТГ чате")
    try:
        thread_id = int(thread_id) if thread_id is not None else None
    except ValueError:
        thread_id = None

    # Формируем чат
    chats = []
    if thread_id is not None:
        chats.append({
            "name": default_chat["name"],
            "chat_id": default_chat["chat_id"],
            "thread_id": thread_id,
            "is_disabled": False,
            "address_list": default_address_list
        })

    # Финальная структура пользователя
    return {
        "user_id": str(safe_get("ID аккаунта в домиленд")).strip(),
        "name": safe_get("ФИО"),
        "order_class": safe_get("какие категории заявок закрывает в Домиленд"),
        "telegram": {
            "username": str(safe_get("Аккаунт в ТГ")).strip().lstrip("@"),
            "chats": chats
        },
        "work_schedule": work_schedule
    }

# === ЗАПУСК ===

def main():
    df = pd.read_excel(EXCEL_FILE, sheet_name=SHEET_NAME)
    df = df[df["ID аккаунта в домиленд"].notna()]
    users = [map_row_to_user(row) for _, row in df.iterrows()]

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=4)

    print(f"✅ Готово! JSON сохранён в файл: {OUTPUT_FILE}")

# Если запускается как скрипт
if __name__ == "__main__":
    main()
