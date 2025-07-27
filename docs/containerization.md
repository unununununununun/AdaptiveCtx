# Контейнеризация

## Файлы
* **Dockerfile** — образ сервис-API (Python 3.11-slim).
* **docker-compose.yml** — локальный стек `api` + `postgres:16`.

| Сервис | Порт | ENV (по умолчанию) |
|--------|------|--------------------|
| db     | 5432 | POSTGRES_* creds   |
| api    | 8000 | DATABASE_URL, ADCTX_API_KEYS |

## Быстрый старт
```bash
# собрать и запустить
docker compose up --build
# UI → http://localhost:8000
```

Если `DATABASE_URL` не задан — сервис переключится на локальный SQLite (`data.db`).