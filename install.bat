@echo off
REM Church Community Tracker — Windows installer
REM Double-click this file to install.
cd /d "%~dp0"

echo.
echo  Church Community Tracker — Installer
echo  =====================================
echo.

REM Try python, then py launcher
where python >nul 2>&1
if %ERRORLEVEL% == 0 (
    set PYTHON=python
) else (
    where py >nul 2>&1
    if %ERRORLEVEL% == 0 (
        set PYTHON=py
    ) else (
        echo  ERROR: Python not found.
        echo  Please install Python 3.8+ from https://www.python.org/downloads/
        echo  Make sure to check "Add Python to PATH" during installation.
        pause
        exit /b 1
    )
)

echo  Using: %PYTHON%
echo.

%PYTHON% install.py
if %ERRORLEVEL% neq 0 (
    echo.
    echo  Installation failed. See messages above.
    pause
    exit /b 1
)

echo.
echo  Press any key to launch the app now...
pause >nul
%PYTHON% main.py
