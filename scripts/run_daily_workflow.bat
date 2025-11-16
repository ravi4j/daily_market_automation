@echo off
REM Daily Market Automation - Complete Workflow
REM Run all daily tasks in sequence
REM Usage: scripts\run_daily_workflow.bat

setlocal

REM Get project directory
cd /d "%~dp0\.."
set PROJECT_DIR=%CD%
set LOG_FILE=logs\daily_workflow.log

echo ======================================== >> %LOG_FILE%
echo Daily Market Automation Workflow >> %LOG_FILE%
echo Started: %DATE% %TIME% >> %LOG_FILE%
echo ======================================== >> %LOG_FILE%

echo ========================================
echo   Daily Market Automation Workflow
echo ========================================
echo.

REM Activate virtual environment
if exist "venv\Scripts\activate.bat" (
    echo [OK] Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo [X] Virtual environment not found! Run: scripts\setup_local.bat
    echo [X] Virtual environment not found! >> %LOG_FILE%
    pause
    exit /b 1
)

REM Load environment variables from .env
if exist ".env" (
    for /f "usebackq tokens=1,2 delims==" %%a in (".env") do (
        set "%%a=%%b"
    )
)

REM Check environment variables
if "%TELEGRAM_BOT_TOKEN%"=="" (
    echo [!] Warning: TELEGRAM_BOT_TOKEN not set
)
if "%TELEGRAM_CHAT_ID%"=="" (
    echo [!] Warning: TELEGRAM_CHAT_ID not set
)

REM Step 1: Fetch Market Data
echo.
echo === Step 1: Fetching Market Data ===
echo === Step 1: Fetching Market Data === >> %LOG_FILE%
python src\fetch_daily_prices.py >> %LOG_FILE% 2>&1
if errorlevel 1 (
    echo [X] Failed to fetch market data
    echo [X] Failed to fetch market data >> %LOG_FILE%
    exit /b 1
) else (
    echo [OK] Market data fetched successfully
    echo [OK] Market data fetched successfully >> %LOG_FILE%
)

REM Step 2: Generate Charts
echo.
echo === Step 2: Generating Charts ===
echo === Step 2: Generating Charts === >> %LOG_FILE%

echo   - Breakout charts...
python src\visualize_breakouts.py >> %LOG_FILE% 2>&1

echo   - Indicator charts...
python src\visualize_breakouts_with_indicators.py >> %LOG_FILE% 2>&1

echo   - ABC pattern charts...
python src\visualize_abc_patterns.py >> %LOG_FILE% 2>&1

if errorlevel 1 (
    echo [X] Failed to generate charts
    echo [X] Failed to generate charts >> %LOG_FILE%
    exit /b 1
) else (
    echo [OK] All charts generated successfully
    echo [OK] All charts generated successfully >> %LOG_FILE%
)

REM Step 3: Run Trading Strategies
echo.
echo === Step 3: Running Trading Strategies ===
echo === Step 3: Running Trading Strategies === >> %LOG_FILE%
python scripts\send_daily_alerts.py >> %LOG_FILE% 2>&1
if errorlevel 1 (
    echo [X] Failed to send trading alerts
    echo [X] Failed to send trading alerts >> %LOG_FILE%
    exit /b 1
) else (
    echo [OK] Trading alerts sent successfully
    echo [OK] Trading alerts sent successfully >> %LOG_FILE%
)

REM Step 4: Scan News for Portfolio
echo.
echo === Step 4: Scanning News for Portfolio ===
echo === Step 4: Scanning News for Portfolio === >> %LOG_FILE%
python scripts\send_news_opportunities.py >> %LOG_FILE% 2>&1
if errorlevel 1 (
    echo [X] Failed to scan news opportunities
    echo [X] Failed to scan news opportunities >> %LOG_FILE%
    exit /b 1
) else (
    echo [OK] News opportunities scanned and sent
    echo [OK] News opportunities scanned and sent >> %LOG_FILE%
)

REM Done!
echo.
echo ========================================
echo   [OK] Daily Workflow Complete!
echo ========================================
echo.
echo Summary:
echo   - Market data updated
echo   - Charts generated
echo   - Trading alerts sent
echo   - News opportunities scanned
echo.
echo Check outputs in:
echo   - data\market_data\*.csv
echo   - charts\*\*.png
echo   - signals\*.json
echo.
echo Log saved to: %LOG_FILE%
echo.

echo ======================================== >> %LOG_FILE%
echo Daily Workflow Complete >> %LOG_FILE%
echo Finished: %DATE% %TIME% >> %LOG_FILE%
echo ======================================== >> %LOG_FILE%
echo. >> %LOG_FILE%

if "%1"=="" pause

