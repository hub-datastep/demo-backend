def process_results(test_cases, api_results):
    processed_results = []

    for idx, api_result in enumerate(api_results['nomenclatures']):
        test_case = test_cases[idx]

        # Сравнение номенклатур и групп
        expected_nomenclature = test_case['Ожидание номенклатура']
        expected_group = test_case['Ожидание группа']
        actual_group = api_result['group']

        nomenclature_params_results: list[dict] = api_result['nomenclature_params']
        nomenclature_params_list = []
        for param in nomenclature_params_results:
            param_name, param_value = list(param.items())[0]
            nomenclature_params_list.append(
                f"{param_name}: {param_value}"
            )
        nomenclature_params = "\n".join(nomenclature_params_list)

        if api_result['mappings']:
            actual_nomenclature = api_result['mappings'][0]['nomenclature']
        else:
            actual_nomenclature = ""

        if actual_nomenclature == "":
            if api_result['similar_mappings']:
                actual_nomenclature = "Таких признаков не найдено, но вот номенклатуры"
            else:
                actual_nomenclature = ""

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
