@echo off
setlocal
title VeriGuard AI
set ROOT_DIR=%~dp0
cd /d "%ROOT_DIR%"

if exist "backend\venv\Scripts\python.exe" (
    backend\venv\Scripts\python.exe run_app.py
) else (
    python run_app.py
)

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [!] VeriGuard AI encountered an error on exit.
    pause
)
