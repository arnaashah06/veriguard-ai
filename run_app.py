# run_app.py
"""
VeriGuard AI - Master Desktop Application Launcher
Manages Backend, Frontend, Port Checks, Browser Auto-Launch, and Graceful Shutdown.
"""

import os
import sys
import time
import socket
import subprocess
import urllib.request
import webbrowser

# Ensure UTF-8 stdout encoding on Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(ROOT_DIR, "backend")
FRONTEND_DIR = os.path.join(ROOT_DIR, "frontend")
VENV_PYTHON = os.path.join(BACKEND_DIR, "venv", "Scripts", "python.exe")

# Fallback for systems where python is global
if not os.path.isfile(VENV_PYTHON):
    VENV_PYTHON = sys.executable

def is_port_in_use(port: int) -> bool:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.5)
            return s.connect_ex(("127.0.0.1", port)) == 0
    except Exception:
        return False

def wait_for_url(url: str, timeout: int = 15) -> bool:
    start = time.time()
    while time.time() - start < timeout:
        try:
            with urllib.request.urlopen(url, timeout=1) as resp:
                if resp.status == 200:
                    return True
        except Exception:
            time.sleep(0.4)
    return False

def main():
    # Set Windows console title
    if sys.platform == "win32":
        try:
            import ctypes
            ctypes.windll.kernel32.SetConsoleTitleW("VeriGuard AI - Desktop Controller")
        except Exception:
            pass

    print("=======================================================================")
    print("      __     __         _  ____                      _       _    ___ ")
    print("      \\ \\   / /__ _ __ (_)/ ___|_   _  __ _ _ __ __| |     / \\  |_ _|")
    print("       \\ \\ / / _ \\ '__| | |  _| | | |/ _` | '__/ _` |    / _ \\  | | ")
    print("        \\ V /  __/ |  | | |_| | |_| | (_| | | | (_| |   / ___ \\ | | ")
    print("         \\_/ \\___|_|  |_|\\____|\\__,_|\\__,_|_|  \\__,_|  /_/   \\_\\___|")
    print()
    print("           Real-Time Identity Fraud Detection & Cross-Document Engine")
    print("=======================================================================")
    print()

    procs = []

    try:
        # 1. Check or Launch Backend (FastAPI on Port 8000)
        if is_port_in_use(8000):
            print("  [OK] Backend server is already running on port 8000.")
        else:
            print("  [*] Launching VeriGuard AI Backend server on port 8000...")
            creationflags = subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0
            backend_proc = subprocess.Popen(
                [VENV_PYTHON, "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8000"],
                cwd=BACKEND_DIR,
                creationflags=creationflags
            )
            procs.append(backend_proc)

        # 2. Check or Launch Frontend (Vite on Port 5173)
        app_url = "http://localhost:8000"
        node_modules = os.path.join(FRONTEND_DIR, "node_modules")

        if os.path.isdir(node_modules):
            if is_port_in_use(5173):
                print("  [OK] Frontend server (Vite) is already active on port 5173.")
                app_url = "http://localhost:5173"
            else:
                print("  [*] Launching VeriGuard AI Frontend HUD (Vite)...")
                npx_cmd = "npx.cmd" if sys.platform == "win32" else "npx"
                try:
                    creationflags = subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0
                    frontend_proc = subprocess.Popen(
                        [npx_cmd, "vite", "--port", "5173"],
                        cwd=FRONTEND_DIR,
                        creationflags=creationflags
                    )
                    procs.append(frontend_proc)
                    app_url = "http://localhost:5173"
                except Exception as e:
                    print(f"  [!] Note: Vite dev server unavailable ({e}).")
                    print("  [*] Running in Standalone Mode on port 8000.")
                    app_url = "http://localhost:8000"
        else:
            print("  [*] Running in High-Performance Standalone Mode on port 8000.")
            app_url = "http://localhost:8000"

        # 3. Wait for Backend Health Check
        print("  [*] Synchronizing with verification engine...")
        ready = wait_for_url("http://127.0.0.1:8000/health", timeout=12)
        if ready:
            print("  [OK] Verification engine initialized successfully!")
        else:
            print("  [!] Backend taking a moment to initialize...")

        # 4. Automatically Launch Default Web Browser
        print(f"\n  [OK] VeriGuard AI is ACTIVE!")
        print(f"  [*] Opening your browser at: {app_url}")
        time.sleep(1)
        webbrowser.open(app_url)

        # 5. Interactive Status Dashboard
        print("\n" + "=" * 71)
        print("  [ONLINE] STATUS: VERIGUARD AI IS RUNNING")
        print(f"  [>] Web Dashboard:    {app_url}")
        print("  [>] Interactive Docs: http://localhost:8000/docs")
        print("  [>] Verification:     Aadhaar, PAN, Voter ID, Driving Licence, Face")
        print("  [>] Statutory Link:   Section 139AA Income-tax Compliance Active")
        print("=" * 71)
        print("\n  >> Press [Enter] or close this window anytime to STOP VeriGuard AI <<\n")

        # Keep alive until user hits Enter
        input()

    except KeyboardInterrupt:
        pass
    except Exception as err:
        print(f"\n[!] Unexpected error: {err}")
        input("Press Enter to close...")
    finally:
        print("\n[*] Stopping VeriGuard AI background services...")
        for p in procs:
            try:
                p.terminate()
                p.wait(timeout=2)
            except Exception:
                try:
                    p.kill()
                except Exception:
                    pass
        print("[OK] VeriGuard AI has exited cleanly. Have a great day!")
        time.sleep(1)

if __name__ == "__main__":
    main()
