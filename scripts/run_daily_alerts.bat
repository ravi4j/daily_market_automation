@echo off
REM Run trading strategies and send alerts
cd /d "%~dp0\.."
call venv\Scripts\activate.bat
python scripts\send_daily_alerts.py >> logs\daily_alerts.log 2>&1

