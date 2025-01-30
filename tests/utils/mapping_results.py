from scheme.mapping.mapping_scheme import MappingOneNomenclatureRead


def _get_result_for_test_case(
    test_case_nomenclature: str,
    results: list[MappingOneNomenclatureRead],
) -> MappingOneNomenclatureRead | None:
    for mapping_result in results:
        if mapping_result.nomenclature == test_case_nomenclature:
            return mapping_result

    return None


def _get_is_correct_value_text(is_correct: bool):
    if is_correct:
        return "Корректно"
    return "Не корректно"


def process_results(
    test_cases: list[dict],
    results: list[MappingOneNomenclatureRead],
) -> list[dict]:
    processed_results: list[dict] = []

    for i, case in enumerate(test_cases):
        test_case_nomenclature = case['Номенклатура на Вход']

        # Find test case result
        mapping_result = _get_result_for_test_case(
            test_case_nomenclature=test_case_nomenclature,
            results=results,
        )

        # Extract expected values
        expected_internal_group = case['Ожидание Внутренняя Группа']
        expected_group = case['Ожидание Группа']
        expected_view = case['Ожидание Вид']
        expected_nomenclature = case['Ожидание Номенклатура']

        # Extract predicted values
        predicted_internal_group = mapping_result.internal_group
        predicted_group = mapping_result.group
        predicted_group_code = mapping_result.group_code
        predicted_view = mapping_result.view
        predicted_view_code = mapping_result.view_code
        predicted_material_code = mapping_result.material_code

        # Extract input nomenclature params
        nomenclature_params_results: list[dict] | None = mapping_result.nomenclature_params
        nomenclature_params_list = []
        if nomenclature_params_results:
            for param in nomenclature_params_results:
                param_name, param_value = list(param.items())[0]
                nomenclature_params_list.append(
                    f"{param_name}: {param_value}"
                )
        nomenclature_params = "\n".join(nomenclature_params_list)

        # Extract hard-search found nomenclature
        predicted_nomenclature = ""
        if mapping_result.mappings:
            predicted_nomenclature = mapping_result.mappings[0].nomenclature

        # Set comment if hard-search nomenclature not found
        if predicted_nomenclature == "":
            if mapping_result.similar_mappings:
                predicted_nomenclature = "Таких признаков не найдено, но вот номенклатуры"

        # Extract soft-search (similar) nomenclatures
        predicted_similar_nomenclatures = ""
        if mapping_result.similar_mappings:
            similar_nomenclatures = []

            for mapping in mapping_result.similar_mappings:
                similar_nomenclatures.append(mapping.nomenclature)

            predicted_similar_nomenclatures = "\n".join(similar_nomenclatures)

        # Check if predicted values same as expected
        is_correct_internal_group = expected_internal_group == predicted_internal_group
        is_correct_group = expected_group == predicted_group
        is_correct_view = expected_view == predicted_view
        is_correct_nomenclature = expected_nomenclature == predicted_nomenclature

        # Combine results for sheet
        result = {
            "Тест-Кейс ID": case['Тест-Кейс ID'],
            "Шаг алгоритма": case['Шаг алгоритма'],
            "Тип ошибки": case['Тип ошибки'],

            "Номенклатура на Вход": test_case_nomenclature,

            "Ожидаемая Внутренняя Группа": expected_internal_group,
            "Предсказанная Внутренняя Группа": predicted_internal_group,

            "Ожидаемая Группа": expected_group,
            "Предсказанная Группа": predicted_group,
            "Предсказанная Группа Код": predicted_group_code,

            "Ожидаемый Вид": expected_view,
            "Предсказанный Вид": predicted_view,
            "Предсказанный Вид Код": predicted_view_code,

            "Ожидаемая Номенклатура": expected_nomenclature,
            "Предсказанная Номенклатура": predicted_nomenclature,
            "Предсказанная Номенклатура Код": predicted_material_code,

            "Предсказанные Варианты Номенклатур": predicted_similar_nomenclatures,

            "Параметры": nomenclature_params,

            "Корректно Внутренняя Группа?": _get_is_correct_value_text(is_correct_internal_group),
            "Корректно Группа?": _get_is_correct_value_text(is_correct_group),
            "Корректно Вид?": _get_is_correct_value_text(is_correct_view),
            "Корректно Номенклатура?": _get_is_correct_value_text(is_correct_nomenclature),
        }

        processed_results.append(result)

    return processed_results
