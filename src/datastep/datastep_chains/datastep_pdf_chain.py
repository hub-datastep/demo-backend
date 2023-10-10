from datastep.components import datastep_faiss
from langchain.chat_models import ChatOpenAI
from langchain import PromptTemplate
from langchain.chains import LLMChain


def _get_chain():
    llm = ChatOpenAI(temperature=0)
    template = """По данному тексту ответь на вопрос

    Вопрос:
    {query}

    Текст:
    {text}"""

    prompt = PromptTemplate(
        template=template,
        input_variables=["query", "text"]
    )

    return LLMChain(llm=llm, prompt=prompt)


def get_prediction(source_id: str, query: str):
    chain = _get_chain()
    doc = datastep_faiss.search(source_id, query)
    return chain.run(
        query=query,
        text=doc.page_content
    )


if __name__ == "__main__":
    print(get_prediction("123", "Выплата по купону"))
