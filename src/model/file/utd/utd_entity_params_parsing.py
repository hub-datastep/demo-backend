import re
from datetime import date, datetime

MONTHS_NAME_AND_NUMBER_STR = {
    "января": "01",
    "февраля": "02",
    "марта": "03",
    "апреля": "04",
    "мая": "05",
    "июня": "06",
    "июля": "07",
    "августа": "08",
    "сентября": "09",
    "октября": "10",
    "ноября": "11",
    "декабря": "12",
}

DATE_FORMAT = "%d.%m.%Y"


def normalize_date(date_str: str) -> date | None:
    """
    Функция для нормализации дат в формате DD.MM.YYYY и тип datetime.date
    """

    # Init Params
    normalized_date = None

    # Patterns
    # Date format like: 01 января 2021
    date_pattern1 = r"(\d{1,2})\s+([а-яА-Я]+)\s+(\d{4})"
    # Date format like: 01.01.2021
    date_pattern2 = r"(\d{1,2})\.(\d{1,2})\.(\d{4})"

    # Normalize Date
    date_match1 = re.search(
        pattern=date_pattern1,
        string=date_str,
    )
    date_match2 = re.search(
        pattern=date_pattern2,
        string=date_str,
    )
    date_match = date_match1 or date_match2
    if date_match1 or date_match2:
        day = date_match.group(1)
        month = date_match.group(2)
        year = date_match.group(3)

        if date_match1:
            month = MONTHS_NAME_AND_NUMBER_STR.get(month.lower())

        date_string = f"{day}.{month}.{year}"
        normalized_date = datetime.strptime(date_string, DATE_FORMAT).date()

    return normalized_date


def format_param(
    param: str,
    to_number: bool | None = False,
) -> str | int | float | None:
    symbols_to_remove = r"[\s\%\-\n]+"
    param = re.sub(symbols_to_remove, "", param)
    param = param.strip()

    if not param:
        param = None

    if param and to_number:
        param = float(param) if "." in param else int(param)

    return param


def get_utd_number(pages_text: str):
    """
    Parse UTD number from pages text
    """

    # Init Params
    utd_number = None

    # Patterns
    utd_number_pattern = r"Счет-фактура\s*№\s*([\w-]+)"

    # Parse Param
    utd_number_match = re.search(
        pattern=utd_number_pattern,
        string=pages_text,
        flags=re.IGNORECASE,
    )
    if utd_number_match:
        utd_number = utd_number_match.group(1)

    return utd_number


def get_utd_date_str(pages_text: str):
    """
    Parse UTD date from pages text
    """

    # Init Params
    utd_date_str = None

    # Patterns
    utd_date_str_pattern = r"Счет-фактура[^\n]*?от\s*(\d{1,2}[\.\s][а-яА-Я]+[\.\s]\d{4}|\d{2}\.\d{2}\.\d{4})"

    # Parse Param
    utd_date_str_match = re.search(
        pattern=utd_date_str_pattern,
        string=pages_text,
        flags=re.IGNORECASE,
    )
    if utd_date_str_match:
        utd_date_str = utd_date_str_match.group(1)

    return utd_date_str


def get_supplier_inn(pages_text: str) -> str | None:
    """
    Parse supplier INN from UTD pages text
    """

    # Init Params
    supplier_inn = None

    # Patterns
    supplier_inn_pattern = r"ИНН[\/КПП продавца]*[:\s]*([0-9]{10})"

    # Parse Param
    match = re.search(
        pattern=supplier_inn_pattern,
        string=pages_text,
        flags=re.IGNORECASE,
    )
    if match:
        supplier_inn = match.group(1)

    return supplier_inn


def get_organization_inn(pages_text: str) -> str | None:
    """
    Parse organization INN from UTD pages text
    """

    # Init Params
    organization_inn = None

    # Patterns
    organization_inn_pattern = r"ИНН[\/КПП]* покупателя:?[\s\S]*?(\d{10,12})"
    buyer_inn_pattern = r"ИНН[\/КПП]*?[\s\S]*?(\d{10,12})"

    # Parse Param
    organization_inn_match = re.search(
        pattern=organization_inn_pattern,
        string=pages_text,
        flags=re.IGNORECASE,
    )
    if organization_inn_match:
        organization_inn = organization_inn_match.group(1)
    else:
        buyer_inn_match = re.search(
            pattern=buyer_inn_pattern,
            string=pages_text[900:],
            flags=re.IGNORECASE,
        )
        if buyer_inn_match:
            organization_inn = buyer_inn_match.group(1)

    return organization_inn


def get_correction_params(pages_text: str) -> tuple[str, str] | None:
    """
    Parse correction number and date from UTD pages text
    """

    # Init Params
    correction_number = None
    correction_date = None

    # Patterns
    correction_pattern = r"Исправление\s+№\s+(\S+)\s+от\s+(\d{2}\.\d{2}\.\d{4})"

    # Parse Param
    correction_match = re.search(
        pattern=correction_pattern,
        string=pages_text,
        flags=re.IGNORECASE,
    )
    if correction_match:
        correction_number = correction_match.group(1)
        correction_date = correction_match.group(2)

    return correction_number, correction_date


def get_contract_params(
    pages_text: str,
) -> tuple[str | None, str | None, str | None]:
    """
    Parse contract name and date from UTD pages text
    """

    # Init Params
    contract_number = None
    contract_name = None
    contract_date = None

    # Patterns
    contract_pattern = (
        r"(основ.+передач.+сдач.+получ.+при[её]м)\S*\s*((.+)\s*"
        r"от\s*(\d{1,2}\.\d{1,2}\.\d{2,4}|(\d{1,2})\s([а-яА-ЯёЁ]+)\s(\d{2,4})))"
    )

    # Parse Param
    contract_match = re.search(
        pattern=contract_pattern,
        string=pages_text,
        flags=re.IGNORECASE,
    )
    if contract_match:
        contract_name = contract_match.group(2)
        contract_date = contract_match.group(4)

    return contract_number, contract_name, contract_date
