# tesseract_config.py
"""
VeriGuard AI - Tesseract OCR Discovery
"""

import os
import shutil

CANDIDATE_PATHS = [
    os.environ.get("TESSERACT_PATH", ""),
    os.environ.get("TESSERACT_CMD", ""),
    "/opt/homebrew/bin/tesseract",       # Apple Silicon Mac (Homebrew)
    "/usr/local/bin/tesseract",          # Intel Mac (Homebrew)
    "/usr/bin/tesseract",                # Linux / Unix
    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "Tesseract-OCR", "tesseract.exe"),
]

which_tesseract = shutil.which("tesseract")
if which_tesseract:
    CANDIDATE_PATHS.insert(0, which_tesseract)

TESSERACT_PATH = None
for candidate in CANDIDATE_PATHS:
    if candidate and os.path.isfile(candidate):
        TESSERACT_PATH = os.path.abspath(candidate)
        break

if not TESSERACT_PATH:
    TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

TESSERACT_DATA_DIR = os.path.join(os.path.dirname(TESSERACT_PATH), "tessdata")
