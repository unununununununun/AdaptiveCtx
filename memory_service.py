from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
import threading

app = FastAPI(title="AdaptiveCtx API – MVP v0.1")

# -----------------------------
# Embedding model (loaded once)
# -----------------------------
MODEL_NAME = "sentence-transformers/paraphrase-MiniLM-L6-v2"
model_lock = threading.Lock()
encoder: SentenceTransformer | None = None

def get_encoder() -> SentenceTransformer:
    global encoder
    with model_lock:
        if encoder is None:
            encoder = SentenceTransformer(MODEL_NAME)
    return encoder

EMB_DIM = get_encoder().get_sentence_embedding_dimension()

# -----------------------------
# In-memory vector store per namespace
# -----------------------------
class NamespaceStore:
    def __init__(self):
        self.index = faiss.IndexFlatIP(EMB_DIM)
        self.texts: List[str] = []
        self.meta: List[Dict] = []
        self.lock = threading.Lock()

    def add(self, text: str, meta: Dict | None = None):
        emb = get_encoder().encode([text], normalize_embeddings=True)
        with self.lock:
            self.index.add(emb)
            self.texts.append(text)
            self.meta.append(meta or {})

    def search(self, query: str, k: int = 4):
        if len(self.texts) == 0:
            return []
        emb = get_encoder().encode([query], normalize_embeddings=True)
        with self.lock:
            D, I = self.index.search(emb, min(k, len(self.texts)))
            return [
                {"text": self.texts[idx], **self.meta[idx]} for idx in I[0]
            ]

stores: Dict[str, NamespaceStore] = {}

def get_store(ns: str) -> NamespaceStore:
    if ns not in stores:
        stores[ns] = NamespaceStore()
    return stores[ns]

# -----------------------------
# API Schemas
# -----------------------------
class QueryRequest(BaseModel):
    query: str = Field(..., description="Search string")
    top_k: int = Field(4, description="How many chunks to return", ge=1, le=20)
    ns: str = Field("global", description="Namespace")

class UpdateRequest(BaseModel):
    q: str
    a: str
    ns: str = Field("global", description="Namespace")

# -----------------------------
# Endpoints
# -----------------------------
@app.post("/query")
def query(req: QueryRequest):
    store = get_store(req.ns)
    slots = store.search(req.query, req.top_k)
    return {"slots": slots}

@app.post("/update")
def update(req: UpdateRequest):
    store = get_store(req.ns)
    combined = f"Q: {req.q}\nA: {req.a}"
    meta = {"source": "update"}
    store.add(combined, meta)
    return {"ok": True, "ns": req.ns, "size": len(store.texts)}

@app.get("/admin/namespaces")
def list_namespaces():
    return {"namespaces": list(stores.keys())}

@app.get("/health")
async def health():
    return {"status": "ok"}
