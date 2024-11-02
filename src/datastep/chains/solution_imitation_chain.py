from langchain.chains.llm import LLMChain
from langchain_core.prompts import PromptTemplate
from langchain_openai import AzureChatOpenAI

from infra.env import AZURE_DEPLOYMENT_NAME_EMERGENCY_CLASSIFICATION
from scheme.solution_imitation.solution_immitation_llm_output_scheme import LLMOutputTable


def _get_solution_imitation_structured_llm() -> AzureChatOpenAI:
    llm = AzureChatOpenAI(
        azure_deployment=AZURE_DEPLOYMENT_NAME_EMERGENCY_CLASSIFICATION,
        temperature=0,
        verbose=False,
    )
    structured_llm = llm.with_structured_output(LLMOutputTable, method="json_mode")
    return structured_llm


def get_solution_imitation_chain(prompt: PromptTemplate):
    structured_llm = _get_solution_imitation_structured_llm()
    return LLMChain(llm=structured_llm, prompt=prompt)


def get_solution_imitation_prompt(
    template: str,
    input_variables: list[str],
) -> PromptTemplate:
    prompt = PromptTemplate(
        template=template,
        input_variables=input_variables,
    )
    return prompt
