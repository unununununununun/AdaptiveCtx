# syntax=docker/dockerfile:1
FROM python:3.11-slim

WORKDIR /app

# Install git (sentence-transformers pulls models), build deps
RUN apt-get update && apt-get install -y --no-install-recommends git && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1
EXPOSE 8000
CMD ["uvicorn", "adaptive_ctx.memory_service:app", "--host", "0.0.0.0", "--port", "8000"]