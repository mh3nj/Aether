@echo off
title Aether - Smart Assistant Launcher
color 0A

setlocal enabledelayedexpansion
set STARTDIR=%CD%


echo :)   :)   :)   :)   :)   :)   :)   :)   :)   :)
echo         Aether Setup & Launcher
echo :)   :)   :)   :)   :)   :)   :)   :)   :)   :)
echo.

REM Python check
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python 3.9+ required
    echo Download from https://python.org
    pause
    exit /b 1
)

REM Version check (3.9+)
for /f "tokens=2 delims= " %%v in ('python --version') do set PYVER=%%v
for /f "tokens=1,2 delims=." %%a in ("!PYVER!") do (
    set MAJOR=%%a
    set MINOR=%%b
)
if !MAJOR! LSS 3 (
    echo [ERROR] Python 3.9+ required

    pause
    exit /b 1
)
if !MAJOR! EQU 3 if !MINOR! LSS 9 (

    echo [ERROR] Python 3.9+ required
    pause
    exit /b 1
)

echo [OK] Python !PYVER! found

REM Git check (optional - can fallback to ZIP)
git --version >nul 2>&1
if errorlevel 1 (
    echo [WARN] Git not found - will use existing files
    set NOGIT=1
) else (
    echo [OK] Git found
)

REM Clone or update
if exist "aether" (
    cd aether
    if not defined NOGIT (
        echo [UPDATE] Pulling latest...
        git pull
    )
) else (
    if defined NOGIT (
        echo [ERROR] No Git and no existing folder
        echo Please download ZIP from GitHub
        pause
        exit /b 1
    )
    echo [CLONE] Downloading Aether...
    git clone https://github.com/mh3nj/aether.git
    cd aether
)

REM Virtual environment
if not exist ".venv" (
    echo [SETUP] Creating venv...
    python -m venv .venv
)

call .venv\Scripts\activate.bat

REM Install dependencies
if exist requirements.txt (
    echo [INSTALL] Installing packages...
    pip install --upgrade pip
    pip install -r requirements.txt
) else (
    echo [WARN] No requirements.txt found
)

REM Check for .env file
if not exist .env (
    echo [WARN] No .env file found
    echo Creating template...
    echo OPENAI_API_KEY=your_key_here > .env
    echo Please edit .env with your API keys
    notepad .env
    pause
)

REM Launch
echo.
echo [LAUNCH] Starting Aether...
python main.py  # or whatever your entry point is

cd /d "%STARTDIR%"
pause