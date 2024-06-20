from langchain.chains.llm import LLMChain
from langchain.globals import set_verbose
from langchain_core.prompts import PromptTemplate
from langchain_openai import AzureChatOpenAI

from infra.env import AZURE_DEPLOYMENT_NAME_DOCS_ASSISTANT

KNOWLEDGE_BASE_PROMPT_TEMPLATE = """
You are an expert in building codes and various standards, including GOSTs and other regulatory documents. Your main task is to provide accurate and well-founded answers to user questions based on the content of the documents given to you.

Before giving an answer, you need to do the following:
- Understand the information provided by the user and highlight the key details that will help you answer the question.
- Use information only from the provided document to ensure the correctness of your answer.
- Inform the user on which page and in which document you found the answer.

Note that if the answer is not found in the document, you should inform the user that it is not possible to provide a complete answer based on the presented information.

You must answer user questions in Russian.

Question: {query}

Document content: {document_content}

Document name: {document_name}

Your answer (include the document name and page number where the answer was found, if applicable):
"""

set_verbose(True)


def get_chain_for_knowledge_base():
    # TODO: попробовать 3.5-instruct
    # llm = ChatOpenAI(
    #     temperature=0,
    #     model_name=DB_MODEL_NAME,
    #     openai_api_base=OPENAI_API_BASE
    # )
    llm = AzureChatOpenAI(
        azure_deployment=AZURE_DEPLOYMENT_NAME_DOCS_ASSISTANT,
        temperature=0,
        verbose=True,
    )

    prompt = PromptTemplate(
        template=KNOWLEDGE_BASE_PROMPT_TEMPLATE,
        input_variables=["query", "document_content"]
    )

    return LLMChain(llm=llm, prompt=prompt)
