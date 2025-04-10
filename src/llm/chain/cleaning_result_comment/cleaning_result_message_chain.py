import asyncio
from datetime import datetime

from langchain.chains.llm import LLMChain
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import AzureChatOpenAI
from loguru import logger
from openai import RateLimitError

from infra.llm_clients_credentials import get_llm_by_client_credentials
from infra.order_classification import WAIT_TIME_IN_SEC
from scheme.order_notification.order_notification_scheme import (
    CleaningResultMessageLLMResponse,
)
from util.dates import get_now_utc

_PROMPT_TEMPLATE = """
# Твоя задача
Напиши сообщение о выполненной работе по заявке с Классом '{order_class}' и передай детали его выполнения,
если они указаны в комментарии исполнителя.
Если задача не выполнена (это можно понять исходя из комментария исполнителя), то не пиши сообщение.
Также поясни как ты написал сообщение и почему, ссылайся и цитируй комментарий исполнителя и жалобу жильца в пояснении.

# Входные данные
Текущая дата: '{current_date}'
Класс заявки: '{order_class}'
Жалоба жильца в заявке: '{order_query}'
Комментарий исполнителя: '{order_status_comment}'

# Как писать сообщение
1. Проанализируй комментарий исполнителя и убери из него:
    - Агрессию
    - Раздражение
    - Ругательства
    - Оскорбления
    - Угрозы
    - Недовольство
2. Выдели все детали, которые написаны в комментарии исполнителя
3. Используя жалобу жильца и комментарий исполнителя напиши сообщение, описывающее что было сделано и укажи в нём детали из комментария исполителя.

## Что нужно написать в сообщении
- Все детали, которые отписал исполнитель:
    - какие проблемы, связанные с жалобой жильца, остались нерешенными
    - как решили жалобу жильца
    - что использовали для решения и зачем/почему
- Учитывай, что в жалобе жильца и комментарии исполнителя используется Российский формат даты: "день.месяц.год".
- Важно, чтобы в сообщении не было написано то, что исполнитель не делал, или то, на что житель не жаловался.

## Что нельзя писать в сообщении
- Вопросы
- Просьбы дать фидбек (обратную связь)
- Просьбы оценить работу

## Что делать, если в комментарии исполнителя нет подробностей/деталей
Если в комментарии исполнителя написано только, что работа выполнена, и нет никаких подробностей/деталей,
то перечисли все проблемы из жалобы жильца в сообщении и напиши, что они решены.
Обычно исполнители пишу комментирии по типу "работу выполнил",
потому что им лень расписывать то, на что жаловался жилец, но на самом деле оно выполнено.

## Что делать, если в комментарии исполнителя есть вопросы
Если комментарий исполнителя содержит один или несколько вопросов, то не пиши сообщение.

## Что делать, если в комментарии исполнителя сказано, что работы ещё не проведены
Если комментарий исполнителя сказано, что работы ещё не проведены,
и они произведутся в будущем, то не пиши сообщение.

# Вот примеры того как надо собирать сообшение
<Примеры сообщений>
Пример 1:
- Жалоба жильца: 'Возможно засорился мусоропровод в подъезде №1,
сильный запах на 14 этаже с 31 августа. Нужна уборка.'
- Комментарий исполнителя: 'Засор устранен. Застрял пакет с мусором. Обработка проведена
хлорным раствором и раствором "Цимекса"'
- Написанное сообщение: 'Засор мусоропровода устранили (в нём застрял пакет с мусором)
и обработали хлорным раствором
и раствором “Цимекса”, чтобы запаха больше не было.'
Пример 2:
- Жалоба жильца: 'Опять не моют под ковриками со стороны дверей.Идите и мойте.'
- Комментарий исполнителя: ''
- Написанное сообщение: 'Помыли под ковриками, теперь всё чисто.'
Пример 3:
- Жалоба жильца: 'Требуется уборка в лифте 9 секции, пассажирский
грязно, липкий пол и очень неприятный запах'
- Комментарий исполнителя: 'Уборка выполнена по графику'
- Написанное сообщение: 'Уборка в лифте 9 секции произведена по графику.'
Пример 4:
- Жалоба жильца: 'Афины,10 этаж ,очень грязно.Уборка не производится несколько дней'
- Комментарий исполнителя: 'Добрый день. Сегодня производилась уборка.
График-1 раз в день.
Скажите соседям у кого делают ремонт, пусть пользуются влажной тряпкой у порога!
Да и в целом они должны убирать после себя!'
- Написанное сообщение: 'Сегодня производилась уборка. График: 1 раз в день.'
Пример 5:
- Жалоба жильца: 'Уборка не производится уже несколько дней'
- Комментарий исполнителя: 'Где конкретно не производится уборка?'
- Написанное сообщение: ''
Пример 6:
- Жалоба жильца: 'Просьба очистить обшивку в пассажирском лифте от надписей.'
- Комментарий исполнителя: 'Работу выполнил'
- Написанное сообщение: 'Мы убрали надписи в пассажирском лифте.'
</Примеры сообщений>

Ответь в формате JSON по схеме:
- "filtered_comment": "<отфильтрованный комментарий после шага 1>"
- "comment": "<пояснение как ты писал сообщение>"
- "message": "<текст сообщения о выполненной работе>"
"""


parser = JsonOutputParser(pydantic_object=CleaningResultMessageLLMResponse)


def _get_prompt() -> PromptTemplate:
    prompt = PromptTemplate(
        input_variables=[
            "current_date",
            "order_class",
            "order_query",
            "order_status_comment",
        ],
        template=_PROMPT_TEMPLATE,
    )
    return prompt


def get_cleaning_results_message_chain(
    llm: AzureChatOpenAI,
    verbose: bool = False,
) -> LLMChain:
    prompt = _get_prompt()

    chain = LLMChain(
        llm=llm,
        prompt=prompt,
        output_parser=parser,
        verbose=verbose,
    )
    return chain


async def get_cleaning_results_message(
    chain: LLMChain,
    order_query: str,
    order_status_comment: str,
    client: str | None = None,
) -> CleaningResultMessageLLMResponse:
    try:
        current_date = get_now_utc().date()
        current_date_str = current_date.strftime("%d.%m.%Y")
        order_class = "Клининг"

        response: str = await chain.arun(
            current_date=current_date_str,
            order_class=order_class,
            order_query=order_query,
            order_status_comment=order_status_comment,
        )

        parsed_response = CleaningResultMessageLLMResponse(**response)
        return parsed_response
    except RateLimitError as e:
        logger.error(f"RateLimit error occurred: {str(e)}")
        logger.info(f"Wait {WAIT_TIME_IN_SEC} seconds and try again")
        await asyncio.sleep(WAIT_TIME_IN_SEC)
        logger.info(
            f"Timeout passed, try to classify order '{order_query}' of client '{client}' again"
        )

        return await get_cleaning_results_message(
            chain=chain,
            order_query=order_query,
            order_status_comment=order_status_comment,
            client=client,
        )


if __name__ == "__main__":
    from pandas import read_excel
    from tqdm import tqdm

    from infra.llm_clients_credentials import Service

    llm = get_llm_by_client_credentials(service=Service.ORDER_CLASSIFICATION)
    chain = get_cleaning_results_message_chain(llm=llm)

    FILE_PATH = "/home/syrnnik/Downloads/vysota/cleaning-results-message-with-llm/LLM Message Tests.xlsx"
    SHEET_NAME = "test-cases"

    test_cases = read_excel(FILE_PATH, SHEET_NAME)

    test_cases["Сообщение от LLM"] = None
    test_cases["Пояснение к Сообщению"] = None
    test_cases["Отфильтрованный Коммент Исполнителя"] = None
    for i, case in tqdm(
        test_cases.iterrows(),
        desc="Generate Message",
        total=len(test_cases),
        unit="1 order&comment",
    ):
        order_query = case["Жалоба Жильца"]
        order_query = order_query.replace("\n", " ").strip()
        order_status_comment = case["Комментарий Исполнителя"]
        order_status_comment = order_status_comment.replace("\n", " ").strip()

        response = get_cleaning_results_message(
            chain=chain,
            order_query=order_query,
            order_status_comment=order_status_comment,
        )
        case["Сообщение от LLM"] = response.message
        case["Пояснение к Сообщению"] = response.comment
        case["Отфильтрованный Коммент Исполнителя"] = response.filtered_comment

        test_cases.loc[i] = case

        logger.debug(f"Order Query:{order_query}")
        logger.debug(f"Order Status Comment:{order_status_comment}")
        logger.debug(f"LLM Response:\n{response}")

    now = datetime.now().strftime("%d-%m-%Y %H-%M")
    EXPORT_FILE_PATH = f"LLM Message Test Results {now}.xlsx"
    EXPORT_SHEET_NAME = f"Results from {now}"
    test_cases.to_excel(
        EXPORT_FILE_PATH,
        sheet_name=EXPORT_SHEET_NAME,
        index=False,
    )
