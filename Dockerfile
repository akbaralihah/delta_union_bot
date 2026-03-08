# Stage 1: Build
FROM ghcr.io/astral-sh/uv:python3.12-alpine AS builder

WORKDIR /app
COPY pyproject.toml .
RUN uv export --no-dev --format requirements-txt > requirements.txt

# Stage 2: Final
FROM python:3.12-alpine

WORKDIR /app

# Install system dependencies for asyncpg
RUN apk add --no-cache libpq-dev gcc musl-dev

COPY --from=builder /app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

CMD ["python", "main.py"]
