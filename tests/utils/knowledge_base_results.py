from scheme.prediction.prediction_scheme import KnowledgeBasePredictionRead


def process_results(
    test_cases: list[dict],
    results: list[KnowledgeBasePredictionRead],
) -> list[dict]:
    processed_results: list[dict] = []

    for idx, result in enumerate(results):
        test_case = test_cases[idx]

        # Сравнение номенклатур и групп
        expected_filename = test_case['Ожидаемый файл']
        expected_answer = test_case['Ожидаемый ответ']
        actual_filename = result.filename

        actual_answer = None
        if result.answer:
            actual_answer = result.answer

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
