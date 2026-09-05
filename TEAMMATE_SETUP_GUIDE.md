# 🚀 VeriGuard AI — 1-Click Application & Teammate Setup Guide

This guide explains how to use **VeriGuard AI** as a **True 1-Click Desktop Application** on your own laptop, how to share it with your teammates, and how they can run it on their laptops in under 3 minutes with zero hassle.

---

## ⚡ 1. How to Use as a 1-Click App on Your Laptop

You now have **3 ways** to launch the entire platform with a single click:

### Option A: From Your Windows Desktop (Recommended)
1. Double-click the **`VeriGuard AI`** shortcut right on your Windows Desktop.
2. The platform automatically:
   - Initializes the FastAPI backend and AI/forensic engines.
   - Launches the cybernetic frontend HUD.
   - Automatically opens your default web browser to **`http://localhost:8000`** (or **`http://localhost:5173`**).
   - Shows an interactive control console in the terminal.

*(If you ever move the project folder, just double-click `create_desktop_shortcut.bat` once to recreate the desktop icon).*

### Option B: From File Explorer
- Navigate to the project root folder `veriguard-ai/` and double-click:
  **`VeriGuard-AI.bat`** (or **`start_veriguard.bat`**).

### Option C: Clean 1-Click Shutdown
- To close all background servers cleanly, simply double-click:
  **`stop_veriguard.bat`** (or press **`Q`** in the launcher terminal).

---

## 👥 2. How to Share VeriGuard AI with Your Group Mates

You can share the project via **Pen Drive / USB Drive**, **Google Drive / Zip File**, or **GitHub**.

### 📦 Creating a Lightweight Zip to Share
To keep the zip file ultra-small (**~15 MB** instead of 1.5 GB), delete or exclude these two temporary cache folders before zipping:
- `backend\venv\` *(Your teammates will automatically generate their own local virtualenv)*
- `frontend\node_modules\` *(Only needed if they want to edit React code; the compiled app in `frontend\dist\` is already bundled)*

Keep everything else! Specifically ensure:
- `backend\`
- `frontend\dist\` *(Pre-compiled production bundle)*
- `VeriGuard-AI.bat`
- `setup_environment.bat`
- `stop_veriguard.bat`
- `create_desktop_shortcut.bat`

---

## 💻 3. Setting Up on a Teammate's Laptop (3-Minute Setup)

When a teammate copies or clones the project onto their laptop for the first time, have them follow these **3 simple steps**:

### Step 1: Ensure Prerequisites are Installed (One-time)
1. **Python 3.10, 3.11, 3.12, or 3.13**:
   - Download from: [https://www.python.org/downloads/](https://www.python.org/downloads/)
   - > [!IMPORTANT]
     > During Python installation, **YOU MUST CHECK THE BOX**:
     > **☑ "Add python.exe to PATH"** (at the bottom of the first installer screen).
2. **Tesseract-OCR for Windows**:
   - Download the official 1-click Windows installer (approx 40MB):
     [https://github.com/UB-Mannheim/tesseract/wiki](https://github.com/UB-Mannheim/tesseract/wiki)
   - Run the installer and keep the default install path (`C:\Program Files\Tesseract-OCR`).
3. **Node.js (Optional)**:
   - *Not strictly required!* VeriGuard AI features a **High-Performance Standalone Mode** where Python alone serves both the React Web App and API on `http://localhost:8000`.
   - If they wish to do live frontend development with Hot Reloading, install Node.js LTS from [https://nodejs.org](https://nodejs.org).

---

### Step 2: Run the Automated Setup Script
In the extracted `veriguard-ai/` folder, double-click:
👉 **`setup_environment.bat`**

This automated script will:
- ✅ Check Python and system path configuration.
- ✅ Create an isolated Python virtual environment (`backend\venv`).
- ✅ Install all required libraries (`fastapi`, `uvicorn`, `pillow`, `pytesseract`, `pydantic`, etc.).
- ✅ Detect Tesseract OCR.
- ✅ Programmatically generate all 7 demo assets (`demo_aadhaar_clean.png`, etc.).
- ✅ Execute the automated self-test (18/18 test cases) to guarantee 100% functionality.

---

### Step 3: Launch the App & Create Desktop Icon
1. Double-click **`create_desktop_shortcut.bat`** to place the **"VeriGuard AI"** icon on their desktop.
2. Double-click **`VeriGuard-AI.bat`** (or the new Desktop icon) anytime to launch!
3. Their browser will automatically open to the dashboard.

---

## 📱 4. Accessing from Mobile Phones on the Same Wi-Fi

You can demonstrate VeriGuard AI on a smartphone (e.g. testing the camera selfie or mobile layout) during your hackathon pitch:

1. Connect both the laptop and the smartphone to the **same Wi-Fi network** or mobile hotspot.
2. On the laptop, find your local IP address:
   - Open Command Prompt and type `ipconfig`.
   - Look for **IPv4 Address** (e.g., `192.168.1.35`).
3. On your smartphone's browser (Chrome / Safari), open:
   `http://192.168.1.35:8000`
4. The full cybernetic VeriGuard AI web application will load instantly on the phone!

---

## 🎯 5. How to Rehearse Your Hackathon Demo

Once launched, use the **1-Click Demo Buttons** on the Upload Page:

| Demo Button | Scenario | What Happens | Expected Result |
| :--- | :--- | :--- | :--- |
| 🟢 **Scenario 1: Clean KYC** | Authentic Aadhaar + PAN + Matching Selfie (Rahul Sharma) | Verifies Verhoeff $D_5$ checksum, Section 139AA statutory linkage, and 82.9% face match. | **Risk Score: 0 (LOW RISK)**, Emerald checkmark, Tier 3 Fast-Track clearance. |
| 🔴 **Scenario 2: Counterfeit Alert** | Tampered Aadhaar Card | Catches altered 12th check digit via Dihedral $D_5$ algorithm. | **Risk Score: 35 (MEDIUM RISK)**, Amber warning, Why-Flagged explains math failure. |
| ⚠️ **Scenario 3: Synthetic Conflict** | Person A Aadhaar + Person B PAN + Imposter Face | Cross-reconciler flags conflicting names/DOBs, and biometrics flags imposter face. | **Risk Score: 100 (CRITICAL RISK)**, Crimson alert wave, Tier 1 Escalation. |

---

## 🛠️ 6. Troubleshooting FAQ

### Q1: When double-clicking `VeriGuard-AI.bat`, it closes immediately!
- **Reason**: Python is likely not installed or not added to your system PATH.
- **Fix**: Re-run the Python installer, select **Modify**, and ensure **"Add python.exe to PATH"** is checked. Then restart your terminal or laptop.

### Q2: Tesseract OCR warning is displayed
- **Reason**: Tesseract-OCR is not installed in `C:\Program Files\Tesseract-OCR`.
- **Fix**: Install Tesseract from [https://github.com/UB-Mannheim/tesseract/wiki](https://github.com/UB-Mannheim/tesseract/wiki). The application will automatically detect it once installed.

### Q3: Port 8000 is already in use
- **Fix**: `VeriGuard-AI.bat` automatically terminates zombie processes on port 8000 on startup. You can also manually double-click `stop_veriguard.bat` to clear all ports.

### Q4: Windows Defender / SmartScreen warning: "Windows protected your PC"
- **Reason**: Standard Windows prompt when running newly downloaded `.bat` scripts on a PC for the first time.
- **Fix**: Click **"More info"** and then click **"Run anyway"**.
