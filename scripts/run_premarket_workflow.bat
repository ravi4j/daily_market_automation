@echo off
REM Pre-Market Gap Monitor Workflow for Windows
REM Runs morning gap detection and sends Telegram alerts
REM Usage: scripts\run_premarket_workflow.bat

setlocal enabledelayedexpansion

REM Change to project directory
cd /d "%~dp0\.." || exit /b 1

echo.
echo ============================================================================
echo                   PRE-MARKET GAP MONITOR WORKFLOW
echo ============================================================================
echo.

REM Get current time (Windows doesn't have easy timezone conversion)
for /f "tokens=1-3 delims=:." %%a in ("%time%") do (
    set hour=%%a
    set minute=%%b
)
echo Current Time: %date% %time%
echo.

REM ============================================================================
REM PRE-FLIGHT CHECKS
REM ============================================================================

echo === Pre-Flight Checks ===
echo.

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo [X] Virtual environment not found
    echo     Run: python -m venv venv
    echo     Then: venv\Scripts\activate
    exit /b 1
) else (
    echo [OK] Virtual environment found
)

REM Activate virtual environment
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [X] Failed to activate virtual environment
    exit /b 1
)
echo [OK] Virtual environment activated

REM Check environment variables
if "%TELEGRAM_BOT_TOKEN%"=="" (
    echo [X] TELEGRAM_BOT_TOKEN not set
    echo     Set it in your .env file or environment variables
    exit /b 1
) else (
    echo [OK] TELEGRAM_BOT_TOKEN is set
)

if "%TELEGRAM_CHAT_ID%"=="" (
    echo [X] TELEGRAM_CHAT_ID not set
    echo     Set it in your .env file or environment variables
    exit /b 1
) else (
    echo [OK] TELEGRAM_CHAT_ID is set
)

REM Check if positions are configured
echo.
echo === Checking Configuration ===
echo.

findstr /R "^  [A-Z]" config\premarket_config.yaml >nul 2>&1
if errorlevel 1 (
    echo [!] No positions configured in premarket_config.yaml
    echo     Add your active positions to receive gap alerts
    echo     Edit: config\premarket_config.yaml
) else (
    echo [OK] Positions configured in premarket_config.yaml
)

echo.

REM ============================================================================
REM WORKFLOW EXECUTION
REM Add new steps below following the same pattern
REM See WORKFLOW_MAINTENANCE.md for details
REM ============================================================================

echo === Running Pre-Market Gap Monitor ===
python scripts\send_premarket_alerts.py

if errorlevel 1 (
    echo [X] Failed to send pre-market alerts
    exit /b 1
) else (
    echo [OK] Pre-market alerts sent successfully
)

REM ============================================================================
REM END OF WORKFLOW
REM All workflow steps completed above
REM ============================================================================

echo.
echo ============================================================================
echo                    [OK] WORKFLOW COMPLETED SUCCESSFULLY
echo ============================================================================
echo.
echo Summary:
echo   * Pre-market gaps detected and analyzed
echo   * Market futures sentiment assessed
echo   * Telegram alerts sent
echo.
echo Next scheduled runs:
echo   * 7:00 AM ET (early warning)
echo   * 8:00 AM ET (mid-check)
echo   * 9:00 AM ET (final warning before open)
echo.
echo Market opens at 9:30 AM ET
echo.

endlocal

