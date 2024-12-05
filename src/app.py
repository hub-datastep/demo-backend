import uvicorn
from fastapi import FastAPI
from controller.parsing import parsing

app = FastAPI()

# Parsing PDF files
app.include_router(parsing.router, tags=["parsing"], prefix="/parsing")


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8080, reload=True)
