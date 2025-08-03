"""AdaptiveCtx API service with persistent DB + autosave and defrag."""

import os, json, io, hashlib, numpy as np
from typing import List, Dict
from fastapi import FastAPI, HTTPException, Depends, Header, Body
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from sentence_transformers import SentenceTransformer

from .db import Base, engine, async_session, Chunk
from sqlalchemy import select

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

# -----------------------------
# Schemas
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
app = FastAPI(title="AdaptiveCtx API – Persistent")
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
            store.meta.append(json.loads(row.meta or "{}"))

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/update")
async def update(p: UpdatePayload, _auth: None = Depends(api_key_dep)):
    text = f"Q: {p.q}\nA: {p.a}"
    store = get_store(p.ns)
    meta = {"source": "update"}
    store.add(text, meta)

    async with async_session() as ses:
        async with ses.begin():
            emb_bytes = Chunk.emb_to_bytes(store.embeddings[-1])
            ses.add(Chunk(ns=p.ns, text=text, embedding=emb_bytes, meta=json.dumps(meta)))
    return {"ok": True}

@app.post("/query")
async def query(p: QueryPayload, _auth: None = Depends(api_key_dep)):
    store = get_store(p.ns)
    slots = store.search(p.query, k=p.top_k)

    # autosave query itself (optional)
    if os.getenv("AUTOSAVE_QUERY", "1") not in {"0", "false", "False"}:
        q_hash = hashlib.sha1(p.query.encode("utf-8")).hexdigest()
        if q_hash not in (m.get("hash") for m in store.meta):
            meta = {"source": "auto_query", "hash": q_hash}
            store.add(p.query, meta)
            async with async_session() as ses:
                async with ses.begin():
                    ses.add(
                        Chunk(ns=p.ns, text=p.query, embedding=Chunk.emb_to_bytes(store.embeddings[-1]), meta=json.dumps(meta))
                    )
    return {"slots": slots}

# ----------------- admin -----------------
@app.post("/admin/defrag")
async def defrag(ns: str = "global", _auth: None = Depends(api_key_dep)):
    store = get_store(ns)
    seen = {}
    keep_idx: List[int] = []
    for i, (txt, meta) in enumerate(zip(store.texts, store.meta)):
        h = meta.get("hash") or hash(txt)
        if h in seen:
            continue
        seen[h] = True
        keep_idx.append(i)

    if len(keep_idx) == len(store.texts):
        return {"defrag": "noop", "size": len(store.texts)}

    # rebuild store
    new_texts, new_meta, new_emb = [], [], []
    for idx in keep_idx:
        new_texts.append(store.texts[idx])
        new_meta.append(store.meta[idx])
        new_emb.append(store.embeddings[idx])
    store.texts, store.meta, store.embeddings = new_texts, new_meta, new_emb

    # rewrite DB
    async with async_session() as ses:
        async with ses.begin():
            await ses.execute(Chunk.__table__.delete().where(Chunk.ns == ns))
            for t, m, e in zip(store.texts, store.meta, store.embeddings):
                ses.add(Chunk(ns=ns, text=t, embedding=Chunk.emb_to_bytes(e), meta=json.dumps(m)))
    return {"defrag": "done", "size": len(store.texts)}