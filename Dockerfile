# syntax=docker/dockerfile:1.4
FROM python:3.11-slim

WORKDIR /app

# --- dependencies -----------------------------------------------------------
# Only git is required for sentence-transformers to clone model repo metadata.
# build-essential убрали — faiss-cpu поставляется как готовый wheel.
RUN apt-get update \
    && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

# --- Python deps ------------------------------------------------------------
# requirements.txt почти не меняется, поэтому кладём раньше COPY .
COPY requirements.txt ./

# Используем BuildKit cache для pip чтоб не тянуть пакеты каждый билд
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-cache-dir -r requirements.txt

# --- source code ------------------------------------------------------------
COPY . .

ENV PYTHONUNBUFFERED=1
EXPOSE 9000

# --- run --------------------------------------------------------------------
CMD ["uvicorn", "memory_service:app", "--host", "0.0.0.0", "--port", "9000"]