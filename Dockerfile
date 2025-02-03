FROM python:3.11-slim

RUN apt-get update && \
  apt-get install -y --no-install-recommends redis && \
  pip install --no-cache-dir poetry==1.7.1 && \
  apt-get clean && \
  rm -rf /var/lib/apt/lists/*

ENV PATH="/root/.local/bin:${PATH}"
ENV PYTHONPATH="/app/src"

WORKDIR /app

COPY pyproject.toml poetry.lock /app/

RUN poetry config virtualenvs.create false && \
  poetry install --no-root --no-dev

COPY . /app/

# RUN mkdocs build
