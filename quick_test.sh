#!/usr/bin/env bash
# One-liner local test runner — clones repo → ./quick_test.sh → results.
set -euo pipefail

if command -v python3 &>/dev/null; then PY=python3; else PY=python; fi
VENV=".venv"

# fresh flag deletes venv for clean reinstall
if [[ "${1:-}" == "--fresh" ]]; then
  echo "[quick_test] Removing existing $VENV for fresh install"
  rm -rf "$VENV"
fi

# create venv if missing
if [ ! -d "$VENV" ]; then
  echo "[quick_test] Creating virtual env $VENV"
  $PY -m venv "$VENV"
fi

# Activate venv
source "$VENV/bin/activate"

# check numpy version
NEED_NUMPY="1.26.4"
INSTALLED_NUMPY=$(python - <<PY
try:
    import importlib, pkg_resources, numpy, sys
    print(numpy.__version__)
except ModuleNotFoundError:
    sys.exit(1)
PY
)

if [ "$INSTALLED_NUMPY" != "$NEED_NUMPY" ]; then
  echo "[quick_test] Installing dependencies (numpy $NEED_NUMPY and others)"
  pip install --quiet --upgrade pip
  pip install --quiet -r requirements.txt
  pip install --quiet numpy=="$NEED_NUMPY"
else
  echo "[quick_test] Dependencies already satisfied (numpy $INSTALLED_NUMPY)"
fi

export ADCTX_API_KEYS=testkey
export PYTHONPATH="$(pwd)":${PYTHONPATH:-}

echo "[quick_test] Running pytest…"
pytest -v

echo "✓ All tests passed"