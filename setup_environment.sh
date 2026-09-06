#!/usr/bin/env bash
# =====================================================================
#             VERIGUARD AI - ENVIRONMENT SETUP (macOS / Linux)
#      Automated Installer for Teammates and Collaborator MacBooks
# =====================================================================

set -e

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

echo "====================================================================="
echo "        VERIGUARD AI - ONE-TIME ENVIRONMENT SETUP (macOS)"
echo "====================================================================="
echo ""

# ---------------------------------------------------------------------
# STEP 1: Check Python 3
# ---------------------------------------------------------------------
echo "[*] Step 1/5: Checking Python 3..."
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "[!] ERROR: Python 3 was not found on your system!"
    echo "    Please install Python 3 (3.10 to 3.13) via Homebrew:"
    echo "    brew install python"
    echo "    or download from: https://www.python.org/downloads/"
    exit 1
fi

echo "[OK] Using Python: $($PYTHON_CMD --version)"

# ---------------------------------------------------------------------
# STEP 2: Check Tesseract OCR
# ---------------------------------------------------------------------
echo ""
echo "[*] Step 2/5: Checking Tesseract OCR..."
if command -v tesseract &> /dev/null || [ -f "/opt/homebrew/bin/tesseract" ] || [ -f "/usr/local/bin/tesseract" ]; then
    echo "[OK] Tesseract OCR is installed!"
else
    echo "[!] NOTICE: Tesseract OCR was not found."
    echo "    To install Tesseract OCR on macOS, run:"
    echo "    brew install tesseract"
    echo "    (The app will still run demo modes, but brew install tesseract is recommended for custom uploads)."
fi

# ---------------------------------------------------------------------
# STEP 3: Setup Python Virtual Environment
# ---------------------------------------------------------------------
echo ""
echo "[*] Step 3/5: Setting up Python Virtual Environment (backend/venv)..."
if [ ! -f "backend/venv/bin/python" ]; then
    echo "[*] Creating isolated virtual environment..."
    $PYTHON_CMD -m venv backend/venv
    echo "[OK] Virtual environment created."
else
    echo "[OK] Virtual environment backend/venv already exists."
fi

VENV_PY="backend/venv/bin/python"

echo "[*] Upgrading pip..."
"$VENV_PY" -m pip install --upgrade pip --quiet

echo "[*] Installing backend dependencies..."
if "$VENV_PY" -m pip install -r backend/requirements.txt --quiet 2>/dev/null; then
    echo "[OK] All dependencies from backend/requirements.txt installed successfully."
else
    echo "[!] Note: Some optional compiled packages (e.g. dlib) were skipped."
    echo "    Installing core forensic & verification packages..."
    "$VENV_PY" -m pip install fastapi uvicorn pillow pydantic python-multipart pytesseract python-dotenv opencv-python-headless numpy scipy --quiet
fi
echo "[OK] Backend dependencies ready."

# ---------------------------------------------------------------------
# STEP 4: Setup Frontend (Node.js / Vite)
# ---------------------------------------------------------------------
echo ""
echo "[*] Step 4/5: Checking Frontend Assets..."
if [ -f "frontend/dist/index.html" ]; then
    echo "[OK] Pre-compiled frontend bundle exists in frontend/dist!"
fi

if command -v node &> /dev/null; then
    echo "[OK] Node.js is installed ($(node --version))."
    if [ ! -d "frontend/node_modules" ]; then
        echo "[*] Installing frontend npm packages..."
        (cd frontend && npm install --silent)
    fi
    echo "[*] Building frontend distribution bundle..."
    (cd frontend && npm run build)
else
    echo "[!] Node.js not found. VeriGuard AI will serve the pre-compiled frontend bundle via Python on port 8000."
fi

# ---------------------------------------------------------------------
# STEP 5: Generate Demo Assets & Run Self-Test
# ---------------------------------------------------------------------
echo ""
echo "[*] Step 5/5: Generating demo assets and running verification self-test..."
"$VENV_PY" backend/generate_demo_assets.py
"$VENV_PY" backend/test_real_vs_fake.py

echo ""
echo "====================================================================="
echo "                    🎉 SETUP COMPLETE ON macOS! 🎉"
echo "====================================================================="
echo "You can now launch VeriGuard AI anytime by running:"
echo ""
echo "     ./start_veriguard.sh"
echo "  or: python3 run_app.py"
echo ""
echo "Your browser will automatically open to http://localhost:8000"
echo "====================================================================="
