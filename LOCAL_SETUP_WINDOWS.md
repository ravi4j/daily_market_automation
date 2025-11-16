# 🪟 Windows 11 Setup Guide

Complete guide for running the Daily Market Automation system on Windows 11.

---

## 📋 Table of Contents

1. [Initial Setup](#initial-setup)
2. [Running Scripts](#running-scripts)
3. [Automated Scheduling (Task Scheduler)](#automated-scheduling)
4. [Daily Workflow](#daily-workflow)
5. [Troubleshooting](#troubleshooting)

---

## 🚀 Initial Setup

### Prerequisites

1. **Python 3.12+** installed
   - Download from: https://www.python.org/downloads/
   - ⚠️ **IMPORTANT**: Check "Add Python to PATH" during installation

2. **Git** (if not already installed)
   - Download from: https://git-scm.com/download/win

### Step 1: Clone/Navigate to Repository

```powershell
# Open PowerShell or Command Prompt
cd C:\Users\YourUsername\path\to\daily_market_automation
```

### Step 2: Run Automated Setup Script

```powershell
# This will set everything up automatically
.\scripts\setup_local.bat
```

**What it does:**
- ✅ Checks Python version (3.12+ required)
- ✅ Creates virtual environment
- ✅ Installs all dependencies
- ✅ Creates directory structure
- ✅ Creates template `.env` file
- ✅ Tests installation

### Step 3: Configure Environment Variables

**Option A: Using `.env` file (Recommended)**

Edit `.env` file in the project root:

```plaintext
# .env file
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
FINNHUB_API_KEY=your_finnhub_key_here
```

**Option B: Set System Environment Variables**

1. Press `Win + X` → Select "System"
2. Click "Advanced system settings"
3. Click "Environment Variables"
4. Under "User variables", click "New"
5. Add:
   - Variable: `TELEGRAM_BOT_TOKEN`, Value: `your_token`
   - Variable: `TELEGRAM_CHAT_ID`, Value: `your_chat_id`
   - Variable: `FINNHUB_API_KEY`, Value: `your_key`

### Step 4: Configure Symbols

Edit `config\symbols.yaml`:

```yaml
symbols:
  - AAPL
  - TQQQ
  - UBER
  - NVDA
```

---

## 🎯 Running Scripts

### Using Batch Scripts (Easy Way)

#### Run Complete Daily Workflow

```powershell
.\scripts\run_daily_workflow.bat
```

This runs all steps:
1. Fetch market data
2. Generate charts
3. Run strategies and send alerts
4. Scan news opportunities

#### Run Weekly Workflow

```powershell
.\scripts\run_weekly_workflow.bat
```

This runs:
1. Update S&P 500 list
2. Scan S&P 500 for opportunities
3. Update news correlations

---

### Manual Commands (Advanced)

#### Activate Virtual Environment

```powershell
# PowerShell
.\venv\Scripts\Activate.ps1

# OR Command Prompt
venv\Scripts\activate.bat
```

#### Individual Scripts

```powershell
# 1. Fetch market data
python src\fetch_daily_prices.py

# 2. Generate charts
python src\visualize_breakouts.py
python src\visualize_breakouts_with_indicators.py
python src\visualize_abc_patterns.py

# 3. Run strategies and alerts
python scripts\send_daily_alerts.py

# 4. News scanner (portfolio)
python scripts\send_news_opportunities.py

# 5. S&P 500 scanner
python scripts\fetch_sp500_list.py
python scripts\scan_sp500_news.py

# 6. On-demand analysis
python scripts\analyze_symbol.py AAPL
python scripts\send_analysis_to_telegram.py AAPL
```

---

## 🤖 Automated Scheduling

### Using Task Scheduler (Recommended)

#### Quick Setup Script

Run the automated Task Scheduler setup:

```powershell
# Run as Administrator (Right-click → Run as Administrator)
.\scripts\setup_scheduled_tasks.ps1
```

This creates all scheduled tasks automatically!

---

### Manual Task Scheduler Setup

#### 1. Open Task Scheduler

Press `Win + R`, type `taskschd.msc`, press Enter

#### 2. Create Daily Market Fetch Task

**Step-by-step:**

1. Click "Create Task" (right panel)
2. **General Tab:**
   - Name: `Daily Market Fetch`
   - Description: `Fetch daily stock market data`
   - Security options: "Run whether user is logged on or not"
   - Configure for: Windows 11

3. **Triggers Tab:**
   - Click "New"
   - Begin the task: "On a schedule"
   - Daily, recur every: 1 days
   - Start time: `4:30 PM`
   - Advanced settings → Repeat task every: (leave unchecked)
   - Days of week: Monday, Tuesday, Wednesday, Thursday, Friday
   - Click "OK"

4. **Actions Tab:**
   - Click "New"
   - Action: "Start a program"
   - Program/script: `C:\Users\YourUsername\path\to\daily_market_automation\scripts\run_daily_fetch.bat`
   - Start in: `C:\Users\YourUsername\path\to\daily_market_automation`
   - Click "OK"

5. **Conditions Tab:**
   - Uncheck "Start the task only if the computer is on AC power"
   - Check "Wake the computer to run this task"

6. **Settings Tab:**
   - Check "Allow task to be run on demand"
   - Check "Run task as soon as possible after a scheduled start is missed"
   - Click "OK"

#### 3. Create Other Scheduled Tasks

Repeat the above process for:

| Task Name | Script | Time | Days |
|-----------|--------|------|------|
| Daily Market Charts | `run_daily_charts.bat` | 4:35 PM | Mon-Fri |
| Daily Market Alerts | `run_daily_alerts.bat` | 4:40 PM | Mon-Fri |
| Daily News Scanner | `run_daily_news.bat` | 4:45 PM | Mon-Fri |
| Weekly S&P 500 Scan | `run_weekly_workflow.bat` | 6:00 PM | Sunday |
| Weekly Correlations | `run_weekly_correlations.bat` | 12:00 PM | Sunday |

---

### PowerShell Scheduled Tasks (Alternative)

**Create tasks via PowerShell (Run as Administrator):**

```powershell
# Daily Market Fetch (4:30 PM, Mon-Fri)
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday,Tuesday,Wednesday,Thursday,Friday -At 4:30PM
$action = New-ScheduledTaskAction -Execute "C:\Users\YourUsername\path\to\daily_market_automation\scripts\run_daily_workflow.bat" -WorkingDirectory "C:\Users\YourUsername\path\to\daily_market_automation"
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -WakeToRun
Register-ScheduledTask -TaskName "Daily Market Automation" -Trigger $trigger -Action $action -Settings $settings -Description "Daily market data fetch and analysis"

# Weekly S&P 500 Scan (Sunday 6 PM)
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At 6:00PM
$action = New-ScheduledTaskAction -Execute "C:\Users\YourUsername\path\to\daily_market_automation\scripts\run_weekly_workflow.bat" -WorkingDirectory "C:\Users\YourUsername\path\to\daily_market_automation"
Register-ScheduledTask -TaskName "Weekly S&P 500 Scan" -Trigger $trigger -Action $action -Settings $settings -Description "Weekly S&P 500 opportunity scan"
```

---

## 📅 Daily Schedule

### Automated (Recommended)

```
Monday - Friday:
  4:30 PM EST - Fetch market data
  4:35 PM EST - Generate charts
  4:40 PM EST - Run strategies & send alerts
  4:45 PM EST - Scan news for portfolio

Sunday:
  12:00 PM EST - Update news correlations
   6:00 PM EST - S&P 500 weekly scan
```

### Manual Testing

```powershell
# Run complete workflow
.\scripts\run_daily_workflow.bat

# View output
type logs\daily_workflow.log
```

---

## 📊 Monitoring & Logs

### View Logs

```powershell
# Real-time monitoring (PowerShell)
Get-Content logs\daily_fetch.log -Wait -Tail 50

# View last 50 lines
Get-Content logs\daily_fetch.log -Tail 50

# Search for errors
Select-String -Path "logs\*.log" -Pattern "error" -CaseSensitive:$false

# View all logs
type logs\daily_fetch.log
type logs\daily_alerts.log
type logs\sp500_scan.log
```

### Check Scheduled Tasks Status

```powershell
# List all market automation tasks
Get-ScheduledTask | Where-Object {$_.TaskName -like "*Market*"}

# Check task history
Get-ScheduledTask -TaskName "Daily Market Automation" | Get-ScheduledTaskInfo

# View last run result
(Get-ScheduledTask -TaskName "Daily Market Automation").State
(Get-ScheduledTask -TaskName "Daily Market Automation").LastRunTime
(Get-ScheduledTask -TaskName "Daily Market Automation").LastTaskResult
```

---

## 🛠️ Troubleshooting

### Issue: Python not found

**Error:** `'python' is not recognized as an internal or external command`

**Solution:**

1. Reinstall Python with "Add to PATH" checked
2. OR manually add Python to PATH:
   - Press `Win + X` → System → Advanced system settings
   - Environment Variables → System variables → Path → Edit
   - Add: `C:\Users\YourUsername\AppData\Local\Programs\Python\Python312`
   - Add: `C:\Users\YourUsername\AppData\Local\Programs\Python\Python312\Scripts`

### Issue: PowerShell execution policy

**Error:** `cannot be loaded because running scripts is disabled`

**Solution:**

```powershell
# Run PowerShell as Administrator
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Issue: Virtual environment not activating

**Solution:**

```powershell
# Try full path
C:\path\to\daily_market_automation\venv\Scripts\activate.bat

# OR recreate venv
rmdir /s /q venv
python -m venv venv
venv\Scripts\activate.bat
pip install -r requirements-base.txt
pip install -r requirements-fetch.txt
pip install pandas-ta
```

### Issue: Task Scheduler not running

**Check:**

1. Task Scheduler service is running:
   ```powershell
   Get-Service -Name "Schedule" | Start-Service
   ```

2. Task history enabled:
   - Open Task Scheduler
   - Action → Enable All Tasks History

3. Check last run status:
   - Open Task Scheduler
   - Find your task → History tab

### Issue: Environment variables not loaded

**Solution:**

Batch files should load from `.env` automatically via `python-dotenv`:

```batch
@echo off
cd /d %~dp0\..
call venv\Scripts\activate.bat
pip install python-dotenv
python -c "from dotenv import load_dotenv; load_dotenv()"
python src\fetch_daily_prices.py
```

### Issue: Firewall blocking scripts

**Solution:**

1. Windows Security → Firewall & network protection
2. Allow an app through firewall
3. Add Python: `C:\Users\YourUsername\AppData\Local\Programs\Python\Python312\python.exe`

---

## 🎯 Quick Reference

### Essential Commands

```powershell
# Activate environment
.\venv\Scripts\Activate.ps1

# Run workflows
.\scripts\run_daily_workflow.bat
.\scripts\run_weekly_workflow.bat

# Individual scripts
python src\fetch_daily_prices.py
python scripts\send_daily_alerts.py
python scripts\send_news_opportunities.py

# Check scheduled tasks
Get-ScheduledTask | Where-Object {$_.TaskName -like "*Market*"}

# View logs
Get-Content logs\daily_fetch.log -Tail 50
```

### File Locations

```
Project Root: C:\Users\YourUsername\...\daily_market_automation\
├── venv\                      # Virtual environment
├── .env                       # Environment variables
├── logs\                      # Log files
│   ├── daily_fetch.log
│   ├── daily_alerts.log
│   └── sp500_scan.log
├── data\
│   ├── market_data\          # CSV files
│   ├── metadata\             # S&P 500, correlations
│   └── cache\                # Temp cache
├── charts\                   # Generated charts
└── signals\                  # Trading signals
```

---

## 📝 Next Steps

### First Time Setup

1. ✅ Run `.\scripts\setup_local.bat`
2. ✅ Edit `.env` with your credentials
3. ✅ Edit `config\symbols.yaml` with your portfolio
4. ✅ Test: `.\scripts\run_daily_workflow.bat`
5. ✅ Set up Task Scheduler: `.\scripts\setup_scheduled_tasks.ps1`
6. ✅ Monitor logs for a week

### Ongoing Maintenance

- **Daily:** Check Telegram for alerts
- **Weekly:** Review S&P 500 opportunities
- **Monthly:** Update dependencies: `pip install -r requirements-base.txt --upgrade`

---

## 🚀 Ready to Go!

Your Windows 11 machine is now set up to run the Daily Market Automation system!

**Need help?** Check the main documentation:
- `README.md` - Project overview
- `LOCAL_SETUP_GUIDE.md` - macOS/Linux setup
- `QUICKSTART_CONFIG.md` - Configuration guide

**Questions?** Open an issue on GitHub or check the logs!
