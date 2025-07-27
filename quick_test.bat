@echo off
REM One-liner test runner: git clone → quick_test.bat → results

if "%1"=="--fresh" (
    echo [quick_test] Removing existing .venv
    rmdir /s /q .venv 2>nul
)

if not exist .venv (
    echo [quick_test] Creating virtual env .venv
    python -m venv .venv
)
call .\.venv\Scripts\activate.bat >nul

REM ---------- dependency check -------------------------------------------------
set NEED_NUMPY=1.26.4
for /f "delims=" %%V in ('python -c "import sys, import importlib;\ntry:\n import numpy as n; print(n.__version__)\nexcept ModuleNotFoundError:\n sys.exit(1)"') do set CUR_NUMPY=%%V

if "%CUR_NUMPY%" NEQ "%NEED_NUMPY%" (
    echo [quick_test] Installing / updating dependencies …
    python -m pip install --quiet --upgrade pip
    python -m pip install --quiet -r requirements.txt
    python -m pip install --quiet numpy==%NEED_NUMPY%
) else (
    echo [quick_test] Dependencies already satisfied (numpy %CUR_NUMPY%)
)

REM ---------------------------------------------------------------------------
set "ADCTX_API_KEYS=testkey"
set "PYTHONPATH=%CD%;%PYTHONPATH%"

echo [quick_test] Running pytest …
pytest -v
if %errorlevel% neq 0 (
    echo Tests FAILED
    exit /b 1
) else (
    echo ✓ All tests passed
)