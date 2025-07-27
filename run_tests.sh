#!/usr/bin/env bash
# Run full test-suite locally.
# Usage: ./run_tests.sh
set -euo pipefail
export ADCTX_API_KEYS=testkey
pytest -v

echo "✓ All tests passed"