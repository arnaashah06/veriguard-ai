# test_full_pipeline.py (Root Launcher)
"""
VeriGuard AI - Root Pipeline Test Launcher
Automatically redirects execution to backend/test_full_pipeline.py using the project's virtualenv.
"""

import os
import sys
import subprocess

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_SCRIPT = os.path.join(CURRENT_DIR, "backend", "test_full_pipeline.py")
VENV_PYTHON = os.path.join(CURRENT_DIR, "backend", "venv", "Scripts", "python.exe")

if not os.path.isfile(BACKEND_SCRIPT):
    print(f"[!] Error: Target test script not found at: {BACKEND_SCRIPT}")
    sys.exit(1)

# Select Python binary (prefer virtualenv python)
python_bin = VENV_PYTHON if os.path.isfile(VENV_PYTHON) else sys.executable

cmd = [python_bin, BACKEND_SCRIPT] + sys.argv[1:]
result = subprocess.run(cmd)
sys.exit(result.returncode)
