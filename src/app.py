import uvicorn
from fastapi import FastAPI
from controller.parsing import parsing
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi_versioning import VersionedFastAPI
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

from controller.auth import auth_controller
from controller.chat import message_controller, chat_controller
from controller.file import file_controller
from controller.mode import mode_controller
from controller.prediction import prediction_controller
from controller.prompt import prompt_controller
from controller.role import role_controller
from controller.tenant import tenant_controller
from controller.user import user_controller
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

# Parsing PDF files
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
