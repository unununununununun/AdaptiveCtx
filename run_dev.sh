#!/usr/bin/env bash
# Start AdaptiveCtx API for local development
uvicorn memory_service:app --reload --host 0.0.0.0 --port 9000