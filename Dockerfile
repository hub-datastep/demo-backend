FROM python:3.11

RUN pip install poetry
ENV PATH="${PATH}:/root/.local/bin"

RUN apt-get update
RUN apt-get install -y redis

RUN pip install --upgrade pip

RUN pip install onnxruntime
RUN pip install mkdocs-material "mkdocstrings[python]"

WORKDIR /app

COPY . /app

RUN poetry config virtualenvs.create false
RUN poetry install --no-root

RUN mkdocs build
