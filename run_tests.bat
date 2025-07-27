@echo off
REM Run full test-suite locally (Windows).
REM Usage:  run_tests.bat

set "ADCTX_API_KEYS=testkey"
pytest -v
if %errorlevel% neq 0 (
    echo Tests FAILED
    exit /b 1
) else (
    echo ✓ All tests passed
)