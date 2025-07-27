# Тесты и CI

* **tests/test_api.py** — async-pytest, проверяет `/health`, цикл Update→Query.
* **GitHub Actions** workflow `.github/workflows/ci.yml` запускает тесты на Python 3.11 при каждом push/PR.

Локальный запуск:
```bash
pytest -q
```