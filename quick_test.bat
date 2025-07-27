@echo off
REM One-liner test runner: git clone → quick_test.bat → results

if not exist .venv (
    echo [quick_test] Creating virtual env .venv
    python -m venv .venv
)
call .\.venv\Scripts\activate.bat
python -m pip install --quiet --upgrade pip
python -m pip install --quiet --upgrade --force-reinstall -r requirements.txt
REM ensure numpy 1.26.4
python -m pip uninstall -y numpy >nul 2>&1
python -m pip install --quiet numpy==1.26.4

set "ADCTX_API_KEYS=testkey"
set "PYTHONPATH=%CD%;%PYTHONPATH%"

echo [quick_test] Running pytest…
pytest -v
if %errorlevel% neq 0 (
    echo Tests FAILED
    exit /b 1
) else (
    echo ✓ All tests passed
)