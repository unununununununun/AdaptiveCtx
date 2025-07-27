#!/usr/bin/env bash
# One-liner local test runner — clones repo → ./quick_test.sh → results.
set -euo pipefail

if command -v python3 &>/dev/null; then PY=python3; else PY=python; fi
VENV=".venv"

if [ ! -d "$VENV" ]; then
  echo "[quick_test] Creating virtual env $VENV"
  $PY -m venv "$VENV"
fi

# Activate venv
# shellcheck disable=SC1090
source "$VENV/bin/activate"

pip install --quiet --upgrade pip
pip install --quiet --upgrade --force-reinstall -r requirements.txt
# ensure correct numpy version (torch needs <2)
pip uninstall -y numpy 2>/dev/null || true
pip install --quiet numpy==1.26.4

export ADCTX_API_KEYS=testkey
export PYTHONPATH="$(pwd)":${PYTHONPATH:-}

echo "[quick_test] Running pytest…"
pytest -v

echo "✓ All tests passed"