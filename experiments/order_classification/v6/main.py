import re

from langchain.chains import LLMChain
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate

from order_classification.v6.modules.env import env

PROMPT_TEMPLATE = """
Заявка жильца:
```
{query}
```

Прочитай заявку жильца и убери из неё:
- Срочность (необходимость немедленного решения).
- Агрессию, раздражение, ругательства, оскорбления, угрозы.
Важно, чтобы заявка звучала нейтрально, а не агрессивно или срочно.

Твоей ответ должен содержать только содержание заявки жильца.

Содержание заявки жильца:
"""


def format_order_query(order_query: str) -> str:
    order_query = re.sub(r"[\s!\n]+", " ", order_query)
    return order_query


# Инициализация LLM
llm = OpenAI(
    api_key=env.EXPERIMENTS_API_KEY,
    temperature=0.7,
)

classification_chain = LLMChain(
    llm=llm,
    prompt=PromptTemplate(
        input_variables=["query"],
        template=PROMPT_TEMPLATE
    ),
    verbose=True,
)

summary_chain = LLMChain(
    llm=llm,
    prompt=PromptTemplate(
        input_variables=["query"],
        template=PROMPT_TEMPLATE
    )
)

if __name__ == "__main__":
    # Шаг 1: Загрузка тест-кейсов
    test_cases = [
        "Срочно!!!! Починить кран на кухне, все затопило!!!",
        "Когда уже почините лифт??? Безобразие!",
    ]

    # Создаем и тестируем цепочку
    for test_case in test_cases:
        formatted_query = format_order_query(test_case)

        result = classification_chain.run(
            query=formatted_query,
        )

        print(f"Input: {test_case}")
        print(f"Output: {result}")
