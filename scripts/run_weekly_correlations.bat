@echo off
REM Update news correlations
cd /d "%~dp0\.."
call venv\Scripts\activate.bat
python scripts\update_news_correlations.py >> logs\correlations.log 2>&1

