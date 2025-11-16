# 🏠 Local Machine Setup Guide

Complete guide for running the Daily Market Automation system on your own machine instead of GitHub Actions.

---

## 📋 Table of Contents

1. [Initial Setup](#initial-setup)
2. [Directory Structure](#directory-structure)
3. [Running Scripts Manually](#running-scripts-manually)
4. [Automated Scheduling (Cron/Task Scheduler)](#automated-scheduling)
5. [Daily Workflow](#daily-workflow)
6. [Troubleshooting](#troubleshooting)

---

## 🚀 Initial Setup

### 1. Clone Repository (Already Done)

```bash
cd /Users/rsharm231/mb-code/code/ravi4j-repos-code/daily_market_automation
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate  # Windows
```

### 3. Install Dependencies

```bash
# Install all requirements
pip install -r requirements-base.txt
pip install -r requirements-fetch.txt
pip install --index-url https://pypi.org/simple/ pandas-ta
```

### 4. Set Environment Variables

Create a `.env` file in the project root:

```bash
# .env file (add to .gitignore, already there)
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
FINNHUB_API_KEY=your_finnhub_key_here  # Optional
```

**Load environment variables:**

```bash
# Option A: Export manually (temporary, session-only)
export TELEGRAM_BOT_TOKEN='your_token'
export TELEGRAM_CHAT_ID='your_chat_id'
export FINNHUB_API_KEY='your_key'

# Option B: Use dotenv (install python-dotenv)
pip install python-dotenv
# Then scripts will auto-load from .env

# Option C: Add to your shell profile (permanent)
echo 'export TELEGRAM_BOT_TOKEN="your_token"' >> ~/.zshrc
echo 'export TELEGRAM_CHAT_ID="your_chat_id"' >> ~/.zshrc
echo 'export FINNHUB_API_KEY="your_key"' >> ~/.zshrc
source ~/.zshrc
```

---

## 📁 Directory Structure

After setup, your structure will be:

```
daily_market_automation/
├── venv/                       # Virtual environment (local only)
├── .env                        # Environment variables (local only)
├── data/
│   ├── market_data/           # CSV price data
│   ├── metadata/              # S&P 500 lists, correlation DB
│   └── cache/                 # Temp cache (auto-cleaned)
├── signals/                   # Generated signals/alerts
├── charts/                    # Generated charts
│   ├── breakouts/
│   ├── indicators/
│   └── abc_patterns/
├── logs/                      # Log files (create this)
│   ├── daily_fetch.log
│   ├── daily_charts.log
│   ├── daily_alerts.log
│   └── sp500_scan.log
├── scripts/                   # Automation scripts
├── src/                       # Core modules
└── config/                    # Configuration files
```

**Create logs directory:**

```bash
mkdir -p logs
```

---

## 🎯 Running Scripts Manually

### Daily Workflow (Run in Order)

#### 1. Fetch Latest Market Data

```bash
# Activate venv first
source venv/bin/activate

# Fetch data for all symbols in config/symbols.yaml
python src/fetch_daily_prices.py

# Check what was updated
ls -lh data/market_data/*.csv
```

**Output:**
```
✅ Saved AAPL -> data/market_data/AAPL.csv
✅ Saved TQQQ -> data/market_data/TQQQ.csv
...
```

---

#### 2. Generate Charts

```bash
# Generate all chart types
python src/visualize_breakouts.py              # Simple breakout charts
python src/visualize_breakouts_with_indicators.py  # Enhanced with indicators
python src/visualize_abc_patterns.py           # ABC pattern charts

# Check generated charts
ls -lh charts/*/*.png
```

**Output:**
```
charts/breakouts/AAPL.png
charts/indicators/AAPL_indicators.png
charts/abc_patterns/AAPL_ABC_BULLISH.png
```

---

#### 3. Run Trading Strategies & Send Alerts

```bash
# Run all strategies and send Telegram alerts
python scripts/send_daily_alerts.py

# OR with specific confidence level
python scripts/send_daily_alerts.py --min-confidence HIGH

# OR specific strategies only
python scripts/send_daily_alerts.py --strategies rsi_macd trend_following
```

**Output:**
```
📱 Sending combined message with 3 alerts to Telegram...
✅ Message sent successfully!
```

---

#### 4. News Scanner (Daily Portfolio)

```bash
# Scan your portfolio symbols for news opportunities
python scripts/send_news_opportunities.py
```

**Output:**
```
📰 Scanning 4 symbols for opportunities...
✅ Insider tracking enabled
💼 Fetching insider data...
✅ Found 2 opportunities
📤 Sent to Telegram
```

---

#### 5. Weekly S&P 500 Scan

```bash
# First, update S&P 500 list (weekly or monthly)
python scripts/fetch_sp500_list.py

# Then scan for opportunities
python scripts/scan_sp500_news.py

# OR test mode first
python scripts/scan_sp500_news.py --top 10

# OR full scan (slower)
python scripts/scan_sp500_news.py --full-scan

# OR specific sector
python scripts/scan_sp500_news.py --sector "Information Technology"
```

**Output:**
```
📊 Loading S&P 500 constituent list...
🔍 Pre-filtering for stocks with 5.0%+ drops...
✅ Found 47 stocks with 5.0%+ drops (from 503 total)
📰 Scanning 47 stocks for opportunities...
✅ Scan complete! Found 12 opportunities
📤 Sending to Telegram...
```

---

#### 6. Update News Correlations (Weekly)

```bash
# Update price movements and recalculate correlations
python scripts/update_news_correlations.py
```

**Output:**
```
📊 Updating News Correlations...
📈 Updating price movements for 15 symbols...
🔄 Recalculating correlations...
✅ Update complete!
```

---

#### 7. On-Demand Analysis

```bash
# Analyze a specific symbol
python scripts/analyze_symbol.py NVDA
python scripts/send_analysis_to_telegram.py NVDA

# OR combined
python scripts/analyze_symbol.py NVDA && python scripts/send_analysis_to_telegram.py NVDA
```

---

## 🤖 Automated Scheduling

### Option A: macOS/Linux (Cron)

**Edit crontab:**

```bash
crontab -e
```

**Add these entries:**

```bash
# Daily Market Automation Schedule
# Make sure to use full paths!

# Set environment variables (adjust paths)
TELEGRAM_BOT_TOKEN=your_token
TELEGRAM_CHAT_ID=your_chat_id
FINNHUB_API_KEY=your_key
PATH=/usr/local/bin:/usr/bin:/bin

# Project directory
PROJECT=/Users/rsharm231/mb-code/code/ravi4j-repos-code/daily_market_automation

# 1. Fetch data daily at 4:30 PM EST (after market close)
30 16 * * 1-5 cd $PROJECT && venv/bin/python src/fetch_daily_prices.py >> logs/daily_fetch.log 2>&1

# 2. Generate charts at 4:35 PM EST
35 16 * * 1-5 cd $PROJECT && venv/bin/python src/visualize_breakouts.py >> logs/daily_charts.log 2>&1
35 16 * * 1-5 cd $PROJECT && venv/bin/python src/visualize_breakouts_with_indicators.py >> logs/daily_charts.log 2>&1
35 16 * * 1-5 cd $PROJECT && venv/bin/python src/visualize_abc_patterns.py >> logs/daily_charts.log 2>&1

# 3. Run strategies and send alerts at 4:40 PM EST
40 16 * * 1-5 cd $PROJECT && venv/bin/python scripts/send_daily_alerts.py >> logs/daily_alerts.log 2>&1

# 4. Scan news for portfolio at 4:45 PM EST
45 16 * * 1-5 cd $PROJECT && venv/bin/python scripts/send_news_opportunities.py >> logs/news_scan.log 2>&1

# 5. Weekly S&P 500 scan on Sundays at 6 PM EST
0 18 * * 0 cd $PROJECT && venv/bin/python scripts/fetch_sp500_list.py >> logs/sp500_scan.log 2>&1
5 18 * * 0 cd $PROJECT && venv/bin/python scripts/scan_sp500_news.py >> logs/sp500_scan.log 2>&1

# 6. Update correlations weekly on Sundays at 12 PM EST
0 12 * * 0 cd $PROJECT && venv/bin/python scripts/update_news_correlations.py >> logs/correlations.log 2>&1
```

**Verify cron jobs:**

```bash
crontab -l
```

**Check cron logs:**

```bash
tail -f logs/daily_fetch.log
tail -f logs/daily_alerts.log
```

---

### Option B: macOS (LaunchAgent - Recommended)

**Create launch agent plist files:**

```bash
# Create LaunchAgents directory if it doesn't exist
mkdir -p ~/Library/LaunchAgents
```

**1. Daily Market Fetch** (`~/Library/LaunchAgents/com.daily.market.fetch.plist`):

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.daily.market.fetch</string>
    <key>ProgramArguments</key>
    <array>
        <string>/Users/rsharm231/mb-code/code/ravi4j-repos-code/daily_market_automation/venv/bin/python</string>
        <string>/Users/rsharm231/mb-code/code/ravi4j-repos-code/daily_market_automation/src/fetch_daily_prices.py</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>16</integer>
        <key>Minute</key>
        <integer>30</integer>
        <key>Weekday</key>
        <integer>1-5</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>/Users/rsharm231/mb-code/code/ravi4j-repos-code/daily_market_automation/logs/daily_fetch.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/rsharm231/mb-code/code/ravi4j-repos-code/daily_market_automation/logs/daily_fetch_error.log</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>TELEGRAM_BOT_TOKEN</key>
        <string>your_token_here</string>
        <key>TELEGRAM_CHAT_ID</key>
        <string>your_chat_id_here</string>
        <key>FINNHUB_API_KEY</key>
        <string>your_key_here</string>
    </dict>
</dict>
</plist>
```

**Load the launch agent:**

```bash
launchctl load ~/Library/LaunchAgents/com.daily.market.fetch.plist
launchctl list | grep com.daily.market
```

**Unload/reload if needed:**

```bash
launchctl unload ~/Library/LaunchAgents/com.daily.market.fetch.plist
launchctl load ~/Library/LaunchAgents/com.daily.market.fetch.plist
```

---

### Option C: Windows (Task Scheduler)

**Create batch script** (`run_daily_fetch.bat`):

```batch
@echo off
cd /d C:\path\to\daily_market_automation
call venv\Scripts\activate
python src\fetch_daily_prices.py >> logs\daily_fetch.log 2>&1
```

**Schedule in Task Scheduler:**

1. Open Task Scheduler
2. Create Basic Task
3. Name: "Daily Market Fetch"
4. Trigger: Daily at 4:30 PM, Monday-Friday
5. Action: Start a program
6. Program: `C:\path\to\run_daily_fetch.bat`
7. Done!

---

## 📅 Daily Workflow Summary

### Automated Schedule (Recommended)

```
4:30 PM EST - Fetch latest market data
4:35 PM EST - Generate all charts
4:40 PM EST - Run strategies & send alerts
4:45 PM EST - Scan news for portfolio

Sunday 12:00 PM EST - Update correlations
Sunday  6:00 PM EST - S&P 500 weekly scan
```

### Manual Workflow (For Testing)

```bash
# Create a master script: scripts/run_daily_workflow.sh

#!/bin/bash
set -e  # Exit on error

PROJECT_DIR="/Users/rsharm231/mb-code/code/ravi4j-repos-code/daily_market_automation"
cd "$PROJECT_DIR"

# Activate virtual environment
source venv/bin/activate

echo "=== 1. Fetching Market Data ==="
python src/fetch_daily_prices.py

echo -e "\n=== 2. Generating Charts ==="
python src/visualize_breakouts.py
python src/visualize_breakouts_with_indicators.py
python src/visualize_abc_patterns.py

echo -e "\n=== 3. Running Strategies & Sending Alerts ==="
python scripts/send_daily_alerts.py

echo -e "\n=== 4. Scanning News for Portfolio ==="
python scripts/send_news_opportunities.py

echo -e "\n✅ Daily workflow complete!"
```

**Make it executable:**

```bash
chmod +x scripts/run_daily_workflow.sh
```

**Run it:**

```bash
./scripts/run_daily_workflow.sh
```

---

## 🔍 Monitoring & Logs

### View Logs

```bash
# Real-time monitoring
tail -f logs/daily_fetch.log
tail -f logs/daily_alerts.log
tail -f logs/sp500_scan.log

# View last 50 lines
tail -50 logs/daily_fetch.log

# Search for errors
grep -i error logs/*.log
grep -i success logs/*.log
```

### Log Rotation (Keep logs manageable)

```bash
# Add to crontab (rotate logs weekly)
0 0 * * 0 cd /Users/rsharm231/mb-code/code/ravi4j-repos-code/daily_market_automation && find logs/ -name "*.log" -mtime +30 -delete
```

---

## 🛠️ Troubleshooting

### Issue: Scripts not finding modules

**Solution:** Always activate venv first

```bash
source venv/bin/activate
```

### Issue: Permission denied for scripts

**Solution:** Make scripts executable

```bash
chmod +x scripts/*.py
chmod +x src/*.py
```

### Issue: Cron job not running

**Solution:** Check cron is running and has permissions

```bash
# macOS: Check launchd
launchctl list | grep cron

# Check cron logs (macOS)
log show --predicate 'process == "cron"' --last 1h
```

### Issue: Environment variables not loaded in cron

**Solution:** Set them in crontab directly or use full paths

```bash
# In crontab
TELEGRAM_BOT_TOKEN=your_token
TELEGRAM_CHAT_ID=your_chat_id

# OR load from file
* * * * * source ~/.zshrc && /path/to/script.py
```

### Issue: Virtual environment not found

**Solution:** Use absolute paths in cron

```bash
# Bad
python src/fetch_daily_prices.py

# Good
/Users/rsharm231/mb-code/code/ravi4j-repos-code/daily_market_automation/venv/bin/python /Users/rsharm231/mb-code/code/ravi4j-repos-code/daily_market_automation/src/fetch_daily_prices.py
```

---

## 📊 Quick Reference

### Essential Commands

```bash
# Activate environment
source venv/bin/activate

# Daily workflow
./scripts/run_daily_workflow.sh

# Individual scripts
python src/fetch_daily_prices.py
python scripts/send_daily_alerts.py
python scripts/send_news_opportunities.py
python scripts/scan_sp500_news.py

# Check what's running
ps aux | grep python
crontab -l
launchctl list | grep market

# View logs
tail -f logs/*.log
```

---

## 🎯 Next Steps

1. ✅ Set up virtual environment
2. ✅ Install dependencies
3. ✅ Configure environment variables
4. ✅ Test scripts manually
5. ✅ Set up automated scheduling (cron/launchd)
6. ✅ Monitor logs for a week
7. ✅ Adjust timing as needed

---

**Ready to run everything locally!** 🚀

Let me know if you want me to create the master workflow script or help set up the cron jobs!

