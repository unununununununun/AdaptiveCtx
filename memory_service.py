"""Adaptive Context Memory Service – minimal MVP.

Exposes:
 • POST /update {q,a,ns}
 • POST /query  {query,top_k,ns}
 • GET  /health

In-memory NumPy vector search; data persisted to SQLite/PostgreSQL via SQLAlchemy async.
"""

import os
import numpy as np
from typing import List, Dict
from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel, Field
from sentence_transformers import SentenceTransformer

from db import Base, engine, async_session, Chunk
from sqlalchemy import select

# -----------------------------------------------------------------------------
# Config & helpers
# -----------------------------------------------------------------------------

_VALID_KEYS = set(filter(None, os.getenv("ADCTX_API_KEYS", "").split(",")))


def api_key_dep(x_api_key: str | None = Header(None, alias="X-API-Key")):
    """Simple API-key auth dependency."""
    if _VALID_KEYS and (x_api_key not in _VALID_KEYS):
        raise HTTPException(status_code=401, detail="Invalid or missing API key")


def get_encoder() -> SentenceTransformer:
    """Singleton SentenceTransformer."""
    if not hasattr(get_encoder, "model"):
        model_name = os.getenv("EMBED_MODEL", "all-MiniLM-L6-v2")
        get_encoder.model = SentenceTransformer(model_name)
    return get_encoder.model  # type: ignore


class NamespaceStore:
    """Thread-unsafe in-memory store per namespace (fits MVP needs)."""

    def __init__(self):
        self.embeddings: List[np.ndarray] = []  # list of 1-D float32
        self.texts: List[str] = []

    def add(self, text: str):
        emb = get_encoder().encode(text, normalize_embeddings=True).astype("float32")
        self.embeddings.append(emb)
        self.texts.append(text)

    def search(self, query: str, k: int = 4):
        if not self.embeddings:
            return []
        emb_q = get_encoder().encode(query, normalize_embeddings=True).astype("float32")
        mat = np.vstack(self.embeddings)  # (n, d)
        scores = mat @ emb_q  # cosine sim since vectors are normalized
        idx = np.argsort(scores)[::-1][:k]
        return [{"text": self.texts[i], "score": float(scores[i])} for i in idx]


stores: Dict[str, NamespaceStore] = {}


def get_store(ns: str) -> NamespaceStore:
    if ns not in stores:
        stores[ns] = NamespaceStore()
    return stores[ns]


# -----------------------------------------------------------------------------
# Pydantic models
# -----------------------------------------------------------------------------


class UpdatePayload(BaseModel):
    q: str
    a: str
    ns: str = Field("global")


class QueryPayload(BaseModel):
    query: str
    top_k: int = Field(4, ge=1, le=20)
    ns: str = Field("global")


# -----------------------------------------------------------------------------
# FastAPI app
# -----------------------------------------------------------------------------


app = FastAPI(title="AdaptiveCtx API – MVP")


@app.on_event("startup")
async def _init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # warm-up: load all chunks into RAM (could be large – acceptable for MVP)
    async with async_session() as ses:
        result = await ses.stream_scalars(select(Chunk))
        async for row in result:
            store = get_store(row.ns)
            store.texts.append(row.text)
            store.embeddings.append(Chunk.bytes_to_emb(row.embedding))


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/update")
async def update(p: UpdatePayload, _auth: None = Depends(api_key_dep)):
    text = f"Q: {p.q}\nA: {p.a}"
    store = get_store(p.ns)
    store.add(text)

    # persist
    async with async_session() as ses:
        async with ses.begin():
            emb_bytes = Chunk.emb_to_bytes(store.embeddings[-1])
            ses.add(Chunk(ns=p.ns, text=text, embedding=emb_bytes, meta=None))

    return {"ok": True}


@app.post("/query")
async def query(p: QueryPayload, _auth: None = Depends(api_key_dep)):
    res = get_store(p.ns).search(p.query, k=p.top_k)
    return res
