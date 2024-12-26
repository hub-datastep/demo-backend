from loguru import logger

from model.mapping.mapping_model import build_where_metadatas

# Тест-кейсы для Жёсткого Поиска
_HARD_SEARCH_TEST_CASES = [
    # Тест-кейс 1: Группа и жёсткий поиск
    {
        "group": "test_group",
        "brand": None,
        "view": None,
        "metadatas_list": None,
        "is_params_needed": False,
        "is_brand_needed": False,
        "is_view_needed": False,
        "expected_result": {"internal_group": "test_group"},
    },
    # Тест-кейс 2: Группа, бренд и жёсткий поиск
    {
        "group": "test_group",
        "brand": "test_brand",
        "view": None,
        "metadatas_list": None,
        "is_params_needed": False,
        "is_brand_needed": True,
        "is_view_needed": False,
        "expected_result": {
            "$and": [
                {"internal_group": "test_group"},
                {"brand": "test_brand"},
            ],
        },
    },
    # Тест-кейс 3: Группа, параметры и жёсткий поиск
    {
        "group": "test_group",
        "brand": None,
        "view": None,
        "metadatas_list": [
            {"param1": "value1"},
            {"param2": "value2"},
        ],
        "is_params_needed": True,
        "is_brand_needed": False,
        "is_view_needed": False,
        "expected_result": {
            "$and": [
                {"internal_group": "test_group"},
                {"param1": "value1"},
                {"param2": "value2"},
            ],
        },
    },
    # Тест-кейс 4: Группа, бренд, параметры и жёсткий поиск
    {
        "group": "test_group",
        "brand": "test_brand",
        "view": None,
        "metadatas_list": [
            {"param1": "value1"},
            {"param2": "value2"},
        ],
        "is_params_needed": True,
        "is_brand_needed": True,
        "is_view_needed": False,
        "expected_result": {
            "$and": [
                {"internal_group": "test_group"},
                {"param1": "value1"},
                {"param2": "value2"},
                {"brand": "test_brand"},
            ],
        },
    },
    # Тест-кейс 5: Группа, view и жёсткий поиск
    {
        "group": "test_group",
        "brand": None,
        "view": "test_view",
        "metadatas_list": None,
        "is_params_needed": False,
        "is_brand_needed": False,
        "is_view_needed": True,
        "expected_result": {
            "$and": [
                {"internal_group": "test_group"},
                {"view": "test_view"},
            ],
        },
    },
    # Тест-кейс 6: Группа, бренд, view и жёсткий поиск
    {
        "group": "test_group",
        "brand": "test_brand",
        "view": "test_view",
        "metadatas_list": None,
        "is_params_needed": False,
        "is_brand_needed": True,
        "is_view_needed": True,
        "expected_result": {
            "$and": [
                {"internal_group": "test_group"},
                {"brand": "test_brand"},
                {"view": "test_view"},
            ],
        },
    },
    # Тест-кейс 7: Группа, параметры, view и жёсткий поиск
    {
        "group": "test_group",
        "brand": None,
        "view": "test_view",
        "metadatas_list": [
            {"param1": "value1"},
            {"param2": "value2"},
        ],
        "is_params_needed": True,
        "is_brand_needed": False,
        "is_view_needed": True,
        "expected_result": {
            "$and": [
                {"internal_group": "test_group"},
                {"param1": "value1"},
                {"param2": "value2"},
                {"view": "test_view"},
            ],
        },
    },
    # Тест-кейс 8: Группа, бренд, параметры, view и жёсткий поиск
    {
        "group": "test_group",
        "brand": "test_brand",
        "view": "test_view",
        "metadatas_list": [
            {"param1": "value1"},
            {"param2": "value2"},
        ],
        "is_params_needed": True,
        "is_brand_needed": True,
        "is_view_needed": True,
        "expected_result": {
            "$and": [
                {"internal_group": "test_group"},
                {"param1": "value1"},
                {"param2": "value2"},
                {"brand": "test_brand"},
                {"view": "test_view"},
            ],
        },
    },
    # Тест-кейс 9: Группа, один параметр и жёсткий поиск
    {
        "group": "test_group",
        "brand": None,
        "view": None,
        "metadatas_list": [{"param1": "value1"}],
        "is_params_needed": True,
        "is_brand_needed": False,
        "is_view_needed": False,
        "expected_result": {
            "$and": [
                {"internal_group": "test_group"},
                {"param1": "value1"},
            ],
        },
    },
    # Тест-кейс 10: Группа, бренд, один параметр и жёсткий поиск
    {
        "group": "test_group",
        "brand": "test_brand",
        "view": None,
        "metadatas_list": [{"param1": "value1"}],
        "is_params_needed": True,
        "is_brand_needed": True,
        "is_view_needed": False,
        "expected_result": {
            "$and": [
                {"internal_group": "test_group"},
                {"param1": "value1"},
                {"brand": "test_brand"},
            ],
        },
    },
    # Тест-кейс 11: Группа, бренд, один параметр, view и жёсткий поиск
    {
        "group": "test_group",
        "brand": "test_brand",
        "view": "test_view",
        "metadatas_list": [{"param1": "value1"}],
        "is_params_needed": True,
        "is_brand_needed": True,
        "is_view_needed": True,
        "expected_result": {
            "$and": [
                {"internal_group": "test_group"},
                {"param1": "value1"},
                {"brand": "test_brand"},
                {"view": "test_view"},
            ],
        },
    },
]

# Тест-кейсы для Мягкого Поиска
_SOFT_SEARCH_TEST_CASES = [
    # Тест-кейс 1: Группа и мягкий поиск
    {
        "group": "test_group",
        "brand": None,
        "view": None,
        "metadatas_list": None,
        "is_params_needed": False,
        "is_brand_needed": False,
        "is_view_needed": False,
        "expected_result": {"internal_group": "test_group"},
    },
    # Тест-кейс 2: Группа, бренд и мягкий поиск
    {
        "group": "test_group",
        "brand": "test_brand",
        "view": None,
        "metadatas_list": None,
        "is_params_needed": False,
        "is_brand_needed": True,
        "is_view_needed": False,
        "expected_result": {
            "$or": [
                {"internal_group": "test_group"},
                {
                    "$and": [
                        {"internal_group": "test_group"},
                        {"brand": "test_brand"},
                    ],
                },
            ],
        },
    },
    # Тест-кейс 3: Группа, параметры и мягкий поиск
    {
        "group": "test_group",
        "brand": None,
        "view": None,
        "metadatas_list": [
            {"param1": "value1"},
            {"param2": "value2"},
        ],
        "is_params_needed": True,
        "is_brand_needed": False,
        "is_view_needed": False,
        "expected_result": {
            "$and": [
                {"internal_group": "test_group"},
                {
                    "$or": [
                        {"param1": "value1"},
                        {"param2": "value2"},
                    ],
                },
            ],
        },
    },
    # Тест-кейс 4: Группа, бренд, параметры и мягкий поиск
    {
        "group": "test_group",
        "brand": "test_brand",
        "view": None,
        "metadatas_list": [
            {"param1": "value1"},
            {"param2": "value2"},
        ],
        "is_params_needed": True,
        "is_brand_needed": True,
        "is_view_needed": False,
        "expected_result": {
            "$and": [
                {"internal_group": "test_group"},
                {
                    "$or": [
                        {"param1": "value1"},
                        {"param2": "value2"},
                        {"brand": "test_brand"},
                    ],
                },
            ],
        },
    },
    # Тест-кейс 5: Группа, view и мягкий поиск
    {
        "group": "test_group",
        "brand": None,
        "view": "test_view",
        "metadatas_list": None,
        "is_params_needed": False,
        "is_brand_needed": False,
        "is_view_needed": True,
        "expected_result": {
            "$or": [
                {"internal_group": "test_group"},
                {
                    "$and": [
                        {"internal_group": "test_group"},
                        {"view": "test_view"},
                    ],
                },
            ],
        },
    },
    # Тест-кейс 6: Группа, бренд, view и мягкий поиск
    {
        "group": "test_group",
        "brand": "test_brand",
        "view": "test_view",
        "metadatas_list": None,
        "is_params_needed": False,
        "is_brand_needed": True,
        "is_view_needed": True,
        "expected_result": {
            "$and": [
                {"internal_group": "test_group"},
                {
                    "$or": [
                        {"brand": "test_brand"},
                        {"view": "test_view"},
                    ],
                },
            ],
        },
    },
    # Тест-кейс 7: Группа, параметры, view и мягкий поиск
    {
        "group": "test_group",
        "brand": None,
        "view": "test_view",
        "metadatas_list": [
            {"param1": "value1"},
            {"param2": "value2"},
        ],
        "is_params_needed": True,
        "is_brand_needed": False,
        "is_view_needed": True,
        "expected_result": {
            "$and": [
                {"internal_group": "test_group"},
                {
                    "$or": [
                        {"param1": "value1"},
                        {"param2": "value2"},
                        {"view": "test_view"},
                    ],
                },
            ],
        },
    },
    # Тест-кейс 8: Группа, бренд, параметры, view и мягкий поиск
    {
        "group": "test_group",
        "brand": "test_brand",
        "view": "test_view",
        "metadatas_list": [
            {"param1": "value1"},
            {"param2": "value2"},
        ],
        "is_params_needed": True,
        "is_brand_needed": True,
        "is_view_needed": True,
        "expected_result": {
            "$and": [
                {"internal_group": "test_group"},
                {
                    "$or": [
                        {"param1": "value1"},
                        {"param2": "value2"},
                        {"brand": "test_brand"},
                        {"view": "test_view"},
                    ],
                },
            ],
        },
    },
    # Тест-кейс 9: Группа, один параметр и мягкий поиск
    {
        "group": "test_group",
        "brand": None,
        "view": None,
        "metadatas_list": [{"param1": "value1"}],
        "is_params_needed": True,
        "is_brand_needed": False,
        "is_view_needed": False,
        "expected_result": {
            "$or": [
                {"internal_group": "test_group"},
                {
                    "$and": [
                        {"internal_group": "test_group"},
                        {"param1": "value1"},
                    ],
                },
            ],
        },
    },
    # Тест-кейс 10: Группа, бренд, один параметр и мягкий поиск
    {
        "group": "test_group",
        "brand": "test_brand",
        "view": None,
        "metadatas_list": [{"param1": "value1"}],
        "is_params_needed": True,
        "is_brand_needed": True,
        "is_view_needed": False,
        "expected_result": {
            "$and": [
                {"internal_group": "test_group"},
                {
                    "$or": [
                        {"param1": "value1"},
                        {"brand": "test_brand"},
                    ],
                },
            ],
        },
    },
    # Тест-кейс 11: Группа, бренд, один параметр, view и мягкий поиск
    {
        "group": "test_group",
        "brand": "test_brand",
        "view": "test_view",
        "metadatas_list": [{"param1": "value1"}],
        "is_params_needed": True,
        "is_brand_needed": True,
        "is_view_needed": True,
        "expected_result": {
            "$and": [
                {"internal_group": "test_group"},
                {
                    "$or": [
                        {"param1": "value1"},
                        {"brand": "test_brand"},
                        {"view": "test_view"},
                    ],
                },
            ],
        },
    },
]


def run_test_cases(test_cases: list[dict], is_hard_params: bool):
    failed_test_cases = []
    for i, test_case in enumerate(test_cases):
        result = build_where_metadatas(
            group=test_case["group"],
            brand=test_case["brand"],
            view=test_case["view"],
            metadatas_list=test_case["metadatas_list"],
            is_hard_params=is_hard_params,
            is_params_needed=test_case["is_params_needed"],
            is_brand_needed=test_case["is_brand_needed"],
            is_view_needed=test_case["is_view_needed"],
        )
        test_case_idx = i + 1
        logger.info(f"Тест-кейс {test_case_idx}:\n{test_case}")
        logger.debug(f"Результат:\n{result}")
        logger.debug(f"Ожидаемый результат:\n{test_case['expected_result']}")
        if sorted(result) != sorted(test_case["expected_result"]):
            failed_test_cases.append(test_case_idx)
            logger.error("Тест-кейс не пройден")
        else:
            logger.success("Тест-кейс пройден")

    return failed_test_cases


if __name__ == "__main__":
    logger.info("Тесты составления условия Where для векторстора..")

    logger.info("Тест с Жёстким Поиском..")
    failed_test_cases_hard = run_test_cases(
        _HARD_SEARCH_TEST_CASES, is_hard_params=True
    )

    logger.info("Тест с Мягким Поиском..")
    failed_test_cases_soft = run_test_cases(
        _SOFT_SEARCH_TEST_CASES, is_hard_params=False
    )

    if failed_test_cases_hard:
        logger.error(
            f"Не пройдены тест-кейсы на Жёсткий Поиск: {failed_test_cases_hard}"
        )
    else:
        logger.success("Все тест-кейсы на Жёсткий Поиск пройдены")

    if failed_test_cases_soft:
        logger.error(
            f"Не пройдены тест-кейсы на Мягкий Поиск: {failed_test_cases_soft}"
        )
    else:
        logger.success("Все тест-кейсы на Мягкий Поиск пройдены")
