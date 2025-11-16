@echo off
REM Generate daily charts only
cd /d "%~dp0\.."
call venv\Scripts\activate.bat
python src\visualize_breakouts.py >> logs\daily_charts.log 2>&1
python src\visualize_breakouts_with_indicators.py >> logs\daily_charts.log 2>&1
python src\visualize_abc_patterns.py >> logs\daily_charts.log 2>&1

