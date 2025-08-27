# syntax=docker/dockerfile:1.4
FROM python:3.11-slim

WORKDIR /app

# --- dependencies -----------------------------------------------------------
# Only git is required for sentence-transformers to clone model repo metadata.
RUN apt-get update \
    && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

# --- Torch ---------------------------------------------------------------
ARG TORCH_VARIANT=cpu  # cpu | cu118 | cu121 ...
ENV TORCH_VARIANT=${TORCH_VARIANT}

# Install PyTorch separately to cache this layer
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

# --- run --------------------------------------------------------------------
# Run the MCP server using stdio transport.
CMD ["python", "-m", "adaptive_ctx.memory_service"]
