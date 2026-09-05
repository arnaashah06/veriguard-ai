# backend/tesseract_config.py
"""
VeriGuard AI - Tesseract OCR Discovery & Configuration Module
Automatically detects Tesseract-OCR across standard Windows installations, PATH, and AppData.
"""

import os
import sys
import shutil

# Standard Windows installation candidates
CANDIDATE_PATHS = [
    os.environ.get("TESSERACT_PATH", ""),
    os.environ.get("TESSERACT_CMD", ""),
    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "Tesseract-OCR", "tesseract.exe"),
    os.path.join(os.environ.get("USERPROFILE", ""), "AppData", "Local", "Programs", "Tesseract-OCR", "tesseract.exe"),
]

# Check system PATH
which_tesseract = shutil.which("tesseract")
if which_tesseract:
    CANDIDATE_PATHS.insert(0, which_tesseract)

TESSERACT_PATH = None
for candidate in CANDIDATE_PATHS:
    if candidate and os.path.isfile(candidate):
        TESSERACT_PATH = os.path.abspath(candidate)
        break

if not TESSERACT_PATH:
    # Default fallback path
    TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

TESSERACT_DATA_DIR = os.path.join(os.path.dirname(TESSERACT_PATH), "tessdata")

def get_tesseract_info():
    found = os.path.isfile(TESSERACT_PATH)
    return {
        "found": found,
        "executable": TESSERACT_PATH,
        "tessdata": TESSERACT_DATA_DIR if os.path.isdir(TESSERACT_DATA_DIR) else None
    }

if os.path.isfile(TESSERACT_PATH):
    print(f"✅ Tesseract found at: {TESSERACT_PATH}")
else:
    print(f"⚠️ Notice: Tesseract executable not detected at {TESSERACT_PATH}")
    print("   Download the 1-click Windows installer from: https://github.com/UB-Mannheim/tesseract/wiki")