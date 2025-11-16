# 🚀 Windows 11 Quick Start

Get up and running in 5 minutes!

---

## 📦 One-Command Setup

Open PowerShell or Command Prompt in the project directory and run:

```powershell
.\scripts\setup_local.bat
```

This will:
- ✅ Check Python 3.12+
- ✅ Create virtual environment
- ✅ Install all dependencies
- ✅ Create folder structure
- ✅ Create `.env` template

---

## 🔑 Configure Credentials

Edit `.env` file:

```powershell
notepad .env
```

Add your credentials:

```plaintext
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=-1001234567890
FINNHUB_API_KEY=your_key_here
```

---

## 📝 Configure Symbols

Edit `config\symbols.yaml`:

```powershell
notepad config\symbols.yaml
```

Add your portfolio:

```yaml
symbols:
  - AAPL
  - TQQQ
  - NVDA
```

---

## 🧪 Test Run

Run the complete daily workflow:

```powershell
.\scripts\run_daily_workflow.bat
```

You should see:
```
========================================
  Daily Market Automation Workflow
========================================

[OK] Activating virtual environment...

=== Step 1: Fetching Market Data ===
[OK] Market data fetched successfully

=== Step 2: Generating Charts ===
[OK] All charts generated successfully

=== Step 3: Running Trading Strategies ===
[OK] Trading alerts sent successfully

=== Step 4: Scanning News for Portfolio ===
[OK] News opportunities scanned and sent
```

---

## 🤖 Automate It (Optional)

Run as Administrator:

```powershell
.\scripts\setup_scheduled_tasks.ps1
```

This creates:
- **Daily**: Mon-Fri at 4:30 PM (fetch data, charts, alerts)
- **Weekly**: Sunday at 6:00 PM (S&P 500 scan)

---

## 📊 Check Results

### Generated Files

```powershell
# View latest data
dir data\market_data\*.csv

# View charts
start charts\breakouts\AAPL.png

# View signals
type signals\daily_alerts.json
```

### Logs

```powershell
# Real-time monitoring
Get-Content logs\daily_workflow.log -Wait -Tail 20

# View last 50 lines
Get-Content logs\daily_workflow.log -Tail 50
```

---

## 📱 Telegram

You should receive a message like:

```
🚨 DAILY TRADING ALERTS 🚨

Total Alerts: 3
  🟢 BUY: 2
  🔴 SELL: 1

High Confidence: ⭐⭐⭐ 2

━━━━━━━━━━━━━━━━━━━━

📈 AAPL - BUY SIGNAL
Strategy: RSI + MACD
Confidence: ⭐⭐⭐ HIGH
...
```

---

## 🛠️ Individual Commands

```powershell
# Activate virtual environment first
.\venv\Scripts\Activate.ps1

# Then run individual scripts
python src\fetch_daily_prices.py
python scripts\send_daily_alerts.py
python scripts\send_news_opportunities.py
python scripts\scan_sp500_news.py --top 10

# Analyze specific symbol
python scripts\analyze_symbol.py NVDA
```

---

## ⏰ Schedule Summary

If you set up Task Scheduler:

| When | What |
|------|------|
| Mon-Fri 4:30 PM | Fetch data |
| Mon-Fri 4:35 PM | Generate charts |
| Mon-Fri 4:40 PM | Send trading alerts |
| Mon-Fri 4:45 PM | Scan news |
| Sunday 12:00 PM | Update correlations |
| Sunday 6:00 PM | S&P 500 scan |

---

## 🔍 Verify Scheduled Tasks

```powershell
# List tasks
Get-ScheduledTask | Where-Object {$_.TaskName -like "*Market*"}

# Check last run
Get-ScheduledTask -TaskName "Daily Market Automation" | Get-ScheduledTaskInfo

# Test run manually
Start-ScheduledTask -TaskName "Daily Market Automation"
```

---

## 📚 Need More Help?

- **Complete Guide**: `LOCAL_SETUP_WINDOWS.md`
- **macOS/Linux**: `LOCAL_SETUP_GUIDE.md`
- **Config Help**: `QUICKSTART_CONFIG.md`
- **Project Overview**: `README.md`

---

## ✅ You're All Set!

Your Windows 11 machine is now:
- ✅ Fetching market data daily
- ✅ Generating technical analysis charts
- ✅ Running 5 trading strategies
- ✅ Sending Telegram alerts
- ✅ Scanning news for opportunities
- ✅ Tracking insider trading
- ✅ Learning from correlations

**Enjoy automated trading insights!** 📈🚀

