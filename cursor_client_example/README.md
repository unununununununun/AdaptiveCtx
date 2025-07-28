# cursor_client_example

Минимальный шаблон папки-агента, который показывает, как пользоваться
AdaptiveCtx в Cursor без дополнительного кода.

Содержимое:
```
cursor_client_example/
 ├─ main.py              # точка входа агента
 └─ (корень репо)
     └─ cursor_client/   # клиент уже присутствует выше
```

Основные шаги
-------------
1. Поднимите сервис памяти (и опционально агент) одной командой:
   ```bash
   docker compose up --build
   ```
   После старта вы увидите приглашение `You:` прямо в терминале контейнера
   `agent`.

2. Хотите ответы от GPT, а не эхо? Перед запуском укажите переменную
   окружения `OPENAI_API_KEY` (перед `docker compose` или в `.env`).
   Без ключа скрипт автоматически переключится в «echo-mode».

3. Дашборд FastAPI доступен по адресу http://localhost:8000 — можно
   проверить, что новые Q/A сразу попадают в `/admin/export`.

-----

Запуск отдельно (без Docker)
---------------------------
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r ../../requirements.txt  # из корня репо
export ADCTX_API_KEYS=secret123
uvicorn adaptive_ctx.memory_service:app --port 8000 &

# отдельный терминал
export MEMORY_API=http://localhost:8000
python main.py
```
