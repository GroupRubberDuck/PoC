# =========================
# 1️⃣ Builder stage
# =========================
FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system deps
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry via pip (more reliable in Docker)
RUN pip install --no-cache-dir poetry

# Copy only dependency files first (better caching)
COPY pyproject.toml poetry.lock ./

# Disable virtualenv creation
RUN poetry config virtualenvs.create false

# Install dependencies (no dev)
RUN poetry install --only main --no-root --no-interaction --no-ansi
# =========================
# 2️⃣ Runtime stage
# =========================
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Copy installed site-packages + binaries
COPY --from=builder /usr/local/lib/python3.12 /usr/local/lib/python3.12
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy project
COPY . .

# Non-root user
RUN useradd -m appuser
USER appuser

CMD ["python", "-m", "myapp.main"]