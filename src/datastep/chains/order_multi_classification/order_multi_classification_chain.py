from langchain_openai import AzureChatOpenAI
from loguru import logger

from datastep.chains.order_classification_chain import get_llm_by_client_credentials
from datastep.chains.order_multi_classification.class_score_chain import get_class_score_chain, get_class_score
from datastep.chains.order_multi_classification.most_relevant_class_chain import get_most_relevant_class, \
    get_most_relevant_class_chain
from scheme.order_classification.order_classification_config_scheme import OrderClassificationClient

# Правила для каждого класса
rules_by_class = {
    "Сантехника": [
        "Заявка содержит слова: течь, кран, труба, вода.",
        "Заявка связана с поломкой сантехнического оборудования."
    ],
    "Электрика": [
        "Заявка содержит слова: электричество, лампа, розетка, провод.",
        "Заявка связана с поломкой электроприборов или электросети."
    ],
    "Уборка": [
        "Заявка содержит слова: мусор, грязь, уборка, пыль.",
        "Заявка связана с необходимостью очистки территории."
    ]
}


def _get_scores_of_classes(
    llm: AzureChatOpenAI,
    order_query: str,
    verbose: bool = False,
) -> dict[str, str]:
    score_chain = get_class_score_chain(
        llm=llm,
        verbose=verbose,
    )

    # TODO: get rules by classes from DB

    scores = {}
    for class_name, rules in rules_by_class.items():
        score = get_class_score(
            chain=score_chain,
            order_query=order_query,
            class_name=class_name,
            rules=rules,
        )
        scores[class_name] = score

    return scores


def get_order_class(
    client: str,
    order_query: str,
    verbose: bool = False,
):
    llm = get_llm_by_client_credentials(client=client)

    scores = _get_scores_of_classes(
        llm=llm,
        order_query=order_query,
        verbose=verbose,
    )

    scores_str = "\n\n".join([
        f"{score}"
        for class_name, score in scores.items()
    ])
    # print(scores_str)

    most_relevant_class_chain = get_most_relevant_class_chain(
        llm=llm,
        verbose=verbose,
    )
    order_class = get_most_relevant_class(
        chain=most_relevant_class_chain,
        order_query=order_query,
        scores=scores_str
    )

    return order_class


if __name__ == "__main__":
    user_request = "У меня в розетке искрит, нужна помощь"
    order_class = get_order_class(
        client=OrderClassificationClient.VYSOTA,
        order_query=user_request,
        verbose=True,
    )

    logger.debug(f"Answer: {order_class}")
    logger.debug(f"Answer Type: {type(order_class)}")
