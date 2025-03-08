from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi_versioning import VersionedFastAPI
from loguru import logger
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

from controller.auth import auth_controller
from controller.chat import message_controller, chat_controller
from controller.chroma_collection import chroma_collection_controller
from controller.classifier import classifier_config_controller, classifier_controller
from controller.embedding import embedding_controller
from controller.file import file_controller
from controller.kafka import kafka_controller
from controller.ksr import ksr_controller
from controller.mapping import (
    mapping_controller,
    mapping_with_parsing_controller,
    mapping_result_controller,
)
from controller.mode import mode_controller
from controller.ner import brand_model_controller
from controller.order_classification.vysota import (
    order_classification_controller as vysota_order_classification_controller,
    order_notification_controller as vysota_order_notification_controller,
)
from controller.prediction import prediction_controller
from controller.prompt import prompt_controller
from controller.role import role_controller
from controller.solution_imitation import solution_imitation_controller
from controller.task import task_controller
from controller.tenant import tenant_controller
from controller.used_token import used_token_controller
from controller.user import user_controller
from infra.env import env
from util.healthcheck.redis_connection import check_redis_connection

app = FastAPI()

# Auth
app.include_router(
    auth_controller.router,
    prefix="/auth",
    tags=["Auth"],
)

# User
app.include_router(
    user_controller.router,
    prefix="/user",
    tags=["User"],
)

# Role
app.include_router(
    role_controller.router,
    prefix="/role",
    tags=["Role"],
)

# Tenant
app.include_router(
    tenant_controller.router,
    prefix="/tenant",
    tags=["Tenant"],
)

# Mode
app.include_router(
    mode_controller.router,
    prefix="/mode",
    tags=["Mode"],
)

# Prompt
app.include_router(
    prompt_controller.router,
    prefix="/prompt",
    tags=["Prompt"],
)

# Chat
app.include_router(
    chat_controller.router,
    prefix="/chat",
    tags=["Chat"],
)
app.include_router(
    message_controller.router,
    prefix="/message",
    tags=["Message"],
)
# app.include_router(mark_controller.router, tags=["mark"], prefix="/mark",)
# app.include_router(review_controller.router, tags=["review"], prefix="/review",)

# Assistants
app.include_router(
    prediction_controller.router,
    tags=["Prediction"],
)
app.include_router(
    file_controller.router,
    prefix="/file",
    tags=["File"],
)

# Mapping
app.include_router(
    classifier_config_controller.router,
    prefix="/classifier/config",
    tags=["Classifier Config"],
)
app.include_router(
    mapping_controller.router,
    prefix="/mapping",
    tags=["Mapping"],
)
app.include_router(
    mapping_result_controller.router,
    prefix="/mapping/result",
    tags=["Mapping Result"],
)
app.include_router(
    embedding_controller.router,
    prefix="/embedding",
    tags=["Embedding"],
)
# app.include_router(
#     synchronize_controller.router,
#     tags=["synchronize"],
#     prefix="/synchronize",
# )
app.include_router(
    chroma_collection_controller.router,
    prefix="/collection",
    tags=["Chroma Collection"],
)
app.include_router(
    classifier_controller.router,
    prefix="/classifier",
    tags=["Classifier"],
)
app.include_router(
    brand_model_controller.router,
    prefix="/ner/brand",
    tags=["NER Brand"],
)
# Mapping with Parsing
app.include_router(
    mapping_with_parsing_controller.router,
    prefix="/mapping/with_parsing",
    tags=["Mapping with Parsing"],
)

# Used Tokens
app.include_router(
    used_token_controller.router,
    prefix="/used_token",
    tags=["Used Token"],
)

# Redis Tasks
app.include_router(
    task_controller.router,
    prefix="/task",
    tags=["Task"],
)

# KSR Nomenclature
app.include_router(
    ksr_controller.router,
    prefix="/ksr",
    tags=["KSR"],
)

# Solution Imitation
app.include_router(
    solution_imitation_controller.router,
    prefix="/solution_imitation",
    tags=["Solution Imitation"],
)

# Order Classification
# Vysota Service
app.include_router(
    vysota_order_classification_controller.router,
    prefix="/classification/orders",
    tags=["Orders Classification"],
)
app.include_router(
    vysota_order_notification_controller.router,
    prefix="/notification/orders",
    tags=["Orders Notifications"],
)

# Unistroy Kafka Mapping
app.include_router(
    kafka_controller.router,
    prefix="/kafka",
    tags=["Kafka"],
)


@app.get("/healthcheck")
def healthcheck():
    logger.debug(f"Data Folder Path: {env.DATA_FOLDER_PATH}")
    check_redis_connection()
    return {"status": "ok"}


app = VersionedFastAPI(
    app,
    version_format="{major}",
    prefix_format="/api/v{major}",
    middleware=[
        Middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_methods=["POST", "GET", "PUT", "DELETE"],
            allow_headers=["*"],
        )
    ],
)

# @app.middleware("http")
# async def catch_exceptions_middleware(request: Request, call_next):
#     try:
#         return await call_next(request)
#     except Exception as e:
#         return HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail={
#                 "message": f"{e}",
#                 "traceback": traceback.format_exception(e),
#             },
#         )


# Built docs dir
# app.mount(
#     "/mkdocs",
#     StaticFiles(
#         directory=Path(__file__).parent / ".." / "site",
#         html=True,
#     ),
#     name="mkdocs",
# )

app.mount(
    "/static",
    StaticFiles(directory=Path(__file__).parent / ".." / "data"),
    name="static",
)

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8080, reload=True)
