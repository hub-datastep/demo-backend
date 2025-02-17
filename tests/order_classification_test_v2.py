import importlib
import os
from datetime import datetime

from loguru import logger
from openpyxl import load_workbook
from openpyxl.utils.dataframe import dataframe_to_rows
from pandas import DataFrame, ExcelWriter, read_excel
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from tqdm import tqdm

from configs.env import env
from services.google_sheets_service import get_test_cases

TESTS_ORDER_CLASSIFICATION_SPREADSHEET_NAME = env.TESTS_SPREADSHEET_NAME
TESTS_ORDER_CLASSIFICATION_TABLE_NAME = env.TESTS_TABLE_NAME

# Эмулируем правила для теста.
# В реальном сценарии — загрузка из базы данных
RULES_BY_CLASSES = {
    "Охрана": {
        "rules": [
            "Нужно предоставить пропуск для автомобиля.",
            "Пропустить автомобиль на разгрузку.",
            "Пропуск для человека, требуется допуск.",
            "Проблемы с парковкой или занятость места.",
            "Нарушение тишины или шум.",
            "Проблемы с парковкой в проезде.",
            "Нарушение работы охраны (например, не выгнали авто).",
            "Пожарная безопасность или технические проблемы (например, не закрыта "
            "дверь).",
            "Пропуск на парковку ограничен или есть задолженность.",
            "Проблемы с парковкой из-за неправильно припаркованных машин.",
            "Вопросы безопасности (например, посторонние лица в квартире).",
            "Поступление потерянных вещей (например, потеря сумки).",
            "Воняет или есть проблемы с загрязнением воздуха в подъезде.",
            "Все заявки связанные с парковкой, паркингом и вопросом охраны."
        ],
        "is_use_classification": True,
        "is_use_order_updating": False,
    },
    "Домофон": {
        "rules": [
            "Приложение не получает звонки с домофона или получает их с задержкой.",
            "Невозможно ответить на звонок через приложение или сбрасывается звонок.",
            "Не работает кнопка на домофоне или не реагирует на нажатие.",
            "Электронный замок не открывает дверь с карты или отпечатка пальца.",
            "Не работает панель доступа на этажах или на парковке.",
            "Не открывается дверь с помощью магнита, карты или отпечатка пальца.",
            "Не работает кнопка выхода или замок не срабатывает при выходе.",
            "Домофон не срабатывает при вызове или не передает звонки.",
            "Приложение не позволяет открыть дверь, несмотря на поступивший звонок.",
            "Не срабатывает панель доступа при выходе из лифтового холла или паркинга.",
            "Требуется настройка или ремонт домофона.",
            "Требуется установка домофона.",
            "Проблемы с настройкой домофона через приложение.",
            "Неисправность с ключами или карты для домофона.",
            "Все заявки связанные с домофоном, ключами для его открытия и "
            "взаимодействием приложения и домофона."
        ],
        "is_use_classification": True,
        "is_use_order_updating": False
    },
    "Клининг": {
        "rules": [
            "Требуется уборка пола (включая лифты и коридоры)",
            "Требуется уборка стен и других поверхностей (включая стены лифтов)",
            "Требуется уборка мусора (в том числе больших объектов, таких как паллеты "
            "или арматура)",
            "Требуется уборка в мусорокамерах или местах с загрязнениями (лужи, грязь)",
            "Требуется уборка в определённых зонах (например, возле входных дверей, "
            "в холле или паркинге)",
            "Уборка после покраски (снятие грязной пленки)",
            "уборка придомовой территории от снега и льда",
            "Систематическое отсутствие уборки в указанных зонах (например, на этажах "
            "или в определённых корпусах)",
            "Требуется удаление или очистка территорий от опасных объектов (например, "
            "крысиный яд)",
            "Уборка на долгосрочной основе не проводится в указанных местах (например, "
            "на нескольких этажах)",
            "Все заявки связанные с уборкой и загрязнениями."
        ],
        "is_use_classification": True,
        "is_use_order_updating": False
    },
    "Другой класс": {
        "rules": [
            "Проблемы с водоснабжением на уровне квартир, если проблема исключительно в "
            "счетчиках",
            "Неисправность в зоне ответственности собственника, например неисправен "
            "смеситель и он не закрывается.",
            "Протечка окон, оконных рам, стеклопакетов, откосов - протечка всего, "
            "что не относится инженерным системам (например: труб, кранов, батарей).",
            "Жалобы на качество воды: ржавая, желтая, грязная.",
            "Не работает вентиляция.",
            "Внутренние заявки, заводимые сотрудниками диспетчерской, например: "
            "мониторинг БМС, проверка связи АПС и подобное.",
            "Всё, что никак не получается отнести к остальным классам (Охрана, "
            "Аварийная, Клининг, Домофоны)"
        ],
        "is_use_classification": True,
        "is_use_order_updating": False
    },
    "Аварийная": {
        "rules": [
            "Неисправность лифтов, за исключением консультаций и вопросов по "
            "внутреннему убранству кабины. (лифты в домах могут обозначаться буквами ("
            "A, B, C, D и тд), поэтому иногда жильцы говорят вместо лифта, "
            "просто название буквы. Пример “не работает D” + люди иногда называют "
            "пассажирский лифт сокращенно - “ПЛ” + люди иногда сокращают заявку и не "
            "пишут слово лифт - “не работает грузовой”)",
            "Протечки и повреждения инженерных систем (труб, кранов, батарей).",
            "Нет ХВС (холодное водоснабжение) или ГВС (горячее водоснабжение).",
            "Пахнет из канализации или она засорена.",
            "Нет ЭЭ (электроэнергии), света во всей квартире, этаже, доме, территории "
            "ЖК.",
            "Искры из электросети, например из розетки.",
            "Выбило щиток, автомат.",
            "Сработала ПС (пожарная сигнализация), неважно ложное срабатывание или нет.",
            "Возгорание урны.",
            "Указана критическая поломка, которая негативно влияет одновременно на "
            "большое количество людей или несёт угрозу жизни или имуществу и которая "
            "уже произошла. Необоснованные опасения жильцов не учитываются."
        ],
        "is_use_classification": True,
        "is_use_order_updating": True
    }
}

# Конфиг с которым проводится тесты
# На логику работы программы ни как не влияет
# Сохраняется в отдельный лист таблицы с результатами
# Нужен для описания эксперимента,
# чтобы лучше было видно от каких вводных зависел рез-ат
# Заполнить конфиг вручную (можно добавлять новые параметры в этот дикт, специально
# сделан нетипизированным)
TESTING_CONFIG = {
    "llm_model": "GPT-4o-mini",
    "llm_provider": "Azure",
    "test_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "algorithm_description": "Классификация заявок с использованием многоуровневой "
                             "проверки правил. Добавил класс 'Другой класс'. Обновил "
                             "правила аварийных, клинига. Добавил 5 примеров размышлений",
    "rules_by_classes": RULES_BY_CLASSES,
    "TESTS_ORDER_CLASSIFICATION_SPREADSHEET_NAME":
        TESTS_ORDER_CLASSIFICATION_SPREADSHEET_NAME,
    "TESTS_ORDER_CLASSIFICATION_TABLE_NAME": TESTS_ORDER_CLASSIFICATION_TABLE_NAME,
}

# Колонки, которые обязательно должны быть в тест-кейсах
REQUIRED_COLUMNS = [
    "Order Query",
    "Correct Class",
]


def load_test_cases() -> list[dict]:
    """
    Загружает тест-кейсы из Google Sheets.
    :return: Список тестовых кейсов в виде словарей.
    """
    try:
        test_cases = get_test_cases(
            spreadsheet_name=TESTS_ORDER_CLASSIFICATION_SPREADSHEET_NAME,
            sheet_name=TESTS_ORDER_CLASSIFICATION_TABLE_NAME,
        )
        logger.info(
            f"Тест-кейсы успешно загружены. Количество записей: {len(test_cases)}."
        )
        return test_cases
    except Exception as e:
        logger.error(f"Ошибка загрузки тест-кейсов: {e}")
        return []


def is_test_case_valid(
    test_case: dict,
    is_for_experiments: bool = False,
) -> bool:
    """
    Проверяет наличие обязательных полей в тест-кейсе.

    :param test_case: Один тест-кейс.
    :param is_for_experiments: Флаг, с помощью которого можно отфильтровать тест-кейсы
    для экспериментов.

    :return: True, если кейс валиден, иначе False.
    """

    # Проверка на наличие полей
    for column in REQUIRED_COLUMNS:
        # Проверяем, что у тест-кейса есть необходимые колонки
        if (
            column not in test_case
            or not test_case[column]
            or str(test_case[column]).strip() == ""
        ):
            logger.warning(f"Тест-кейс невалиден: отсутствует или пустое поле '{column}'")
            return False

        test_case_id = test_case["Test Case ID"]
        testing_class = str(test_case["Класс для тестирования"]).lower()
        # Отфильтровываем кейсы, которые требуют уточнения
        if testing_class == "требует уточнения".lower():
            logger.warning(f"Тест-кейс {test_case_id} невалиден и трубует уточнения")
            return False

        # Выбираем тест-кейсы, которые нужны для экспериментов
        if is_for_experiments:
            if testing_class.startswith("топчик".lower()):
                return True
            else:
                return False

    return True


def load_prediction_function(module_name: str, function_name: str):
    """
    Динамически загружает функцию предсказания из указанного модуля.

    :param module_name: Название модуля (файл в папке experiments).
    :param function_name: Имя функции в модуле.

    :return: Ссылка на функцию.
    """
    try:
        module = importlib.import_module(f"{module_name}")
        return getattr(module, function_name)
    except (ModuleNotFoundError, AttributeError) as e:
        logger.error(f"Ошибка при загрузке функции {function_name} из {module_name}: {e}")
        raise


def process_test_case(
    test_case: dict,
    predict_function: callable,
    **kwargs,
) -> dict:
    """
    Обрабатывает тест-кейс с использованием переданной функции предсказания.

    :param test_case: Один тест-кейс.
    :param predict_function: Функция предсказания.
    :param kwargs: Дополнительные аргументы для функции предсказания.

    :return: Результаты выполнения с динамическими параметрами.
    """
    order_query = test_case["Order Query"]
    start_time = datetime.now()

    try:
        # Вызов функции предсказания
        prediction_result = predict_function(order_query, **kwargs)

        # Проверяем, если результат — объект, преобразуем его в словарь
        if hasattr(prediction_result, "__dict__"):
            prediction_result = vars(prediction_result)  # Преобразуем объект в словарь

        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()

        # Сбор гарантированных параметров
        result = {
            "Order Query": order_query,
            "Correct Class": test_case["Correct Class"],
            "Predicted Class": prediction_result[
                "most_relevant_class_response"
            ].order_class,
            "Processing Time": f"{processing_time} сек",
            "Test Case ID": test_case["Test Case ID"],
            "Order ID": test_case["Order ID"]
        }

        # Добавляем все остальные параметры из результата
        for key, value in prediction_result.items():
            if key not in result:  # Избегаем перезаписи гарантированных полей
                result[key] = value

        return result

    except Exception as e:
        logger.error(
            f"Ошибка при обработке запроса '{order_query}': "
            f"{e}: {e.with_traceback(e.__traceback__)}"
        )
        return {
            "Order Query": order_query,
            "Correct Class": test_case["Correct Class"],
            "Predicted Class": None,
            "LLM Comment": f"Ошибка: {str(e)}",
            "Processing Time": "N/A",
            "Test Case ID": test_case["Test Case ID"],
            "Order ID": test_case["Order ID"]
        }


def evaluate_predictions(results: list):
    """
    Оценивает результаты предсказаний на основе основных метрик.

    :param results: Список тест-кейсов с полями Predicted Class и Correct Class.
    """
    # Извлечение истинных и предсказанных классов
    true_classes = [res["Correct Class"]
                    for res in results if res["Predicted Class"]]
    predicted_classes = [res["Predicted Class"]
                         for res in results if res["Predicted Class"]]

    # Проверка, что у нас есть данные для анализа
    if not true_classes or not predicted_classes:
        logger.error("Недостаточно данных для подсчёта метрик.")
        return

    # Подсчёт Accuracy
    accuracy = accuracy_score(true_classes, predicted_classes)
    logger.info(f"Accuracy: {accuracy:.2f}")

    # Генерация отчета по основным метрикам (Precision, Recall, F1)
    report = classification_report(
        true_classes, predicted_classes, output_dict=True
    )
    logger.info(
        "Краткий отчет по метрикам:\n" +
        DataFrame(report).transpose().to_string()
    )

    # Матрица ошибок
    confusion = confusion_matrix(true_classes, predicted_classes)
    logger.info("Confusion Matrix:\n" + DataFrame(confusion).to_string())


def add_success_metric(result: dict) -> dict:
    """
    Добавляет метрику успешности предсказания (1 или 0).
    """
    if result["Predicted Class"] == result["Correct Class"]:
        result["Success Metric"] = 1
    elif (
        result["Predicted Class"] == "Обычная"
        and result["Correct Class"] == "Другой класс"
    ):
        result["Success Metric"] = 1
    else:
        result["Success Metric"] = 0
    return result


def _calculate_overall_metrics(results: list) -> dict:
    """
    Подсчитывает общие метрики (Accuracy, Precision, Recall, F1-score).

    :param results: Список тест-кейсов с результатами предсказаний.

    :return: Словарь с метриками.
    """
    true_classes = [res["Correct Class"] for res in results]
    predicted_classes = [res["Predicted Class"] for res in results]

    accuracy = accuracy_score(true_classes, predicted_classes)
    report = classification_report(true_classes, predicted_classes, output_dict=True)

    return {
        "Accuracy": accuracy,
        "Precision (weighted)": report["weighted avg"]["precision"],
        "Recall (weighted)": report["weighted avg"]["recall"],
        "F1-score (weighted)": report["weighted avg"]["f1-score"]
    }


def save_results_to_excel(
    results: list,
    metrics: dict,
    config: dict,
    file_name: str = None,
):
    """
    Сохраняет результаты тестов и метрики в xlsx-файл.

    :param results: Список результатов тестирования.
    :param metrics: Общие метрики тестирования.
    :param config: Конфигурация тестирования.
    :param file_name: Название файла. Если не указано, формируется автоматически.
    """
    if not file_name:
        now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        file_name = f"test_results_{now}.xlsx"

    # Преобразуем результаты в DataFrame
    results_df = DataFrame(results)

    # Формирование DataFrame для конфигурации
    config_df = DataFrame([{key: value for key, value in config.items()}])

    # Формирование DataFrame для метрик
    metrics_df = DataFrame([metrics])

    # Запись в xlsx-файл
    with ExcelWriter(file_name, engine="openpyxl") as writer:
        results_df.to_excel(writer, sheet_name="Results", index=False)
        config_df.to_excel(writer, sheet_name="Test Config", index=False)
        metrics_df.to_excel(writer, sheet_name="Metrics Summary", index=False)

    logger.info(f"Результаты тестирования сохранены в файл: {file_name}")


def initialize_results_file(file_name: str, columns: list):
    """
    Создает новый xlsx файл с заголовками, если он не существует.
    """
    DataFrame(columns=columns).to_excel(file_name, sheet_name="Results", index=False)
    logger.info(f"Создан новый файл для сохранения результатов: {file_name}")


def append_result_to_excel(file_name: str, result: dict):
    """
    Добавляет одну строку с результатами в существующий xlsx файл.
    Если файл не существует, создает его и добавляет заголовки.
    """
    # Преобразуем все сложные объекты в строки
    result_cleaned = {
        key: (str(value) if not isinstance(value, (int, float, str)) else value)
        for key, value in result.items()}
    result_df = DataFrame([result_cleaned])

    # Если файл не существует, создаём его с заголовками
    if not os.path.exists(file_name):
        result_df.to_excel(file_name, sheet_name="Results", index=False)
        logger.info(f"Создан новый файл с заголовками из первого тест-кейса: {file_name}")
    else:
        # Загружаем существующий файл и лист
        book = load_workbook(file_name)
        sheet = book["Results"]

        # Преобразуем DataFrame в строки и добавляем их в лист
        for row in dataframe_to_rows(result_df, index=False, header=False):
            sheet.append(row)

        # Сохраняем изменения
        book.save(file_name)
        book.close()

    logger.info(f"Результат добавлен в файл: {file_name}")


def calculate_overall_metrics(results_file: str) -> dict:
    """
    Подсчитывает метрики по всем результатам из xlsx-файла.
    """
    results_df = read_excel(results_file, sheet_name="Results")

    true_classes = results_df["Correct Class"]
    predicted_classes = results_df["Predicted Class"]

    accuracy = accuracy_score(true_classes, predicted_classes)
    report = classification_report(true_classes, predicted_classes, output_dict=True)

    return {
        "Accuracy": accuracy,
        "Precision (weighted)": report["weighted avg"]["precision"],
        "Recall (weighted)": report["weighted avg"]["recall"],
        "F1-score (weighted)": report["weighted avg"]["f1-score"]
    }


def save_metrics_and_config_to_excel(
    file_name: str,
    metrics: dict,
    config: dict,
):
    """
    Сохраняет метрики на отдельный лист в xlsx-файле.
    Сохраняет конфиг тестирования в отдельный лист.
    """
    # Сохраняем метрики
    metrics_df = DataFrame([metrics])
    with ExcelWriter(file_name, mode="a", engine="openpyxl") as writer:
        metrics_df.to_excel(writer, sheet_name="Metrics Summary", index=False)

    # Сохраняем конфиг
    config_df = DataFrame([{key: value for key, value in config.items()}])
    with ExcelWriter(file_name, mode="a", engine="openpyxl") as writer:
        config_df.to_excel(writer, sheet_name="Testing Config", index=False)

    logger.success(f"Результаты успешно сохранены в файл: {file_name}.")


if __name__ == "__main__":
    # Инициализация названия файла результатов
    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    file_name = f"test_results_{now}.xlsx"

    # Шаг 1: Загрузка тест-кейсов
    test_cases = load_test_cases()

    # Шаг 2: Валидация данных
    valid_test_cases = [
                           case for case in test_cases
                           if is_test_case_valid(
            test_case=case,
            # Получаем тест-кейсы для экспериментов
            is_for_experiments=True,
        )
                       ][:5]
    logger.info(f"Валидные тест-кейсы: {len(valid_test_cases)} из {len(test_cases)}.")

    # Пример вывода валидных тест-кейсов
    for i, case in enumerate(valid_test_cases[:5], start=1):
        logger.info(f"Тест-кейс {i}: {case}")

    # Загружаем динамическую функцию предсказания из модуля
    get_order_class_predict_function = load_prediction_function(
        "order_classification.v6.modules.chains.order_multi_classification_chain",
        "get_order_class",
    )

    # Шаг 3: Прогон через чейн
    # results = []
    total_cases = len(valid_test_cases)
    for idx, test_case in enumerate(tqdm(valid_test_cases, desc="Обработка тест-кейсов")):
        result = process_test_case(
            test_case=test_case,
            predict_function=get_order_class_predict_function,
            rules_by_classes=RULES_BY_CLASSES,
        )
        # results.append(result)
        result = add_success_metric(result)
        append_result_to_excel(file_name, result)
        logger.info(
            f"[{idx + 1}/{total_cases}] Обработан тест-кейс: "
            f"{result['Order Query']} -> {result['Predicted Class']}"
        )

    # Шаг 4: Подсчет и сохранение метрик
    overall_metrics = calculate_overall_metrics(file_name)
    save_metrics_and_config_to_excel(file_name, overall_metrics, TESTING_CONFIG)
