from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi_versioning import VersionedFastAPI
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

from controller.auth import auth_controller
from controller.chat import message_controller, chat_controller
from controller.chroma_collection import chroma_collection_controller
from controller.classifier import classifier_config_controller, classifier_controller
from controller.embedding import embedding_controller
from controller.file import file_controller
from controller.kafka import kafka_mapping_controller
from controller.ksr import ksr_controller
from controller.mapping import mapping_controller
from controller.mode import mode_controller
from controller.ner import brand_model_controller
from controller.order_classification.vysota import \
    order_classification_controller as vysota_order_classification_controller
from controller.prediction import prediction_controller
from controller.prompt import prompt_controller
from controller.role import role_controller
from controller.solution_imitation import solution_imitation_controller
from controller.task import task_controller
from controller.tenant import tenant_controller
from controller.used_token import used_token_controller
from controller.user import user_controller
from controller.parsing import parsing
from util.healthcheck.redis_connection import check_redis_connection

app = FastAPI()

# Auth
app.include_router(auth_controller.router, tags=["auth"], prefix="/auth")

# User
app.include_router(user_controller.router, tags=["user"], prefix="/user")

# Role
app.include_router(role_controller.router, tags=["role"], prefix="/role")

# Tenant
app.include_router(tenant_controller.router, tags=["tenant"], prefix="/tenant")

# Mode
app.include_router(mode_controller.router, tags=["mode"], prefix="/mode")

# Prompt
app.include_router(prompt_controller.router, tags=["prompt"], prefix="/prompt")

# Chat
app.include_router(chat_controller.router, tags=["chat"], prefix="/chat")
app.include_router(message_controller.router, tags=["message"], prefix="/message")
# app.include_router(mark_controller.router, tags=["mark"], prefix="/mark")
# app.include_router(review_controller.router, tags=["review"], prefix="/review")

# Assistants
app.include_router(prediction_controller.router, tags=["prediction"])
app.include_router(file_controller.router, tags=["file"], prefix="/file")

# Nomenclature
app.include_router(classifier_config_controller.router, tags=["classifier_config"], prefix="/classifier_config")
app.include_router(mapping_controller.router, tags=["mapping"], prefix="/mapping")
app.include_router(embedding_controller.router, tags=["embedding"], prefix="/embedding")
# app.include_router(synchronize_controller.router, tags=["synchronize"], prefix="/synchronize")
app.include_router(chroma_collection_controller.router, tags=["chroma_collection"], prefix="/collection")
app.include_router(classifier_controller.router, tags=["classifier"], prefix="/classifier")
app.include_router(brand_model_controller.router, tags=["ner_brand"], prefix="/ner_brand")

# Used Tokens
app.include_router(used_token_controller.router, tags=["used_token"], prefix="/used_token")

# Other
app.include_router(task_controller.router, tags=["task"], prefix="/task")

# Ksr Nomenclature
app.include_router(ksr_controller.router, tags=["ksr"], prefix="/ksr")

# Solution Imitation
app.include_router(solution_imitation_controller.router, tags=["Solution Imitation"], prefix="/solution_imitation")

# Emergency Class
# Vysota Service
app.include_router(
    vysota_order_classification_controller.router,
    tags=["Orders Classification"],
    prefix="/classification/orders",
)

# Unistroy Kafka Mapping
app.include_router(kafka_mapping_controller.router, tags=["Kafka Mapping"], prefix="/kafka/mapping")

# Parsing utd

app.include_router(parsing.router, tags=["parsing"], prefix="/parsing")


@app.get("/healthcheck")
def healthcheck():
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
    ]
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
app.mount("/mkdocs", StaticFiles(directory=Path(__file__).parent / ".." / "site", html=True), name="mkdocs")
app.mount("/static", StaticFiles(directory=Path(__file__).parent / ".." / "data"), name="static")

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8080, reload=True)
