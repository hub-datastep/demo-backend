# Единицы времени и их склонения
_TIME_UNITS = [
    (60 * 60 * 24 * 30, "месяц", "месяца", "месяцев"),
    (60 * 60 * 24, "день", "дня", "дней"),
    (60 * 60, "час", "часа", "часов"),
    (60, "минута", "минуты", "минут"),
    (1, "секунда", "секунды", "секунд"),
]


def get_time_str_from_seconds(seconds: int) -> str | None:
    for unit_seconds, singular, dual, plural in _TIME_UNITS:
        value = seconds // unit_seconds

        if value > 0:
            # Определяем правильное склонение
            if value % 10 == 1 and value % 100 != 11:
                return f"{value} {singular}"
            elif 2 <= value % 10 <= 4 and (value % 100 < 10 or value % 100 >= 20):
                return f"{value} {dual}"
            else:
                return f"{value} {plural}"


if __name__ == "__main__":
    test_seconds = 17511966
    print(get_time_str_from_seconds(test_seconds))
