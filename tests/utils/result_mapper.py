def _get_mapping_result_for_test_case(
    test_case_nomenclature: str,
    mapping_results_list: list,
) -> dict | None:
    for mapping_result in mapping_results_list:
        if mapping_result['nomenclature'] == test_case_nomenclature:
            return mapping_result

    return None


def _process_results_old(test_cases, mapping_results_list: list):
    processed_results = []

    for i, nomenclature_result in enumerate(mapping_results_list):
        test_case = test_cases[i]

        # Сравнение номенклатур и групп
        expected_nomenclature = test_case['Ожидание номенклатура']
        expected_group = test_case['Ожидание группа']
        actual_group = nomenclature_result['group']

        nomenclature_params_results: list[dict] = nomenclature_result['nomenclature_params']
        nomenclature_params_list = []
        for param in nomenclature_params_results:
            param_name, param_value = list(param.items())[0]
            nomenclature_params_list.append(
                f"{param_name}: {param_value}"
            )
        nomenclature_params = "\n".join(nomenclature_params_list)

        actual_nomenclature = ""
        if nomenclature_result['mappings']:
            actual_nomenclature = nomenclature_result['mappings'][0]['nomenclature']

        if actual_nomenclature == "":
            if nomenclature_result['similar_mappings']:
                actual_nomenclature = "Таких признаков не найдено, но вот номенклатуры"

        # Определение корректности
        correct_group = expected_group == actual_group
        correct_nomenclature = expected_nomenclature == actual_nomenclature
        is_correct_group = "Корректно" if correct_group else "Не корректно"
        is_correct_nom = "Корректно" if correct_nomenclature else "Не корректно"

        processed_result = {
            "Тест-Кейс ID": test_case['Тест-Кейс ID'],
            "Шаг алгоритма": test_case['Шаг алгоритма'],
            "Тип ошибки": test_case['Тип ошибки'],
            "Корректно группа?": is_correct_group,
            "Корректно номенклатура?": is_correct_nom,
            "Номенклатура": test_case['Номенклатура поставщика'],
            "Ожидание группа": expected_group,
            "Реальность группа": actual_group,
            "Ожидание номенклатура": expected_nomenclature,
            "Реальность номенклатура": actual_nomenclature,
            "Параметры": nomenclature_params,
        }

        processed_results.append(processed_result)

    return processed_results


def process_results(test_cases, mapping_results_list: list):
    processed_results = []

    for i, case in enumerate(test_cases):
        test_case = test_cases[i]
        test_case_nomenclature = case['Номенклатура поставщика']

        mapping_result = _get_mapping_result_for_test_case(
            test_case_nomenclature=test_case_nomenclature,
            mapping_results_list=mapping_results_list,
        )

        expected_nomenclature = test_case['Ожидание номенклатура']
        expected_group = test_case['Ожидание группа']
        actual_group = mapping_result['group']
        actual_internal_group = mapping_result['internal_group']
        actual_view = mapping_result['view']

        nomenclature_params_results: list[dict] | None = mapping_result['nomenclature_params']
        nomenclature_params_list = []
        if nomenclature_params_results:
            for param in nomenclature_params_results:
                param_name, param_value = list(param.items())[0]
                nomenclature_params_list.append(
                    f"{param_name}: {param_value}"
                )
        nomenclature_params = "\n".join(nomenclature_params_list)

        actual_nomenclature = ""
        actual_similar_nomenclatures = ""
        if mapping_result['mappings']:
            actual_nomenclature = mapping_result['mappings'][0]['nomenclature']

        if mapping_result['similar_mappings']:
            for mapping in mapping_result['similar_mappings']:
                actual_similar_nomenclatures += f"{mapping['nomenclature']}\n"

        if actual_nomenclature == "":
            if mapping_result['similar_mappings']:
                actual_nomenclature = "Таких признаков не найдено, но вот номенклатуры"

        # Определение корректности
        is_correct_group = expected_group == actual_group
        is_correct_nomenclature = expected_nomenclature == actual_nomenclature
        is_correct_group_text = "Корректно" if is_correct_group else "Не корректно"
        is_correct_nom_text = "Корректно" if is_correct_nomenclature else "Не корректно"

        processed_result = {
            "Тест-Кейс ID": test_case['Тест-Кейс ID'],
            "Шаг алгоритма": test_case['Шаг алгоритма'],
            "Тип ошибки": test_case['Тип ошибки'],
            "Корректно группа?": is_correct_group_text,
            "Корректно номенклатура?": is_correct_nom_text,
            "Номенклатура": test_case_nomenclature,
            "Ожидание группа": expected_group,
            "Реальность группа": actual_group,
            "Реальность внутренняя группа": actual_internal_group,
            "Ожидание номенклатура": expected_nomenclature,
            "Реальность номенклатура": actual_nomenclature,
            "Реальность варианты номенклатур": actual_similar_nomenclatures,
            "Реальность вид": actual_view,
            "Параметры": nomenclature_params,
        }

        processed_results.append(processed_result)

    return processed_results
