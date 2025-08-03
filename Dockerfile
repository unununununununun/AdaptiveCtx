# syntax=docker/dockerfile:1.4
FROM python:3.11-slim

WORKDIR /app

# --- dependencies -----------------------------------------------------------
# Only git is required for sentence-transformers to clone model repo metadata.
# build-essential убрали — faiss-cpu поставляется как готовый wheel.
RUN apt-get update \
    && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

# --- Torch ---------------------------------------------------------------
ARG TORCH_VARIANT=cpu  # cpu | cu118 | cu121 ...
ENV TORCH_VARIANT=${TORCH_VARIANT}

# Отдельно ставим PyTorch нужной сборки, так слой кэшируется отдельно
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-cache-dir torch==2.2.1+${TORCH_VARIANT} \
        --extra-index-url https://download.pytorch.org/whl/${TORCH_VARIANT}

# --- Python deps ---------------------------------------------------------
COPY requirements.txt ./
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-cache-dir -r requirements.txt

# --- source code ------------------------------------------------------------
COPY . .

ENV PYTHONUNBUFFERED=1
EXPOSE 8000

# --- run --------------------------------------------------------------------
CMD ["uvicorn", "adaptive_ctx.memory_service:app", "--host", "0.0.0.0", "--port", "8000"]