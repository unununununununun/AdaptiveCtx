import os
import json
import asyncio
import sys
import numpy as np
from typing import List, Dict

from sentence_transformers import SentenceTransformer
from sqlalchemy import select

from .db import Base, engine, async_session, Chunk
from mcp.server.fastmcp import FastMCP

# --- Core Logic ---
def get_encoder() -> SentenceTransformer:
    if not hasattr(get_encoder, "model"):
        model_name = os.getenv("EMBED_MODEL", "all-MiniLM-L6-v2")
        get_encoder.model = SentenceTransformer(model_name)
    return get_encoder.model

class NamespaceStore:
    def __init__(self):
        self.embeddings: List[np.ndarray] = []
        self.texts: List[str] = []
        self.meta: List[Dict] = []

    def add(self, text: str, meta: Dict | None = None):
        emb = get_encoder().encode(text, normalize_embeddings=True).astype("float32")
        self.embeddings.append(emb)
        self.texts.append(text)
        self.meta.append(meta or {})

    def search(self, query: str, k: int = 4):
        if not self.embeddings:
            return []
        emb_q = get_encoder().encode(query, normalize_embeddings=True).astype("float32")
        mat = np.vstack(self.embeddings)
        scores = mat @ emb_q
        idx = np.argsort(scores)[::-1][:k]
        return [{"text": self.texts[i], **self.meta[i], "score": float(scores[i])} for i in idx]

stores: Dict[str, NamespaceStore] = {}

def get_store(ns: str) -> NamespaceStore:
    if ns not in stores:
        stores[ns] = NamespaceStore()
    return stores[ns]

# --- Database Initialization ---
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with async_session() as ses:
        result = await ses.stream_scalars(select(Chunk))
        async for row in result:
            store = get_store(row.ns)
            store.texts.append(row.text)
            store.embeddings.append(Chunk.bytes_to_emb(row.embedding))
            store.meta.append(json.loads(row.meta or "{}"))

# --- MCP Server Definition ---
server = FastMCP(name="adaptive-memory")

@server.tool(
    name="query_memory",
    title="Query Adaptive Context",
    description="Searches the adaptive context memory for relevant information."
)
def query_context(query: str, top_k: int = 4, ns: str = "global") -> List[Dict]:
    store = get_store(ns)
    return store.search(query, k=top_k)

@server.tool(
    name="update_memory",
    title="Update Adaptive Memory",
    description="Adds a block of text content to the adaptive context memory."
)
def update_memory(content: str, ns: str = "global") -> Dict:
    text = content
    store = get_store(ns)
    meta = {"source": "update_chat"}
    store.add(text, meta)

    async def _db_update():
        async with async_session() as ses:
            async with ses.begin():
                emb_bytes = Chunk.emb_to_bytes(store.embeddings[-1])
                ses.add(Chunk(ns=ns, text=text, embedding=emb_bytes, meta=json.dumps(meta)))
    
    try:
        loop = asyncio.get_running_loop()
        loop.create_task(_db_update())
    except RuntimeError:
        # Fallback for environments without a running loop
        asyncio.run(_db_update())

    return {"ok": True, "message": "Memory update queued."}

if __name__ == "__main__":
    print("Initializing database and loading context...", file=sys.stderr)
    asyncio.run(init__db())
    print("Initialization complete. Starting MCP server on stdio...", file=sys.stderr)
    server.run(transport="stdio")
