from langchain_openai import AzureChatOpenAI
from loguru import logger

from datastep.chains.order_classification_chain import get_llm_by_client_credentials
from datastep.chains.order_multi_classification.class_score_chain import get_class_score_chain, get_class_score
from datastep.chains.order_multi_classification.most_relevant_class_chain import get_most_relevant_class, \
    get_most_relevant_class_chain
from scheme.order_classification.order_classification_config_scheme import RulesWithParams
from scheme.order_classification.order_classification_scheme import MostRelevantClassLLMResponse


def _get_scores_of_classes(
    llm: AzureChatOpenAI,
    order_query: str,
    rules_by_classes: dict,
    client: str | None = None,
    verbose: bool = False,
) -> dict[str, str]:
    score_chain = get_class_score_chain(
        llm=llm,
        verbose=verbose,
    )

    scores = {}
    for class_name, params in rules_by_classes.items():
        rules_with_params = RulesWithParams(**params)

        if not rules_with_params.is_use_classification:
            logger.info(f"Class '{class_name}' was skipped by config of client '{client}'")
            continue

        # Get rules from config
        rules = rules_with_params.rules
        exclusion_rules = rules_with_params.exclusion_rules

        score = get_class_score(
            chain=score_chain,
            order_query=order_query,
            class_name=class_name,
            rules=rules,
            exclusion_rules=exclusion_rules,
            client=client,
        )
        scores[class_name] = score

    return scores


def get_order_class(
    order_query: str,
    rules_by_classes: dict,
    client: str | None = None,
    verbose: bool = False,
) -> MostRelevantClassLLMResponse:
    llm = get_llm_by_client_credentials(client=client)

    scores = _get_scores_of_classes(
        llm=llm,
        order_query=order_query,
        rules_by_classes=rules_by_classes,
        client=client,
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
        scores=scores_str,
        client=client,
    )

    return order_class
