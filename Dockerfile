FROM python:3

RUN pip install poetry
ENV PATH="${PATH}:/root/.local/bin"

WORKDIR /app

COPY poetry.lock pyproject.toml ./
RUN poetry config virtualenvs.create false \
    && poetry install --no-root

COPY src ./

CMD ["python3", "app.py"]