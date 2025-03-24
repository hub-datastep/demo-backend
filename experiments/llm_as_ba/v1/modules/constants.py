# Constants for Excel file processing
REQUEST_ID_FIELD = "№"  # Field name for request ID
REQUEST_CONTENT_FIELD = "Суть обращения"  # Field name for request content
SERVICE_FIELD = "Услуга"  # Field name for service
EXECUTOR_COMMENT_FIELD = "Комментарий к статусу"  # Field name for executor comment
CHAT_HISTORY_FIELD = "Chat"  # Field name for chat history

# Constants for file paths
INPUT_FILE_PATH = "experiments/llm_as_ba/v1/[2025-03-02 - 2024-03-02] Клиентский Сервис Заявки с Чатами.xlsx"
OUTPUT_DIR_PATH = "experiments/llm_as_ba/v1/results"
SHEET_NAME = "Клиент. сервис Orders (0-100)"

# Other settings
VERBOSE = False  # Enable verbose output
WAIT_TIME_IN_SEC = 60  # Wait time for rate limit errors

# Intent and scenario types
INTENT_TYPE = "intent"
SCENARIO_TYPE_QA = "actionless_qa"
SCENARIO_TYPE_ACTION = "action_required"
