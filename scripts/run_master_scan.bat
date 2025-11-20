@echo off
REM =============================================================================
REM MASTER DAILY SCANNER - Windows
REM Intelligent market scanning system
REM =============================================================================

setlocal enabledelayedexpansion

echo ================================================================================
echo 🤖 MASTER DAILY MARKET SCANNER
echo ================================================================================
echo.

REM Get script directory
set SCRIPT_DIR=%~dp0
set PROJECT_ROOT=%SCRIPT_DIR%..
cd /d "%PROJECT_ROOT%"

REM Check if virtual environment exists
if not exist "venv\" (
    echo ❌ Virtual environment not found!
    echo.
    echo Run setup first:
    echo   .\scripts\setup_local.bat
    exit /b 1
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Load environment variables
if exist ".env" (
    for /f "usebackq tokens=*" %%a in (".env") do (
        set "line=%%a"
        if not "!line:~0,1!"=="#" (
            set "%%a"
        )
    )
    echo ✅ Environment variables loaded
) else (
    echo ⚠️  No .env file found
    echo    Set FINNHUB_API_KEY and TELEGRAM credentials for full functionality
)

echo.
echo ================================================================================
echo 🚀 STARTING INTELLIGENT MARKET SCAN
echo ================================================================================
echo.
echo This will:
echo   1. Fetch complete US market universe (stocks + ETFs)
echo   2. Quick pre-screen for opportunities (price drops, volume spikes)
echo   3. Deep analysis with multi-signal scoring
echo   4. Generate consolidated alert with top 5 trades
echo.
echo Expected time: 5-10 minutes
echo.

REM Run master scanner
python scripts\master_daily_scan.py

REM Check exit code
if %ERRORLEVEL% EQU 0 (
    echo.
    echo ================================================================================
    echo ✅ SCAN COMPLETE!
    echo ================================================================================
    echo.
    echo Results saved to:
    echo   📄 signals\master_scan_results.json
    echo.
    echo Telegram alert sent (if configured)
    echo.
) else (
    echo.
    echo ================================================================================
    echo ❌ SCAN FAILED
    echo ================================================================================
    echo.
    exit /b 1
)

endlocal
