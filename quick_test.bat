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
call .\.venv\Scripts\activate.bat

REM check numpy version
for /f "delims=" %%v in ('python - <<PY 2^>nul ^& exit /b
import importlib, sys, json, pkg_resources
try:
    import numpy as np; print(np.__version__)
except ModuleNotFoundError:
    sys.exit(1)
PY') do set NUMPY_VER=%%v

if "%NUMPY_VER%" NEQ "1.26.4" (
    echo [quick_test] Installing/repairing dependencies...
    python -m pip install --quiet --upgrade pip
    python -m pip install --quiet -r requirements.txt
    python -m pip install --quiet numpy==1.26.4
) else (
    echo [quick_test] Dependencies already satisfied (numpy %NUMPY_VER%)
)

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