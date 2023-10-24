import traceback

import sentry_sdk
import uvicorn as uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi_versioning import VersionedFastAPI
from requests import Request
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from controller import (
    auth_controller, chat_controller,
    datastep_controller, mark_controller,
    message_controller, prompt_controller,
    question_controller, review_controller,
    source_controller, logo_controller,
    chat_pdf_controller, user_controller,
    tenant_controller, file_controller,
    task_controller, task_websocket_controller
)

sentry_sdk.init(
    dsn="https://a93b994680a287f702ca14bc34dffb35@o4505793939963904.ingest.sentry.io/4505793941995520",
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production.
    traces_sample_rate=1.0,
    # Set profiles_sample_rate to 1.0 to profile 100%
    # of sampled transactions.
    # We recommend adjusting this value in production.
    profiles_sample_rate=1.0,
)

load_dotenv()

app = FastAPI()

app.include_router(auth_controller.router)
app.include_router(datastep_controller.router)
app.include_router(chat_pdf_controller.router)
app.include_router(chat_controller.router)
app.include_router(message_controller.router)
app.include_router(review_controller.router)
app.include_router(mark_controller.router)
app.include_router(prompt_controller.router)
app.include_router(source_controller.router)
app.include_router(question_controller.router)
app.include_router(logo_controller.router)
app.include_router(user_controller.router)
app.include_router(tenant_controller.router)
app.include_router(file_controller.router)
app.include_router(task_controller.router)


@app.middleware("http")
async def catch_exceptions_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        print(e)
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
                "http://localhost:3000"
            ],
            allow_methods=["POST", "GET", "PUT", "DELETE"],
            allow_headers=["*"],
        )
    ]
)

app.include_router(task_websocket_controller.router)

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8080, reload=False)
