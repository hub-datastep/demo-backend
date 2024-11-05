from langchain.chains.llm import LLMChain
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_openai import AzureChatOpenAI

from infra.env import AZURE_DEPLOYMENT_NAME_EMERGENCY_CLASSIFICATION
from scheme.solution_imitation.solution_imitation_llm_output_scheme import LLMOutput

parser = JsonOutputParser(pydantic_object=LLMOutput)


def _get_solution_imitation_structured_llm() -> AzureChatOpenAI:
    llm = AzureChatOpenAI(
        # TODO: add other deployment for this task
        azure_deployment=AZURE_DEPLOYMENT_NAME_EMERGENCY_CLASSIFICATION,
        temperature=0,
        verbose=False,
    )
    return llm
    # structured_llm = llm.with_structured_output(
    #     schema=LLMOutput,
    #     method="json_mode",
    # )
    # return structured_llm


def get_solution_imitation_chain(prompt: PromptTemplate) -> LLMChain:
    structured_llm = _get_solution_imitation_structured_llm()
    return LLMChain(
        llm=structured_llm,
        prompt=prompt,
        verbose=False,
        output_parser=parser,
    )


def get_solution_imitation_prompt(
    template: str,
    input_variables: list[str],
) -> PromptTemplate:
    prompt = PromptTemplate(
        template=template,
        input_variables=input_variables,
    )
    return prompt
