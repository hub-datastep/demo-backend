from langchain.chains.llm import LLMChain
from langchain_core.prompts import PromptTemplate
from langchain_openai import AzureChatOpenAI

from infra.env import AZURE_DEPLOYMENT_NAME_ORDER_CLASSIFICATION


def get_order_classification_chain(prompt_template: str):
    llm = AzureChatOpenAI(
        azure_deployment=AZURE_DEPLOYMENT_NAME_ORDER_CLASSIFICATION,
        temperature=0,
        verbose=False,
    )

    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["query"]
    )

    return LLMChain(llm=llm, prompt=prompt)
