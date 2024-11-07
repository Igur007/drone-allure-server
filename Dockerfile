FROM python:3.9-slim

WORKDIR /app

COPY pyproject.toml /app/

RUN pip install poetry && poetry install --no-dev
COPY entrypoint.py /app/entrypoint.py

ENTRYPOINT ["python3", "/app/entrypoint.py"]
