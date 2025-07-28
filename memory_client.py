"""Lightweight HTTP client to talk with AdaptiveCtx memory service.

Usage (two-liner):
    from memory_client import query, update
    ctx = query("Hello")
    update("Hello", "World")

Env-vars (all optional):
    MEMORY_API       default http://localhost:8000
    MEMORY_API_KEY   default secret123
"""
from typing import List, Dict
import os, requests

API  = os.getenv("MEMORY_API", "http://localhost:8000")
KEY  = os.getenv("MEMORY_API_KEY", "secret123")
HEAD = {"X-API-Key": KEY, "Content-Type": "application/json"}
TIMEOUT = 5

def query(text: str, ns: str = "chat", k: int = 4) -> List[Dict]:
    """Return top-k memories for given text."""
    r = requests.post(
        f"{API}/query",
        headers=HEAD,
        json={"query": text, "top_k": k, "ns": ns},
        timeout=TIMEOUT,
    )
    r.raise_for_status()
    return r.json()

def update(q: str, a: str, ns: str = "chat") -> None:
    """Save new Q/A pair into memory service."""
    r = requests.post(
        f"{API}/update",
        headers=HEAD,
        json={"q": q, "a": a, "ns": ns},
        timeout=TIMEOUT,
    )
    r.raise_for_status()