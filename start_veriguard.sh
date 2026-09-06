#!/usr/bin/env bash
# =====================================================================
#             VERIGUARD AI - 1-CLICK LAUNCHER (macOS / Linux)
# =====================================================================

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

if [ -f "backend/venv/bin/python" ]; then
    PY_BIN="backend/venv/bin/python"
else
    PY_BIN="python3"
fi

"$PY_BIN" run_app.py
