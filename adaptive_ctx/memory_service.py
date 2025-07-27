"""AdaptiveCtx API service (async)."""

import os, json, io
import numpy as np
from typing import List, Dict
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from sentence_transformers import SentenceTransformer

from .db import Base, engine, async_session, Chunk
from sqlalchemy import select

# -----------------------------------------------------------------------------
# Config & helpers
# -----------------------------------------------------------------------------

_VALID_KEYS = set(filter(None, os.getenv("ADCTX_API_KEYS", "").split(",")))


def api_key_dep(x_api_key: str | None = Header(None, alias="X-API-Key")):
    if _VALID_KEYS and (x_api_key not in _VALID_KEYS):
        raise HTTPException(status_code=401, detail="Invalid or missing API key")


def get_encoder() -> SentenceTransformer:
    if not hasattr(get_encoder, "model"):
        model_name = os.getenv("EMBED_MODEL", "all-MiniLM-L6-v2")
        get_encoder.model = SentenceTransformer(model_name)
    return get_encoder.model  # type: ignore


class NamespaceStore:
    def __init__(self):
        self.embeddings: List[np.ndarray] = []
        self.texts: List[str] = []

    def add(self, text: str):
        emb = get_encoder().encode(text, normalize_embeddings=True).astype("float32")
        self.embeddings.append(emb)
        self.texts.append(text)

    def search(self, query: str, k: int = 4):
        if not self.embeddings:
            return []
        emb_q = get_encoder().encode(query, normalize_embeddings=True).astype("float32")
        mat = np.vstack(self.embeddings)
        scores = mat @ emb_q
        idx = np.argsort(scores)[::-1][:k]
        return [{"text": self.texts[i], "score": float(scores[i])} for i in idx]


stores: Dict[str, NamespaceStore] = {}

def get_store(ns: str) -> NamespaceStore:
    if ns not in stores:
        stores[ns] = NamespaceStore()
    return stores[ns]

# -----------------------------
# Pydantic models
# -----------------------------

class UpdatePayload(BaseModel):
    q: str
    a: str
    ns: str = Field("global")


class QueryPayload(BaseModel):
    query: str
    top_k: int = Field(4, ge=1, le=20)
    ns: str = Field("global")

class ImportPayload(BaseModel):
    ns: str = Field("global")
    items: List[Dict]

# -----------------------------
# FastAPI app
# -----------------------------

app = FastAPI(title="AdaptiveCtx API – MVP")

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def dashboard_root():
    try:
        with open("static/index.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "<h2>Dashboard not found. Build assets into ./static/index.html</h2>"


@app.on_event("startup")
async def _init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
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

    async with async_session() as ses:
        async with ses.begin():
            emb_bytes = Chunk.emb_to_bytes(store.embeddings[-1])
            ses.add(Chunk(ns=p.ns, text=text, embedding=emb_bytes))
            # enqueue for training
            from .db import TrainSample
            ses.add(TrainSample(ns=p.ns, text=text))
    return {"ok": True}


@app.post("/query")
async def query(p: QueryPayload, _auth: None = Depends(api_key_dep)):
    return get_store(p.ns).search(p.query, k=p.top_k)


# Admin endpoints
@app.get("/admin/export")
async def export_ns(ns: str = "global", _auth: None = Depends(api_key_dep)):
    store = get_store(ns)
    data = [{"text": t} for t in store.texts]
    buf = io.BytesIO(json.dumps(data, ensure_ascii=False, indent=2).encode())
    headers = {"Content-Disposition": f"attachment; filename={ns}.json"}
    return StreamingResponse(buf, media_type="application/json", headers=headers)


@app.post("/admin/import")
async def import_ns(p: ImportPayload, _auth: None = Depends(api_key_dep)):
    store = get_store(p.ns)
    added = 0
    for item in p.items:
        text = item.get("text")
        if not text:
            continue
        store.add(text)
        added += 1
    async with async_session() as ses:
        async with ses.begin():
            for text in store.texts[-added:]:
                emb_bytes = Chunk.emb_to_bytes(get_encoder().encode(text, normalize_embeddings=True))
                ses.add(Chunk(ns=p.ns, text=text, embedding=emb_bytes))
    return {"imported": added}