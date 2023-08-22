from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage, AIMessage, BaseMessage

load_dotenv()

# chat_model = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo-16k")
#
# messages = [
#
#     HumanMessage(content="Топ 5 компаний по доходу"),
#     AIMessage(content="""Топ 5 контрагентов по доходу:
#     1. ФСК ДЕВЕЛОПМЕНТ ООО - 30,144,051,795.03
#     2. УДМС ГКУ - 23,334,605,526.13
#     3. ДЗКС ГКУ МО - 19,505,282,124.34
#     4. МОСКОВСКИЙ ФОНД РЕНОВАЦИИ ЖИЛОЙ ЗАСТРОЙКИ - 14,476,085,171.21
#     """),
#     HumanMessage(content="У кого из них меньше всего доход?")
# ]


class DatastepMemoryChain:
    chat_model = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo-16k")
    system_message = SystemMessage(content="""
        По истории чата ответь на вопрос.
        Если в истории чата нет ответа на вопрос, просто напиши "No data".
    """)

    @classmethod
    def run(cls, messages: list[BaseMessage]) -> str | None:
        all_messages = [cls.system_message, *messages]

        for msg in all_messages:
            print(msg)

        answer = cls.chat_model.predict_messages(all_messages).content
        # print("DatastepMemoryChain answer: ", answer)
        if answer == "No data":
            return None
        else:
            return answer
