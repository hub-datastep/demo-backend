import os
from typing import Generator

import requests
from dotenv import load_dotenv

load_dotenv()


class ChatPdfService:
    url = "https://api.chatpdf.com/v1/chats/message"
    source_id = os.getenv("CHAT_PDF_SOURCE_ID")
    headers = {
        "x-api-key": os.getenv("CHAT_PDF_API_KEY"),
        "Content-Type": "application/json",
    }

    @classmethod
    def run(cls, messages) -> Generator:
        try:
            response = requests.post(
                cls.url,
                json=cls.create_body(messages),
                headers=cls.headers,
                stream=True
            )
            response.raise_for_status()

            if response.iter_content:
                max_chunk_size = 1024
                for chunk in response.iter_content(max_chunk_size):
                    text = chunk.decode()
                    yield text
            else:
                raise Exception("No data received")
        except requests.exceptions.RequestException as error:
            print("Error:", error)

    @classmethod
    def create_user_message(cls, content):
        return {
            "role": "user",
            "content": content
        }

    @classmethod
    def create_assistant_message(cls, content):
        return {
            "role": "assistant",
            "content": content
        }

    @classmethod
    def create_body(cls, messages):
        return {
            "stream": True,
            "sourceId": cls.source_id,
            "messages": messages
        }


if __name__ == "__main__":
    messages = [
        {
            "role": "user",
            "content": "Как воспроизводится купонная выплата?",
        },
    ]

    for chunk in ChatPdfService.run(messages):
        print(chunk)
