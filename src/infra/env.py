import os

from dotenv import load_dotenv

load_dotenv()

OPENAI_API_BASE = os.getenv('OPENAI_API_BASE')

REDIS_HOST = os.getenv('REDIS_HOST')
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')

CHROMA_HOST = os.getenv('CHROMA_HOST')
CHROMA_PORT = os.getenv('CHROMA_PORT')

DB_CONNECTION_STRING = os.getenv('DB_CONNECTION_STRING')

FRONTEND_HOST = os.getenv('FRONTEND_HOST')

DATA_FOLDER_PATH = os.getenv('DATA_FOLDER_PATH')
