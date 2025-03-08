class AlertTypeID:
    NEW_ORDER = 1
    ORDER_STATUS_UPDATED = 13


class OrderStatusID:
    PENDING = 1
    IN_PROGRESS = 2


class OrderClass:
    OTHER = "Обычная"
    EMERGENCY = "Аварийная"
    SECURITY = "Охрана"
    INTERCOM = "Домофон"
    CLEANING = "Клининг"


# API
DOMYLAND_API_BASE_URL = "https://sud-api.domyland.ru"

# Auth
DOMYLAND_APP_NAME = "Datastep"

# Chat
ORDER_CLIENT_CHAT_TARGET_TYPE_ID = 2

# "Администрация" department ID
RESPONSIBLE_DEPT_ID = 38

# DataStep AI User ID
AI_USER_ID = 15698

CLEANING_USER_ID = 15496
# Александр Специалист
TRANSFER_ACCOUNT_ID = 8067

# Message to mark AI processed orders (in internal chat)
ORDER_PROCESSED_BY_AI_MESSAGE = "ИИ классифицировал эту заявку как аварийную"
