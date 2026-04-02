FROM python:3.13-slim
WORKDIR /app

RUN apt-get update && apt-get install -y gcc && \
    pip install --no-cache-dir "poetry<2.0.0"

COPY pyproject.toml ./

RUN poetry config virtualenvs.create false && \
    poetry lock && \
    poetry install --no-root --no-interaction --no-ansi

COPY . .

EXPOSE 8000

CMD ["sh", "-c", "alembic upgrade head && uvicorn src.main:app --host 0.0.0.0 --port 8000"]