import time

from langchain.chains.llm import LLMChain
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from loguru import logger
from openai import RateLimitError

from infra.llm_clients_credentials import get_llm_by_client_credentials, Service
from scheme.mapping.llm_mapping_scheme import LLMMappingResponse

_PROMPT_TEMPLATE = """
Ты специалист в области строительства. Ты знаешь все материалы, их параметры и значение
каждого из них. Ты сопоставляем УПД материалы с материалами из НСИ.


# Задача
На основе входных данных выбери наиболее подходящий материал из НСИ, используя
семантику названий материалов, исторические кейсы сопоставлений, которые ранее
сопоставлялись, и правила/эвристики, по которым проверялись эти исторические кейсы,
они записаны у неправильных сопоставлений.

# Входные данные
УПД материал: '{material_name}'

<Похожие кейсы из истории сопоставлений>
{kb_cases_list}
</Похожие кейсы из истории сопоставлений>

<Список материалов НСИ>
{nsi_materials_names}
</Список материалов НСИ>


# Думай по такому алгоритму
1. Есть ли в УПД материале параметры, на которые есть правила/пояснения?
2. Есть ли в истории сопоставлений есть такой же материал, которые правильно
сопоставился, то можно сразу выдать его в ответе.
3. Какие из представленных вариантов НСИ материалов наиболее подходят по семантике к
УПД материалу.
4. Какой из них наиболее подходит по семантике и параметрам — наиболее подходящий НСИ
материал для УПД материала тот, с которым сходится больше параметров.
5. Если на текущее задание нет примеров или правил/пояснений, так что ты не можешь их
использовать, то попробуй использовать свои знания в области строительства и совпадения
цифр в параметрах УПД материала и НСИ материала.


# Что делать, если в списке материалов из НСИ нет подходящего кейса
Если ты не можешь выбрать материал из списка НСИ материалов, то в ответе объясни почему
конкретно ты не можешь выбрать, ссылайся на правила/эвристики из истории сопоставлений.


# Что делать, если в списке материалов из НСИ или в списке сопоставлений нет
подходящего кейса
Если ты не можешь выбрать материал из списка НСИ материалов или из истории
сопоставлений, то в ответе объясни почему конкретно ты не можешь выбрать, ссылайся на
правила/эвристики из истории сопоставлений.
В поле материала в ответе укажи пустоту.


# Выходные данные
В ответе объясни какие параметры имеют входной материал и материал, который ты выбрал,
напиши какой материал ты выбрал и объясни почему. Ссылайся на правила/эвристики из
истории сопоставлений.
Ответь в формате JSON по схеме:
- "comment": "<твоё объяснение>"
- "nomenclature": "<наиболее подходящий материал из НСИ>"
"""

# Wait Time if Rate Limit Error occurred
WAIT_TIME_IN_SEC = 60

parser = JsonOutputParser(pydantic_object=LLMMappingResponse)


def _get_prompt() -> PromptTemplate:
    prompt = PromptTemplate(
        template=_PROMPT_TEMPLATE,
        input_variables=[
            "material_name",
            "kb_cases_list",
            "nsi_materials_names",
        ],
    )
    return prompt


def get_llm_mapping_chain(
    client: str,
    verbose: bool = False,
) -> LLMChain:
    llm = get_llm_by_client_credentials(
        client=client,
        service=Service.MAPPING,
    )

    prompt = _get_prompt()

    chain = LLMChain(
        llm=llm,
        prompt=prompt,
        output_parser=parser,
        verbose=verbose,
    )
    return chain


def run_llm_mapping(
    chain: LLMChain,
    material_name: str,
    kb_cases_list_str: str,
    nsi_materials_names_str: str,
) -> LLMMappingResponse:
    try:
        response = chain.run(
            material_name=material_name,
            kb_cases_list=kb_cases_list_str,
            nsi_materials_names=nsi_materials_names_str,
        )

        parsed_response = LLMMappingResponse(**response)
        return parsed_response

    # TODO: make decorator for it
    except RateLimitError as e:
        logger.error(f"RateLimit error occurred: {str(e)}")
        logger.info(f"Wait {WAIT_TIME_IN_SEC} seconds and try again")
        time.sleep(WAIT_TIME_IN_SEC)
        logger.info(f"Timeout passed, try to run LLM mappin again")

        return run_llm_mapping(
            chain=chain,
            material_name=material_name,
            kb_cases_list_str=kb_cases_list_str,
            nsi_materials_names_str=nsi_materials_names_str,
        )
