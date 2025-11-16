@echo off
REM Weekly Market Automation - S&P 500 Scan & Correlations Update
REM Run weekly tasks (typically Sunday evenings)
REM Usage: scripts\run_weekly_workflow.bat

setlocal

cd /d "%~dp0\.."
set PROJECT_DIR=%CD%
set LOG_FILE=logs\weekly_workflow.log

echo ======================================== >> %LOG_FILE%
echo Weekly Market Automation Workflow >> %LOG_FILE%
echo Started: %DATE% %TIME% >> %LOG_FILE%
echo ======================================== >> %LOG_FILE%

echo ========================================
echo   Weekly Market Automation Workflow
echo ========================================
echo.

REM Activate virtual environment
if exist "venv\Scripts\activate.bat" (
    echo [OK] Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo [X] Virtual environment not found!
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

REM Step 1: Update S&P 500 List
echo.
echo === Step 1: Update S&P 500 List ===
echo === Step 1: Update S&P 500 List === >> %LOG_FILE%
python scripts\fetch_sp500_list.py >> %LOG_FILE% 2>&1
if errorlevel 1 (
    echo [X] Failed to update S&P 500 list
    echo [X] Failed to update S&P 500 list >> %LOG_FILE%
    exit /b 1
) else (
    echo [OK] S&P 500 list updated
    echo [OK] S&P 500 list updated >> %LOG_FILE%
)

REM Step 2: Scan S&P 500 for Opportunities
echo.
echo === Step 2: Scan S&P 500 for Opportunities ===
echo === Step 2: Scan S&P 500 for Opportunities === >> %LOG_FILE%
python scripts\scan_sp500_news.py >> %LOG_FILE% 2>&1
if errorlevel 1 (
    echo [X] Failed to scan S&P 500
    echo [X] Failed to scan S&P 500 >> %LOG_FILE%
    exit /b 1
) else (
    echo [OK] S&P 500 scan complete
    echo [OK] S&P 500 scan complete >> %LOG_FILE%
)

REM Step 3: Update News Correlations
echo.
echo === Step 3: Update News Correlations ===
echo === Step 3: Update News Correlations === >> %LOG_FILE%
python scripts\update_news_correlations.py >> %LOG_FILE% 2>&1
if errorlevel 1 (
    echo [X] Failed to update correlations
    echo [X] Failed to update correlations >> %LOG_FILE%
    exit /b 1
) else (
    echo [OK] News correlations updated
    echo [OK] News correlations updated >> %LOG_FILE%
)

REM Done!
echo.
echo ========================================
echo   [OK] Weekly Workflow Complete!
echo ========================================
echo.
echo Summary:
echo   - S&P 500 list updated
echo   - Opportunities scanned and sent
echo   - Historical correlations updated
echo.
echo Log saved to: %LOG_FILE%
echo.

echo ======================================== >> %LOG_FILE%
echo Weekly Workflow Complete >> %LOG_FILE%
echo Finished: %DATE% %TIME% >> %LOG_FILE%
echo ======================================== >> %LOG_FILE%
echo. >> %LOG_FILE%

if "%1"=="" pause

