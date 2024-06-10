def process_results(test_cases, api_results):
    processed_results = []

    for idx, api_result in enumerate(api_results['nomenclatures']):
        test_case = test_cases[idx]

        # Сравнение номенклатур и групп
        expected_nomenclature = test_case['Ожидание номенклатура']
        expected_group = test_case['Ожидание группа']
        actual_group = api_result['group_name']
        actual_nomenclature = api_result['mappings'][0]['nomenclature'] if api_result['mappings'] else ''

        # Определение корректности
        correct_group = expected_group == actual_group
        correct_nomenclature = expected_nomenclature == actual_nomenclature
        is_correct = "Корректно" if correct_group and correct_nomenclature else "Не корректно"

        processed_result = {
            'Тест-Кейс ID': test_case['Тест-Кейс ID'],
            'Шаг алгоритма': '',
            'Тип ошибки': '',
            'Корректно?': is_correct,
            'Номенклатура': test_case['Номенклатура поставщика'],
            'Ожидание группа': expected_group,
            'Реальность группа': actual_group,
            'Ожидание номенклатура': expected_nomenclature,
            'Реальность номенклатура': actual_nomenclature
        }

        processed_results.append(processed_result)
    
    return processed_results
