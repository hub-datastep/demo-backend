from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from parsing import parsing

app = FastAPI()

# Auth
app.include_router(parsing.router, tags=["parsing"], prefix="/parsing")




# Built docs dir
# app.mount("/mkdocs", StaticFiles(directory=Path(__file__).parent / ".." / "site", html=True), name="mkdocs")
# app.mount("/static", StaticFiles(directory=Path(__file__).parent / ".." / "data"), name="static")

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8080, reload=True)
