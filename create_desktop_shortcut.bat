@echo off
setlocal
title Create VeriGuard AI Desktop Shortcut
echo =====================================================================
echo          CREATING VERIGUARD AI DESKTOP SHORTCUT
echo =====================================================================
echo.

set ROOT_DIR=%~dp0
set TARGET_BAT=%ROOT_DIR%VeriGuard-AI.bat

set VBS_TEMP=%TEMP%\CreateShortcut_%RANDOM%.vbs
echo Set oWS = WScript.CreateObject("WScript.Shell") > "%VBS_TEMP%"
echo sLinkFile = oWS.SpecialFolders("Desktop") ^& "\VeriGuard AI.lnk" >> "%VBS_TEMP%"
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> "%VBS_TEMP%"
echo oLink.TargetPath = "%TARGET_BAT%" >> "%VBS_TEMP%"
echo oLink.WorkingDirectory = "%ROOT_DIR%" >> "%VBS_TEMP%"
echo oLink.Description = "VeriGuard AI - Identity Fraud Detection Platform" >> "%VBS_TEMP%"
echo oLink.IconLocation = "shell32.dll, 220" >> "%VBS_TEMP%"
echo oLink.Save >> "%VBS_TEMP%"

cscript //nologo "%VBS_TEMP%"
del "%VBS_TEMP%" >nul 2>&1

if exist "%USERPROFILE%\Desktop\VeriGuard AI.lnk" (
    echo [OK] SUCCESS! Desktop shortcut created:
    echo      "%USERPROFILE%\Desktop\VeriGuard AI.lnk"
    echo.
    echo You can now minimize all windows and double-click "VeriGuard AI"
    echo directly from your Windows Desktop anytime!
) else (
    echo [!] Notice: Could not write directly to Desktop folder.
    echo     You can easily create it manually:
    echo     Right-click "VeriGuard-AI.bat" in this folder -^> Send to -^> Desktop.
)

echo.
echo =====================================================================
pause
