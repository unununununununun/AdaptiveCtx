"""HTTP client for AdaptiveCtx memory service (stand-alone copy).
Identical to top-level cursor_client.client but bundled here so that
`cursor_client_example` folder can be used independently.
"""
import os, requests
from typing import List, Dict

API_URL = os.getenv("MEMORY_API", "http://localhost:8000")
API_KEY = os.getenv("MEMORY_API_KEY", "secret123")
HEADERS = {"X-API-Key": API_KEY, "Content-Type": "application/json"}

def query(text: str, ns: str = "global", k: int = 4) -> List[Dict]:
    r = requests.post(f"{API_URL}/query", headers=HEADERS,
                      json={"query": text, "top_k": k, "ns": ns})
    r.raise_for_status()
    return r.json()

def update(q: str, a: str, ns: str = "global") -> None:
    r = requests.post(f"{API_URL}/update", headers=HEADERS,
                      json={"q": q, "a": a, "ns": ns})
    r.raise_for_status()