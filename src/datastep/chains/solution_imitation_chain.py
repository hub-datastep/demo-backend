from langchain.chains.llm import LLMChain
from langchain_core.prompts import PromptTemplate
from langchain_openai import AzureChatOpenAI

from infra.env import AZURE_DEPLOYMENT_NAME_EMERGENCY_CLASSIFICATION


def _get_solution_imitation_llm() -> AzureChatOpenAI:
    llm = AzureChatOpenAI(
        azure_deployment=AZURE_DEPLOYMENT_NAME_EMERGENCY_CLASSIFICATION,
        temperature=0,
        verbose=False,
    )
    return llm


def get_solution_imitation_chain(prompt: PromptTemplate):
    llm = _get_solution_imitation_llm()
    return LLMChain(llm=llm, prompt=prompt)


def get_solution_imitation_prompt(
    template: str,
    input_variables: list[str],
) -> PromptTemplate:
    prompt = PromptTemplate(
        template=template,
        input_variables=input_variables,
    )
    return prompt
