import uvicorn as uvicorn
from fastapi import FastAPI

from controller import status_controller

app = FastAPI()

app.include_router(status_controller.router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
