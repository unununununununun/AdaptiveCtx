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
- **Goal**  give power-users a safe environment to run custom optimisation / maintenance code without touching the core.
- **Plugin structure**
  ```text
  plugins/
    ttl_prune.py          # example plugin
    my_company_algo.py    # user script
  ```
  Each file exposes:
  ```python
  PLUGIN_CONFIG = {
      "name": "TTL prune",
      "description": "Drop slots older than N days",
      "params": {"ttl_days": {"type": "int", "default": 90}}
  }

  def optimise(vectors: np.ndarray, meta: list[dict], **params) -> tuple[np.ndarray, list[dict]]:
      """Return new vectors + meta; MUST keep the same dimensionality."""
  ```
- **Dashboard workflow**
  1. Select namespace + plugin.
  2. Auto-generated form for parameters.
  3. *Preview* → AdaMem clones the namespace, runs plugin in a sandboxed subprocess (CPU/RAM limits) and collects metrics:
     * vector count change
     * disk size change
     * `Recall@3` on a golden set
     * p95 latency
  4. Diff & charts rendered in the UI; if `Recall drop > threshold` button *Apply* is disabled.
  5. On *Apply* new index atomically swaps in; old copy kept for rollback (N versions).
- **Security**  plugin runs in a separate process (or side-car Docker) with no network and limited FS access.
- **CLI helpers**
  ```bash
  adapmem plugins list
  adapmem plugins run ttl_prune --ns qa --ttl_days 60 --preview
  adapmem plugins apply  <job-id>
  adapmem plugins rollback <ns> --to 2024-08-07
  ```

### Phase 4 — Alternative indexes (R&D)
* Fibonacci-spiral + graph prototype
* Benchmark vs HNSW, FAISS-PQ on ≥1 M vectors

### Phase 5 — Memory Marketplace (R&D / Monetisation)
- **Idea**  users package their namespaces (or share read-only SaaS) and publish them.
- **Package format**
  ```text
  pack.zip
   ├─ manifest.yaml      # name, licence, language, embed-model-version
   ├─ slots.jsonl        # raw text + metadata
   ├─ vectors.faiss      # or chroma/
   └─ lora_adapter.bin   # optional mini-LM adapter
  ```
- **CLI**
  ```bash
  # export namespace "ui" to zip
  adapmem export ui ui_doc_pack.zip  --with-lora
  # import
  adapmem import ui_doc_pack.zip --ns customer-docs
  ```
- **Marketplace workflow (MVP)**
  1. Static Next.js front-end lists packs (title, size, price, rating).
  2. Stripe (or Gumroad) webhook issues one-time download link.
  3. CLI `adapmem marketplace install <pack_id>` fetches & imports.
- **Quality gates**
  * Automatic quick-bench upon upload (must hit ≥80 % Recall on test set).
  * Virus / PII scan.
- **Licence options**
  * Free (CC-BY / CC0)
  * Paid (commercial EULA)
  * Source-available with AGPL fallback after N years.

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
