from langchain.chains.llm import LLMChain
from langchain_core.prompts import PromptTemplate
from langchain_openai import AzureChatOpenAI

from infra.env import env

CIM_MAPPING_PROMPT_TEMPLATE = """
You are an expert with expertise in both construction and data matching. Your role is to match a 
CIM model and its parameters (type and material) with a list of work types based on semantic 
relevance and practical knowledge of construction practices.
You have comprehensive knowledge of construction materials, methods, and practices.
You understand various construction products and their applications, including how different 
materials and types are used in different types of construction work.
You can identify and comprehend the role and application of each specified model in construction, 
understanding how each model is utilized in building projects.
Analyze the model parameters, including type (сборный or монолитный) and material.
Extract the key attributes from the model to facilitate accurate matching.
Use your construction knowledge and the extracted model parameters to semantically match the most 
appropriate work type from the provided list.
Ensure that the match considers both the model's type and material to ensure precision.
Only match models with the work types listed in the provided work type list.
Present only the single most suitable work type.

Input data:
    Model: {model_name}
    Type: {model_type}
    Material: {model_material}
    Work_types: {work_types_str}

Your answer should be in the format: "<work_type>"
If you can't find correct work, your answer should be: "не найдено"
You must answer in Russian.
"""


def get_chain_for_cim():
    llm = AzureChatOpenAI(
        deployment_name=env.AZURE_DEPLOYMENT_CIM_MAPPING,
        temperature=0,
        verbose=True,
    )

    prompt = PromptTemplate(
        template=CIM_MAPPING_PROMPT_TEMPLATE,
        input_variables=["model_name", "model_type", "model_material", "work_types_str"]
    )

    return LLMChain(llm=llm, prompt=prompt)
