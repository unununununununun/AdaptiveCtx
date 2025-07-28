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

Запуск
------
1. Поднимите сервис памяти:
   ```bash
   docker compose up --build -d      # порт 8000
   # или
   export ADCTX_API_KEYS=secret123
   uvicorn adaptive_ctx.memory_service:app --port 8000
   ```
2. Укажите эту подпапку при создании нового агента в Cursor
   (Directory → `cursor_client_example`, Entry → `main.py`).
3. При желании задайте переменные окружения в разделе *Environment*:
   ```
   MEMORY_API      http://localhost:8000
   MEMORY_API_KEY  secret123
   ```
4. Запустите агента. В консоли увидите диалог; каждая пара Q/A
   автоматически сохраняется в AdaptiveCtx, а перед ответом выводится
   контекст, полученный из памяти.