@echo off
setlocal enabledelayedexpansion
title Stopping VeriGuard AI...

echo [*] Stopping VeriGuard AI background services...

:: Terminate port 8000 (Backend / Standalone)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr /r ":8000 " 2^>nul') do (
    if "%%a" NEQ "0" (
        echo [*] Stopping backend process on PID %%a...
        taskkill /F /PID %%a >nul 2>&1
    )
)

:: Terminate port 5173 (Vite Dev Server)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr /r ":5173 " 2^>nul') do (
    if "%%a" NEQ "0" (
        echo [*] Stopping frontend process on PID %%a...
        taskkill /F /PID %%a >nul 2>&1
    )
)

echo [OK] VeriGuard AI services stopped.
