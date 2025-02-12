def format_rules_list(rules: list[str]) -> str:
    """
    Собираем список правил в одну строку,
    где правила записаны в виде ненумерованного списка
    """
    formatted_rules = "\n".join([f"- {rule}" for rule in rules])
    return formatted_rules
