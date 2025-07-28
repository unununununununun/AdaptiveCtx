"""Local copy of AdaptiveCtx HTTP client.
Provides query() and update() functions to interact with the memory service.
This file is identical to the root-level memory_client.py but is bundled here
so that the folder `cursor_memory_agent` can be used standalone in Cursor.
"""
import os, requests
from typing import List, Dict

API  = os.getenv("MEMORY_API", "http://localhost:8000")
KEY  = os.getenv("MEMORY_API_KEY", "secret123")
HEAD = {"X-API-Key": KEY, "Content-Type": "application/json"}
TIMEOUT = 5

def query(text: str, ns: str = "chat", k: int = 4) -> List[Dict]:
    r = requests.post(f"{API}/query", headers=HEAD,
                      json={"query": text, "top_k": k, "ns": ns},
                      timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()

def update(q: str, a: str, ns: str = "chat") -> None:
    r = requests.post(f"{API}/update", headers=HEAD,
                      json={"q": q, "a": a, "ns": ns},
                      timeout=TIMEOUT)
    r.raise_for_status()