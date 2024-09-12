def process_results(test_cases, api_results):
    processed_results = []

    for idx, api_result in enumerate(api_results):
        test_case = test_cases[idx]

        # Сравнение номенклатур и групп
        expected_filename = test_case['Ожидаемый файл']
        expected_answer = test_case['Ожидаемый ответ']
        actual_filename = api_result['filename']

        if api_result['answer']:
            actual_answer = api_result['answer']
        else:
            actual_answer = ""

        # Определение корректности
        correct_filename = expected_filename == actual_filename
        correct_answer = expected_answer == actual_answer
        is_correct = "Возможно Корректно" if correct_filename and correct_answer else ""

        processed_result = {
            'Тест-Кейс ID': test_case['Тест-Кейс ID'],
            'Вопрос': test_case['Вопрос'],
            'Ожидаемый файл': expected_filename,
            'Реальный файл': actual_filename,
            'Ожидаемый ответ': expected_answer,
            'Реальный ответ': actual_answer,
            'Корректно?': is_correct,
            'Тип вопроса': '',
            'Комментарий': '',

        }

        processed_results.append(processed_result)

    return processed_results
