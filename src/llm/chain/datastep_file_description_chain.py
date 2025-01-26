from langchain.chains.llm import LLMChain
from langchain_core.prompts import PromptTemplate
from langchain_openai import AzureChatOpenAI

from infra.env import AZURE_DEPLOYMENT_NAME_DOCS_ASSISTANT

DESCRIPTION_PROMPT_TEMPLATE = """
You are an expert in analyzing and summarizing documents. 
Given the content of a document, generate a concise and informative description of its contents.

Document content:
{document_content}

Provide a brief description of the document.
Your answer should be in the format: "<description>"
You must answer in Russian.
"""


def get_chain():
    llm = AzureChatOpenAI(
        azure_deployment=AZURE_DEPLOYMENT_NAME_DOCS_ASSISTANT,
        temperature=0,
        verbose=True,
    )

    prompt = PromptTemplate(
        template=DESCRIPTION_PROMPT_TEMPLATE,
        input_variables=["document_content"]
    )

    return LLMChain(llm=llm, prompt=prompt)
