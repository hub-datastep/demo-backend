from langchain.chains.llm import LLMChain
from langchain_core.prompts import PromptTemplate
from langchain_openai import AzureChatOpenAI

from infra.env import env

SEARCH_RELEVANT_DESCRIPTION_PROMPT_TEMPLATE = """
You are an expert in analyzing and matching documents. Given a question and a list of document 
descriptions with their respective filenames,
determine which document is most relevant to answer the question.

Document descriptions:
{documents}

Question:
{query}

Provide the name of the document that is most relevant to answer the question.
If there is no relevant document, provide the word "None".
Your answer should be in the format: <storage_filename> or "None"
You must answer in Russian.
"""


def get_chain_for_relevant_description():
    llm = AzureChatOpenAI(
        deployment_name=env.AZURE_DEPLOYMENT_NAME_DOCS_ASSISTANT,
        temperature=0,
        verbose=True,
    )

    prompt = PromptTemplate(
        template=SEARCH_RELEVANT_DESCRIPTION_PROMPT_TEMPLATE,
        input_variables=["documents", "query"]
    )

    return LLMChain(llm=llm, prompt=prompt)
