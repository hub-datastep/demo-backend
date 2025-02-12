from langchain_openai import AzureChatOpenAI
from loguru import logger

from order_classification.v6.modules.chains.class_score_chain import (
    get_class_score_chain,
    get_class_score,
)
from order_classification.v6.modules.chains.most_relevant_class_chain import (
    get_most_relevant_class,
)
from order_classification.v6.modules.chains.order_query_summarization import (
    get_order_query_summary,
)
from order_classification.v6.modules.env import env
from order_classification.v6.modules.schemas import (
    OrderClassificationLLMResponse,
    RulesWithParams,
)


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
            logger.info(
                f"Class '{class_name}' was skipped by config of client '{client}'"
            )
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
) -> OrderClassificationLLMResponse:
    llm = AzureChatOpenAI(
        azure_deployment=env.MODEL_NAME,
        api_key=env.API_KEY,
        azure_endpoint=env.AZURE_ENDPOINT,
        temperature=0,
        verbose=False,
    )

    # llm = ChatOpenAI(
    #     model_name="gpt-4o-mini",
    #     temperature=0,
    #     openai_api_key=OPENAI_API_KEY_ORDER_CLASSIFICATION_EVALUATION
    # )

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
