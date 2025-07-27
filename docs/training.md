# Fine-tune pipeline (draft)

1. При каждом `POST /update` запись дублируется в таблицу `train_queue` (поле `used=0`).
2. Скрипт `python -m adaptive_ctx.trainer --ns global --batch 256` выбирает свежие записи,
   ставит `used=1` и (пока) выводит их. В будущем здесь будет LoRA-fine-tune.
3. После обучения чек-пойнт будет сохраняться в `checkpoints/<ts>/` и загружаться через
   эндпоинт `POST /admin/reload_encoder {"path": "checkpoints/<ts>"}`.