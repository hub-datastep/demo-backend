from dotenv import load_dotenv
from langchain import OpenAI, ConversationChain, PromptTemplate
from langchain.memory import ChatMessageHistory, ConversationBufferWindowMemory

from dto.chat_dto import ChatOutDto
from repository.chat_repository import chat_repository
from service.auth_service import AuthService

load_dotenv()

template = """The following is a friendly conversation between a human and an AI. The AI is talkative and provides lots of specific details from its context. If there is no information in chat history to answer the question, it says None.

Current conversation:
{history}
Human: {input}
AI:"""


class DatastepMemoryChain:
    def __init__(self):
        self.chain = self.get_chain()

    def run(self, query):
        new_memory = self.get_memory()
        self.chain.memory = new_memory
        return self.chain.predict(input=query)

    def get_chain(self):
        memory = self.get_memory()
        return ConversationChain(
            llm=OpenAI(temperature=0, model_name="gpt-3.5-turbo-16k"),
            memory=memory,
            verbose=True,
            prompt=PromptTemplate(input_variables=["history", "input"], template=template)
        )

    def get_memory(self):
        # user = AuthService.get_current_user()
        chat = chat_repository.fetch_by_user_id("89d269f0-cb51-4e10-8ff2-a03a960ba094")
        history = self.get_history(chat)
        return ConversationBufferWindowMemory(llm=OpenAI(temperature=0), chat_memory=history)

    @classmethod
    def get_history(cls, chat: ChatOutDto):
        history = ChatMessageHistory()
        for message in chat.message:
            if message.query:
                history.add_user_message(message.query)
            elif message.table:
                history.add_ai_message(message.table)
        return history


datastep_memory_chain = DatastepMemoryChain()

print(datastep_memory_chain.run("Кто из сотрудников больше всех зарабатывает?"))
