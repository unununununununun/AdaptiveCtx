# Adaptive Memory Engine (AdaMem)

**Adaptive external memory** for LLM agents.  Keeps long-term knowledge outside the model window and injects only the most relevant fragments into every prompt.

* mini-LM encoder + FAISS/Chroma vector store
* Online LoRA fine-tuning after every update (optional)
* REST API (`/query`, `/update`, `/admin/*`)
* Single Docker image + Streamlit dashboard
* Multi-namespace support for multiple agents

---

## 1 · Why?
Modern LLMs forget quickly: the context window (32 k – 128 k tokens) fills up and old messages get dropped. AdaMem fixes this:

1. Stores virtually unlimited knowledge on disk/SSD.
2. Returns **k** nearest fragments on demand (Retrieval-Augmented Generation).
3. Instantly “learns” new facts via lightweight online LoRA tuning.

CPU-friendly, offline-ready — perfect for on-prem and edge installs.

## 2 · Typical use-cases
| Scenario              | Benefit                                  |
|-----------------------|-------------------------------------------|
| Support chatbot       | remembers fresh tickets immediately       |
| Code assistant        | recalls old PR decisions                  |
| Multi-agent systems   | shared / isolated namespaces              |
| Air-gapped environment| works on CPU, no external APIs            |

## 3 · MVP architecture
```text
User ─┐
      │ 1. /query              ┌───────────────┐
Agent ─┼──────────────────────►│ AdaMem API    │
      │                       │   FastAPI     │
      │ 2. slots (k=4)        │               │
      │◄──────────────────────┤               │
      │                       └──────▲────────┘
      │                              │
      │ 3. /update (Q,A)             │  FAISS  +  mini-LM (LoRA)
      └──────────────────────────────┘
```

## 4 · Quick start (WIP)
```bash
# 1. Clone
$ git clone https://github.com/yourname/AdaptiveCtx.git
$ cd AdaptiveCtx

# 2. Docker Compose (API + dashboard)
$ docker compose up -d

# 3. Smoke test
$ curl -X POST localhost:9000/query \
       -H 'Content-Type: application/json' \
       -d '{"query":"health", "top_k":3}'
```

## 5 · API draft
| Method          | Description                                |
|-----------------|---------------------------------------------|
| `POST /query`   | `{query, top_k, ns}` → list of slots        |
| `POST /update`  | `{q, a, ns}` → `{"ok":true}`              |
| `GET  /admin/namespaces` | list namespaces                    |
| `POST /admin/reembed`    | re-embed with a new model          |

## 6 · Roadmap

### Phase 0 — MVP (v0.1)
* `/query`, `/update`, Chroma/FAISS, bge-base-ru
* Docker image, two demo agents

### Phase 1 — Namespaces & Dashboard (v0.2)
* Multiple collections
* Streamlit UI: search, stats

### Phase 2 — Maintenance (v0.3)
* Defrag (TTL, duplicates)
* Re-embedding with a new encoder

### Phase 3 — Plugin Sandbox (v0.4)
* User optimisation plugins (Python)
* Built-in editor, preview, metrics, rollback

### Phase 4 — Alternative indexes (R&D)
* Fibonacci-spiral + graph
* Benchmark vs HNSW, FAISS-PQ

### Phase 5 — Memory Marketplace (R&D / Monetisation)
* Export / import packages (zip + manifest)
* CLI `adapmem export / import`
* Static catalogue (Next.js + bucket)
* Payment webhook & one-time download links
* Ratings, licence & quality checks

## 7 · Environment variables
| Var                | Default value                    |
|--------------------|----------------------------------|
| `MEMORY_ENDPOINT`  | `http://localhost:9000`          |
| `EMBED_MODEL`      | `intfloat/multilingual-e5-base`  |
| `DEFAULT_NS`       | `global`                         |

## 8 · Contributing & Support
PRs, issues and ideas are welcome!

*Issues* → GitHub

*Chat*   → Cursor / Discord

## 9 · Licence
MIT.

---
*This document is a work-in-progress (last update {{DATE}}).*
