"""HTTP client for AdaptiveCtx memory service."""

import os
import requests
from typing import List, Dict

API_URL   = os.getenv("MEMORY_API", "http://localhost:8000")
API_KEY   = os.getenv("MEMORY_API_KEY", "secret123")
HEADERS   = {"X-API-Key": API_KEY, "Content-Type": "application/json"}

def query(text: str, ns: str = "global", k: int = 4) -> List[Dict]:
    """Return top-k slots for the given query text."""
    r = requests.post(f"{API_URL}/query", headers=HEADERS,
                      json={"query": text, "top_k": k, "ns": ns})
    r.raise_for_status()
    return r.json()


def update(q: str, a: str, ns: str = "global") -> None:
    """Add new Q/A pair to memory."""
    r = requests.post(f"{API_URL}/update", headers=HEADERS,
                      json={"q": q, "a": a, "ns": ns})
    r.raise_for_status()