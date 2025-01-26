from langchain.chains.llm import LLMChain
from langchain_core.prompts import PromptTemplate
from langchain_openai import AzureChatOpenAI

from infra.env import env

DOCS_PROMPT_TEMPLATE = """
You are a lawyer specializing in the field of legal documents,
you understand various types of legal documentation like
contracts, charters, regulations and others.
You clearly understand the contents of the documents and perfectly answer questions about them.
Determine the type and scope of the legal document to answer the question.
Highlight the key points and terms of the document to answer the question.

The content of the document can be solid text without spaces,
you need semantically place spaces between words.



Question:
{query}

Document content:
{document_content}

You must answer in Russian language.
Your answer:
"""


def get_chain_for_docs():
    llm = AzureChatOpenAI(
        deployment_name=env.AZURE_DEPLOYMENT_NAME_DOCS_ASSISTANT,
        temperature=0,
        verbose=True,
    )

    prompt = PromptTemplate(
        template=DOCS_PROMPT_TEMPLATE,
        input_variables=["query", "document_content"]
    )

    return LLMChain(llm=llm, prompt=prompt)
