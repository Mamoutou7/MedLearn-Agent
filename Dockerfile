FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential curl \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md ./
COPY src ./src
COPY scripts ./scripts

RUN pip install --upgrade pip setuptools wheel \
    && pip install -e .

RUN adduser --disabled-password --gecos "" --uid 10001 appuser \
    && mkdir -p /app/.data /tmp/medlearn \
    && chown -R appuser:appuser /app /tmp/medlearn

USER appuser

EXPOSE 8000

CMD ["sh", "-c", "uvicorn healthbot.api.app:app --host 0.0.0.0 --port ${PORT:-8000}"]