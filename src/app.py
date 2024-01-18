import traceback
from pathlib import Path

import uvicorn as uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi_versioning import VersionedFastAPI
from requests import Request
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from dotenv import load_dotenv

from controller.file import task_controller, file_controller, task_websocket_controller

# from controller.nomenclature import nomenclature_controller

load_dotenv()

# from controller import (
#     auth_controller, chat_controller,
#     datastep_controller, mark_controller,
#     message_controller, prompt_controller,
#     question_controller, review_controller,
#     logo_controller, config_controller,
#     chat_pdf_controller, user_controller,
#     tenant_controller, file_controller,
#     task_controller, task_websocket_controller,
#     nomenclature_controller
# )

from controller.prediction import prediction_controller, chat_pdf_controller
from controller.user import user_controller, tenant_controller, auth_controller, prompt_controller, config_controller
from controller.chat import message_controller, mark_controller, chat_controller, review_controller
from infra.database import create_db_and_tables, create_mock_data, get_session

load_dotenv()

app = FastAPI()

app.include_router(auth_controller.router, tags=["auth"], prefix="/auth")
app.include_router(user_controller.router, tags=["user"], prefix="/user")
app.include_router(tenant_controller.router, tags=["tenant"], prefix="/tenant")
app.include_router(config_controller.router, tags=["config"], prefix="/config")
app.include_router(prompt_controller.router, tags=["prompt"], prefix="/prompt")
app.include_router(chat_controller.router, tags=["chat"], prefix="/chat")
app.include_router(message_controller.router, tags=["message"], prefix="/message")
app.include_router(mark_controller.router, tags=["mark"], prefix="/mark")
app.include_router(review_controller.router, tags=["review"], prefix="/review")
app.include_router(prediction_controller.router, tags=["prediction"])
# app.include_router(nomenclature_controller.router, tags=["nomenclature"], prefix="/nomenclature")
app.include_router(file_controller.router, tags=["file"], prefix="/file")
app.include_router(task_controller.router, tags=["task"], prefix="/task")


@app.middleware("http")
async def catch_exceptions_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"message": f"{e}", "traceback": traceback.format_exception(e)},
        )


app = VersionedFastAPI(
    app,
    version_format="{major}",
    prefix_format="/api/v{major}",
    middleware=[
        Middleware(
            CORSMiddleware,
            allow_origins=[
                "https://msu-frontend.fly.dev",
                "https://msu-frontend-dev.fly.dev",
                "https://datastep-frontend-mock.fly.dev",
                "http://localhost:3000",
                "http://45.8.98.160:3000"
            ],
            allow_methods=["POST", "GET", "PUT", "DELETE"],
            allow_headers=["*"],
        )
    ]
)

app.include_router(task_websocket_controller.router, tags=["task"], prefix="/task/ws")
app.mount("/static", StaticFiles(directory=Path(__file__).parent / ".." / "data"), name="static")

@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    # create_mock_data()


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8080, reload=False)
