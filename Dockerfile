FROM python:3.11

RUN pip install poetry==1.7.1
ENV PATH="${PATH}:/root/.local/bin"

RUN apt-get update
RUN apt-get install -y redis

WORKDIR /app

COPY . /app

RUN poetry config virtualenvs.create false
RUN poetry install --no-root

RUN mkdocs build
