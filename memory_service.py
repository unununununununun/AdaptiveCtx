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
_encoder: SentenceTransformer | None = None


def get_encoder() -> SentenceTransformer:
    """Load sentence-transformer lazily and cache it."""
    global _encoder
    with model_lock:
        if _encoder is None:
            _encoder = SentenceTransformer(MODEL_NAME)
    return _encoder

# -----------------------------
# In-memory vector store per namespace
# -----------------------------
class NamespaceStore:
    def __init__(self):
        self.index: faiss.IndexFlatIP | None = None
        self.texts: List[str] = []
        self.meta: List[Dict] = []
        self.lock = threading.Lock()

    def _ensure_index(self, dim: int):
        if self.index is None:
            self.index = faiss.IndexFlatIP(dim)

    def add(self, text: str, meta: Dict | None = None):
        emb = get_encoder().encode([text], normalize_embeddings=True)
        self._ensure_index(emb.shape[1])
        with self.lock:
            self.index.add(emb)
            self.texts.append(text)
            self.meta.append(meta or {})

    def search(self, query: str, k: int = 4):
        if self.index is None:
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

    # ---------------------------------------------------------
    # Autosave: optionally remember every incoming query text
    # ---------------------------------------------------------
    # Enabled by env var `AUTOSAVE_QUERY` (default "1").
    # The query itself is stored so that future searches can
    # recall frequent/important questions even if the agent
    # forgets the wording.
    import os, hashlib
    if os.getenv("AUTOSAVE_QUERY", "1") not in {"0", "false", "False"}:
        # Avoid storing duplicates – use SHA1 of text as a quick dedup key
        q_hash = hashlib.sha1(req.query.encode("utf-8")).hexdigest()
        meta = {"source": "auto_query", "hash": q_hash}
        if q_hash not in (m.get("hash") for m in store.meta):
            store.add(req.query, meta)

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

# -------------------------------------------------------------
# Maintenance helpers
# -------------------------------------------------------------

@app.post("/admin/defrag")
def defrag(ns: str = "global"):
    """Remove duplicate texts inside a namespace (naïve strategy)."""
    store = get_store(ns)
    seen = {}
    new_texts: list[str] = []
    new_meta: list[dict] = []
    import numpy as np

    # Track indices to keep (unique hashes) ---------------------
    keep_idx: list[int] = []
    for i, (txt, meta) in enumerate(zip(store.texts, store.meta)):
        h = meta.get("hash") or hash(txt)
        if h in seen:
            continue  # duplicate
        seen[h] = True
        keep_idx.append(i)

    # If nothing to defrag – early exit ------------------------
    if len(keep_idx) == len(store.texts):
        return {"defrag": "noop", "size": len(store.texts)}

    # Rebuild embeddings matrix --------------------------------
    emb_dim = store.index.d  # type: ignore[attr-defined]
    new_vectors = np.zeros((len(keep_idx), emb_dim), dtype="float32")
    for new_i, old_i in enumerate(keep_idx):
        new_texts.append(store.texts[old_i])
        new_meta.append(store.meta[old_i])
        new_vectors[new_i] = store.index.reconstruct(old_i)  # type: ignore[attr-defined]

    # Replace store data atomically -----------------------------
    store.texts = new_texts
    store.meta = new_meta
    store.index.reset()
    store.index.add(new_vectors)  # type: ignore[arg-type]

    return {"defrag": "done", "size": len(store.texts)}

@app.get("/health")
async def health():
    return {"status": "ok"}
