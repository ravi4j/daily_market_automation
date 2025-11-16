@echo off
REM Fetch daily market data only
cd /d "%~dp0\.."
call venv\Scripts\activate.bat
python src\fetch_daily_prices.py >> logs\daily_fetch.log 2>&1

