@echo off
REM Scan news for portfolio
cd /d "%~dp0\.."
call venv\Scripts\activate.bat
python scripts\send_news_opportunities.py >> logs\news_scan.log 2>&1

