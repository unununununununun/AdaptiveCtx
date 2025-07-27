# Adaptive Memory Engine (AdaMem)

**Адаптивная внешняя память** для LLM-агентов.  Позволяет хранить
долговременные факты вне окна модели и автоматически подмешивать к запросу
только релевантные фрагменты.

* mini-LM-энкодер + FAISS/Chroma векторное хранилище;
* online-дообучение энкодера (LoRA) после каждого обновления;
* REST API (`/query`, `/update`, `/admin/*`);
* Docker-образ + Streamlit-дашборд;
* поддержка нескольких namespace-ов для разных агентов.

---

## 1. Зачем это нужно?

LLM-ассистенты быстро «забывают» информацию: окно контекста
(32–128 k токенов) заполняется, и старые сообщения вытесняются. AdaMem
решает проблему:

1. Хранит сколь угодно большой объём фактов на диске/SSD.
2. По запросу возвращает **k** самых близких слотов (Retrieval-Augmented Generation).
3. Благодаря online-дообучению энкодер мгновенно «учит» новые понятия.

Подходит для on-prem инсталяций, edge-устройств, CI-агентов без GPU.

## 2. Базовые сценарии

| Сценарий                | Выгода                                   |
|-------------------------|------------------------------------------|
| Chat-бот поддержки      | моментально запоминает свежие тикеты     |
| Код-ассистент           | «помнит» старые PR-решения               |
| Многоагентная система   | общий/раздельный namespace для агентов   |
| Offline-режим (air-gap) | работает на CPU, без внешних API         |

## 3. Архитектура (MVP)
```
User ─┐                                    
      │ 1. /query              ┌──────────────┐
Agent ─┼──────────────────────►│ AdaMem API   │
      │                       │  FastAPI     │
      │ 2. slots (k=4)        │              │
      │◄──────────────────────┤              │
      │                       └─────▲────────┘
      │                             │
      │ 3. /update (Q,A)            │  FAISS  +  mini-LM (LoRA)
      └─────────────────────────────┘
```

## 4. Быстрый старт (WIP)
```bash
# 1. Клонируем
$ git clone https://github.com/yourname/adaptive-memory.git
$ cd adaptive-memory

# 2. Запуск через Docker Compose
$ docker compose up -d           # memory-api + dashboard

# 3. Проверка API
$ curl -X POST localhost:9000/query \
       -H 'Content-Type: application/json' \
       -d '{"query":"health", "top_k":3}'
```

## 5. API (черновик)
| Метод         | Описание                         |
|---------------|----------------------------------|
| `POST /query` | `{query, top_k, ns}` → slots     |
| `POST /update`| `{q, a, ns}`  → ok              |
| `GET  /admin/namespaces`| Список space-ов       |
| `POST /admin/reembed`   | Пере-векторизация      |

## 6. Дорожная карта

### Phase 0 — MVP (v0.1)
* `/query`, `/update`, Chroma/FAISS, bge-base-ru.
* Docker-образ, пример двух агентов.

### Phase 1 — Namespace & Dashboard (v0.2)
* Множественные коллекции.
* Streamlit UI: поиск, статистика.

### Phase 2 — Maintenance (v0.3)
* Дефрагментация (TTL, дубликаты).
* Re-embedding на новой модели.

### Phase 3 — Plugin Sandbox (v0.4)
* Песочница оптимизаций: пользовательские скрипты.
* UI-редактор, preview, метрики, rollback.

### Phase 4 — Альтернативные индексы (R&D)
* Спираль Фибоначчи + граф.
* Сравнение с HNSW, FAISS-PQ.

### Phase 5 — Memory Marketplace (R&D / Monetization)
* Экспорт / импорт namespace-пакетов (zip + manifest).
* CLI `adapmem export / import`.
* Прототип каталога пакетов (static Next.js + bucket).
* Поддержка платёжного webhook и одноразовых ссылок.
* Механизмы рейтинга, проверки качества и лицензий.

## 7. Переменные окружения
| Вар                | Значение по умолчанию          |
|--------------------|--------------------------------|
| `MEMORY_ENDPOINT`  | `http://localhost:9000`        |
| `EMBED_MODEL`      | `intfloat/multilingual-e5-base`|
| `DEFAULT_NS`       | `global`                       |

## 8. Вклад и связь
PR-ы, идеи и баг-репорты приветствуются!

*Issues* → GitHub
*Chat*   → Cursor / Discord

## 9. Лицензия
MIT.

---
> Документ — черновик.  Проект в активной разработке.  Последнее обновление: {{DATE}}.
