# syntax=docker/dockerfile:1
FROM python:3.11-slim

WORKDIR /app

# Install git for sentence-transformers model downloads
RUN apt-get update && apt-get install -y --no-install-recommends git && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1
EXPOSE 9000

# Run root memory_service
CMD ["uvicorn", "memory_service:app", "--host", "0.0.0.0", "--port", "9000"]