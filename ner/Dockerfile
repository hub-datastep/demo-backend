FROM python:3.11

WORKDIR /app

COPY . /app/

RUN pip install poetry==1.7.1
RUN poetry config virtualenvs.create false
RUN poetry install --no-root