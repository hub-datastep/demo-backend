import re

from langchain.chains import LLMChain
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate

from order_classification.v6.modules.prompt import PROMPT_TEMPLATE


def format_order_query(order_query: str) -> str:
    order_query = re.sub(r"[\s!\n]+", " ", order_query)
    return order_query


# Инициализация LLM
llm = OpenAI(temperature=0.7)

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


# TODO: fix or remove this
def get_order_class(
    order_query: str,
    rules_by_classes: dict,
) -> dict:
    llm = get_llm_by_client_credentials(client=client)

    query_summary = get_order_query_summary(
        llm=llm,
        order_query=order_query,
        client=client,
        verbose=verbose,
    )

    scores = _get_scores_of_classes(
        llm=llm,
        order_query=query_summary,
        rules_by_classes=rules_by_classes,
        client=client,
        verbose=verbose,
    )

    # Class name already exists in score
    scores_str = "\n\n".join(
        [f"{score_with_class_name}"
         for _, score_with_class_name in scores.items()]
    )
    # print(scores_str)

    most_relevant_class_response = get_most_relevant_class(
        llm=llm,
        order_query=query_summary,
        rules_by_classes=rules_by_classes,
        scores=scores_str,
        client=client,
        verbose=verbose,
    )

    return OrderClassificationLLMResponse(
        most_relevant_class_response=most_relevant_class_response,
        scores=scores_str,
        query_summary=query_summary,
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
