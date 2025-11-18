@echo off
REM Daily ETF Trading & Rebalancing Workflow (Windows)
REM Run this after market close (4:30 PM ET or later)

setlocal EnableDelayedExpansion

REM Get project root directory
set "PROJECT_ROOT=%~dp0.."
cd /d "%PROJECT_ROOT%"

REM Create log directory
if not exist "logs" mkdir logs
set "LOG_FILE=logs\etf_workflow_%DATE:~-4,4%%DATE:~-10,2%%DATE:~-7,2%.log"

echo ========================================
echo   Daily ETF Trading ^& Rebalancing
echo ========================================
echo Date: %DATE% %TIME%
echo.
echo ======================================== >> %LOG_FILE%
echo Daily ETF Workflow >> %LOG_FILE%
echo Started: %DATE% %TIME% >> %LOG_FILE%
echo ======================================== >> %LOG_FILE%
echo. >> %LOG_FILE%

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found!
    echo    Run: python -m venv venv
    echo    Then: venv\Scripts\activate.bat
    echo    Then: pip install -r requirements-base.txt
    pause
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Check environment variables
if "%TELEGRAM_BOT_TOKEN%"=="" (
    echo [!] Telegram credentials not set (alerts will be skipped)
    echo    Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID
    echo.
    echo [!] Telegram credentials not set >> %LOG_FILE%
)

REM ============================================================================
REM STEP 1: Update Daily Data
REM ============================================================================
echo.
echo === Step 1: Updating Market Data ===
echo [%TIME%] Updating market data... >> %LOG_FILE%
python src\fetch_daily_prices.py
if errorlevel 1 (
    echo [!] Failed to update market data (continuing...)
    echo [!] Failed to update market data >> %LOG_FILE%
) else (
    echo [OK] Market data updated
    echo [OK] Market data updated >> %LOG_FILE%
)

REM ============================================================================
REM STEP 2: Scan ETFs for Daily Trades
REM ============================================================================
echo.
echo === Step 2: Scanning ETFs for Trades ===
echo [%TIME%] Scanning ETFs... >> %LOG_FILE%
python scripts\daily_etf_trades.py --category recommended_daily_trading
if errorlevel 1 (
    echo [ERROR] Failed to scan ETFs
    echo [ERROR] Failed to scan ETFs >> %LOG_FILE%
    pause
    exit /b 1
) else (
    echo [OK] ETF scan completed
    echo [OK] ETF scan completed >> %LOG_FILE%
)

REM ============================================================================
REM STEP 3: Check Portfolio Rebalancing
REM ============================================================================
echo.
echo === Step 3: Checking Portfolio Rebalancing ===
echo [%TIME%] Checking rebalancing... >> %LOG_FILE%
python scripts\portfolio_rebalancer.py
if errorlevel 1 (
    echo [!] Rebalancing check had errors (non-critical)
    echo [!] Rebalancing check had errors >> %LOG_FILE%
) else (
    echo [OK] Rebalancing check completed
    echo [OK] Rebalancing check completed >> %LOG_FILE%
)

REM ============================================================================
REM END OF WORKFLOW
REM ============================================================================

echo.
echo ========================================
echo   [OK] ETF Workflow Complete!
echo ========================================
echo.
echo Summary:
echo   - Market data updated
echo   - ETF trades identified
echo   - Rebalancing checked
echo.
echo Check outputs in:
echo   - signals\daily_etf_trades.json
echo   - signals\rebalancing_report.txt (if needed)
echo   - signals\rebalancing_orders.json (if needed)
echo.

REM Show ETF results if available
if exist "signals\daily_etf_trades.json" (
    echo ETF Scan Results:
    python -c "import json; data=json.load(open('signals/daily_etf_trades.json')); print('   [OK] Found', data.get('total_trades', 0), 'opportunities across', data.get('categories_covered', 0), 'categories')"
)

REM Show rebalancing results if available
if exist "signals\rebalancing_orders.json" (
    echo.
    echo Rebalancing Results:
    python -c "import json; data=json.load(open('signals/rebalancing_orders.json')); orders=data.get('total_orders', 0); print('   [!] ' + str(orders) + ' trade orders generated' if orders > 0 else '   [OK] Portfolio is balanced')"
    if exist "signals\rebalancing_report.txt" (
        echo    Review: signals\rebalancing_report.txt
    )
) else (
    if exist "signals\rebalancing_report.txt" (
        echo.
        echo Rebalancing Results:
        echo    [OK] Portfolio is balanced (no trades needed)
    )
)

echo.
echo Log saved to: %LOG_FILE%
echo.
echo Next: Review Telegram alerts and execute trades if needed
echo.

echo ======================================== >> %LOG_FILE%
echo ETF Workflow Complete >> %LOG_FILE%
echo Finished: %DATE% %TIME% >> %LOG_FILE%
echo ======================================== >> %LOG_FILE%
echo. >> %LOG_FILE%

if "%1"=="" pause
