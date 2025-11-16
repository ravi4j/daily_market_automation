@echo off
REM Daily Market Automation - Windows Setup Script
REM One-time setup for local Windows machine
REM Usage: scripts\setup_local.bat

setlocal EnableDelayedExpansion

echo ========================================
echo   Daily Market Automation - Windows Setup
echo ========================================
echo.

REM Get project directory
cd /d "%~dp0\.."
set PROJECT_DIR=%CD%

REM Step 1: Check Python
echo [1/7] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo [X] Python not found! Please install Python 3.12+ from https://www.python.org/downloads/
    echo     Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [OK] Python %PYTHON_VERSION% found

REM Check if Python 3.12+
python -c "import sys; exit(0 if sys.version_info >= (3, 12) else 1)" >nul 2>&1
if errorlevel 1 (
    echo [!] Warning: Python 3.12+ recommended for pandas-ta compatibility
    echo     Current version: %PYTHON_VERSION%
    echo     Continue anyway? Press Ctrl+C to cancel, or
    pause
)

REM Step 2: Create virtual environment
echo.
echo [2/7] Creating virtual environment...
if exist "venv" (
    echo [!] Virtual environment already exists
    set /p RECREATE="    Recreate? (y/N): "
    if /i "!RECREATE!"=="y" (
        rmdir /s /q venv
        python -m venv venv
        echo [OK] Virtual environment recreated
    ) else (
        echo [OK] Using existing virtual environment
    )
) else (
    python -m venv venv
    echo [OK] Virtual environment created
)

REM Step 3: Activate and install dependencies
echo.
echo [3/7] Installing dependencies...
call venv\Scripts\activate.bat

echo     Installing pip...
python -m pip install --upgrade pip >nul 2>&1

echo     Installing base requirements...
pip install -r requirements-base.txt >nul 2>&1
if errorlevel 1 (
    echo [X] Failed to install base requirements
    pause
    exit /b 1
)

echo     Installing fetch requirements...
pip install -r requirements-fetch.txt >nul 2>&1
if errorlevel 1 (
    echo [X] Failed to install fetch requirements
    pause
    exit /b 1
)

echo     Installing pandas-ta...
pip install --index-url https://pypi.org/simple/ pandas-ta >nul 2>&1
if errorlevel 1 (
    echo [!] Warning: pandas-ta installation failed (may need Python 3.12+)
)

echo     Installing python-dotenv...
pip install python-dotenv >nul 2>&1

echo [OK] All dependencies installed

REM Step 4: Create directories
echo.
echo [4/7] Creating directory structure...
if not exist "logs" mkdir logs
if not exist "data\market_data" mkdir data\market_data
if not exist "data\metadata" mkdir data\metadata
if not exist "data\cache" mkdir data\cache
if not exist "signals" mkdir signals
if not exist "charts\breakouts" mkdir charts\breakouts
if not exist "charts\indicators" mkdir charts\indicators
if not exist "charts\abc_patterns" mkdir charts\abc_patterns
if not exist "charts\strategies" mkdir charts\strategies
echo [OK] Directory structure created

REM Step 5: Create .env file
echo.
echo [5/7] Checking environment configuration...
if not exist ".env" (
    echo [!] .env file not found
    echo     Creating template .env file...
    (
        echo # Telegram Configuration (Required^)
        echo TELEGRAM_BOT_TOKEN=your_bot_token_here
        echo TELEGRAM_CHAT_ID=your_chat_id_here
        echo.
        echo # Finnhub API (Optional - for insider trading ^& advanced features^)
        echo FINNHUB_API_KEY=your_finnhub_key_here
    ) > .env
    echo [OK] Template .env created
    echo.
    echo     [!] IMPORTANT: Edit .env with your actual credentials!
    echo     Run: notepad .env
) else (
    echo [OK] .env file exists
)

REM Step 6: Test installation
echo.
echo [6/7] Testing installation...
echo     Testing module imports...
python -c "import pandas; import yfinance; import yaml; print('[OK] All modules imported successfully')" 2>nul
if errorlevel 1 (
    echo [X] Installation test failed
    echo     Some modules could not be imported
    pause
    exit /b 1
)

REM Step 7: Create .gitkeep files
echo.
echo [7/7] Finalizing setup...
type nul > data\market_data\.gitkeep
type nul > data\metadata\.gitkeep
type nul > data\cache\.gitkeep
type nul > logs\.gitkeep
echo [OK] Setup finalized

REM Done!
echo.
echo ========================================
echo   Setup Complete!
echo ========================================
echo.
echo Next Steps:
echo.
echo 1. Configure environment variables:
echo    notepad .env
echo    (Add your TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID)
echo.
echo 2. Configure symbols to track:
echo    notepad config\symbols.yaml
echo.
echo 3. Test the system:
echo    scripts\run_daily_workflow.bat
echo.
echo 4. Set up automated scheduling:
echo    - Run: scripts\setup_scheduled_tasks.ps1 (as Administrator)
echo    - OR see LOCAL_SETUP_WINDOWS.md for manual Task Scheduler setup
echo.
echo Quick Commands:
echo    venv\Scripts\activate.bat              - Activate virtual environment
echo    scripts\run_daily_workflow.bat         - Run complete daily workflow
echo    scripts\run_weekly_workflow.bat        - Run weekly S&P 500 scan
echo    python scripts\analyze_symbol.py AAPL  - Analyze specific symbol
echo.
echo Documentation:
echo    LOCAL_SETUP_WINDOWS.md - Complete Windows guide
echo    README.md              - Project overview
echo.
pause
