import os
from time import sleep

from datastep.components import datastep_agent
from datastep.components.datastep_prediction import DatastepPrediction
from dto.query_dto import QueryDto
from service.datastep_service import datastep_service

mock_prediction = DatastepPrediction(
            answer="""Топ 5 компаний по чистой прибыли за 2023 год:
                1. None - Чистая прибыль: 14,216,107,656.10
                2. ФСК ДЕВЕЛОПМЕНТ ООО - Чистая прибыль: 9,073,095,523.76
                3. МОСКОВСКИЙ ФОНД РЕНОВАЦИИ ЖИЛОЙ ЗАСТРОЙКИ - Чистая прибыль: 4,349,817,014.35
                4. РОСТРАНСМОДЕРНИЗАЦИЯ ФКУ - Чистая прибыль: 3,540,598,929.24
                5. АДМИНИСТРАЦИЯ ВОЛЖСКОГО БАССЕЙНА ФБУ - Чистая прибыль: 3,018,938,800.00""",
            sql="""~~~sql
                SELECT TOP 5 [Контрагент], SUM([Сумма]) AS [Чистая прибыль]
                FROM test
                WHERE [Тип документа] = 'Поступление' AND [План/Факт] = 'Факт' AND [Период] LIKE '%2023%'
                GROUP BY [Контрагент]
                ORDER BY [Чистая прибыль] DESC
                ~~~""",
            table="""| Контрагент                                |   Чистая прибыль |
                |:------------------------------------------|-----------------:|
                |                                           |  14216107656.100 |
                | ФСК ДЕВЕЛОПМЕНТ ООО                       |   9073095523.760 |
                | МОСКОВСКИЙ ФОНД РЕНОВАЦИИ ЖИЛОЙ ЗАСТРОЙКИ |   4349817014.350 |
                | РОСТРАНСМОДЕРНИЗАЦИЯ ФКУ                  |   3540598929.240 |
                | АДМИНИСТРАЦИЯ ВОЛЖСКОГО БАССЕЙНА ФБУ      |   3018938800.000 |""",
            is_exception=False
            )


def get_prediction_v1(body: QueryDto) -> DatastepPrediction:
    if os.getenv("MOCK_PREDICTION") == "True":
        sleep(2)
        return mock_prediction
    return datastep_service.run(body.query)


def get_prediction_v2(body: QueryDto) -> DatastepPrediction:
    if os.getenv("MOCK_PREDICTION") == "True":
        sleep(2)
        return mock_prediction
    return datastep_agent.execute(body.query)


# def reset() -> None:
#     return datastep_service.reset()
