import traceback

import uvicorn as uvicorn
from fastapi import FastAPI
from requests import Request
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from controller import datastep_controller, chat_controller, message_controller, review_controller

app = FastAPI()

app.include_router(datastep_controller.router)
app.include_router(chat_controller.router)
app.include_router(message_controller.router)
app.include_router(review_controller.router)


@app.middleware("http")
async def catch_exceptions_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        print(e)
        return JSONResponse(
            status_code=500,
            content={
                "message": f"{e}",
                "traceback": traceback.format_exception(e)
            },
        )


# @app.exception_handler(Exception)
# async def base_exception_handler(request: Request, exc: Exception):
#     print("test 1")
#     return JSONResponse(
#         status_code=500,
#         content={"message": f"Internal error"},
#     )


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["POST", "GET"],
)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
