# Daily Market Automation

Automated daily OHLCV (Open, High, Low, Close, Volume) data fetcher for multiple stock symbols with intelligent incremental updates.

## ⚡ TL;DR - Quick Setup on New Machine

```bash
# 1. Clone repo
git clone <your-repo-url>
cd daily_market_automation

# 2. Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements-fetch.txt

# 4. Run!
python src/fetch_daily_prices.py

# Data will be in data/*.csv
```

That's it! Run daily to get incremental updates (2-5 seconds).

## 🎯 Features

- ✨ **Incremental Fetching** - Only downloads NEW data (2-5 seconds vs 20-30 seconds)
- 🛡️ **Smart Error Handling** - No crashes on weekends/holidays/market closures
- 📊 **Multiple Symbols** - TQQQ, S&P 500 (^GSPC), AAPL, UBER (easily add more)
- 🔄 **Auto-Retry** - Automatic retry logic for transient network errors
- 📈 **Breakout Detection** - Identifies trendline violations, S/R breaks, and reversal points
- 🎯 **Technical Analysis** - Support/resistance levels, swing highs/lows, trend direction
- 🎯 **Trading Signals** - JSON/CSV exports (NO PASSWORDS NEEDED, safe for public repos!)
- 📱 **Multi-Platform Access** - Consume signals from anywhere (Python, shell, curl, Google Sheets)
- 🤖 **GitHub Actions Automation** - Daily data fetch, chart generation, and signal exports
- 🏗️ **Production Ready** - Organized structure for multiple automation scripts

## 📈 Tracked Symbols

- `TQQQ` - ProShares UltraPro QQQ (3x leveraged NASDAQ-100)
- `^GSPC` - S&P 500 Index
- `AAPL` - Apple Inc.
- `UBER` - Uber Technologies Inc.

All data is stored as CSV files in the `data/` directory.

## 📁 Project Structure

```
daily_market_automation/
├── .github/
│   └── workflows/         # GitHub Actions workflows
├── src/                   # Source code
│   ├── fetch_daily_prices.py  # Market data fetching script
│   ├── detect_breakouts.py    # Breakout detection & analysis
│   ├── visualize_breakouts.py # Chart generation with trendlines
│   ├── export_signals.py      # Trading signal export (JSON/CSV)
│   └── common/           # Shared utilities for future scripts
├── charts/                # Generated chart images (PNG, committed & regenerated daily)
├── tests/                # Test files
│   └── test_incremental.py
├── scripts/              # Helper scripts
│   ├── setup.sh          # Automated setup script
│   ├── fetch_signals.py  # Fetch signals from GitHub (no auth!)
│   ├── view_signals.sh   # View signals in terminal
│   └── send_telegram_signals.py  # Send signals to Telegram
├── data/                 # CSV output files & signals
│   ├── AAPL.csv
│   ├── TQQQ.csv
│   ├── SP500.csv
│   ├── UBER.csv
│   ├── trading_signals.json  # Daily trading signals (detailed)
│   └── trading_signals.csv   # Daily trading signals (simple)
├── docs/                 # Documentation
│   ├── architecture.md
│   ├── breakout-confirmation.md
│   ├── workflows.md
│   └── telegram-setup.md
├── requirements-*.txt    # Python dependencies
└── README.md
```

## 1) Quick Start (Fresh Installation)

### Step 1: Clone the Repository
```bash
# Clone the repository
git clone <your-repo-url>
cd daily_market_automation
```

### Step 2: Setup Virtual Environment (Keeps Everything Local)
```bash
# Create a local virtual environment in .venv folder
python3 -m venv .venv

# Activate it
source .venv/bin/activate   # macOS/Linux
# .venv\Scripts\activate    # Windows
```

> 💡 All packages will be installed locally in `.venv/` folder inside your project - nothing system-wide!

### Step 3: Install Dependencies

We use organized requirements files for different purposes:

**For running the fetch script (recommended):**
```bash
pip install -r requirements-fetch.txt
```

**For development (includes testing, linting, formatting):**
```bash
pip install -r requirements-dev.txt
```

**Just the base dependencies (pandas, numpy, pytz):**
```bash
pip install -r requirements-base.txt
```

### Step 4: Run the Script
```bash
python src/fetch_daily_prices.py
```

You should see:
- Log messages showing data fetching progress
- CSV files created/updated in `data/` directory (TQQQ.csv, SP500.csv, AAPL.csv, UBER.csv)

### 🚀 Quick Setup Script (One Command)

Alternatively, use the automated setup script:

```bash
# Make script executable
chmod +x scripts/setup.sh

# Run setup (creates venv, installs dependencies)
./scripts/setup.sh

# Then just run the fetch script
source .venv/bin/activate
python src/fetch_daily_prices.py
```

### First Run vs Subsequent Runs

**First Run (No existing data):**
- Downloads ~15 years of historical data for all symbols
- Takes ~20-30 seconds
- Creates CSV files in `data/` directory

**Subsequent Runs (Incremental):**
- Only fetches NEW data since last run
- Takes ~2-5 seconds (much faster!)
- Updates existing CSV files

**Weekend/Holiday Runs:**
- Detects no new data available
- Reports "CSV is up to date"
- Exits successfully (no errors)

## 📦 Requirements Files Structure

- **`requirements-base.txt`** - Common dependencies (pandas, numpy, pytz)
- **`requirements-fetch.txt`** - For `src/fetch_daily_prices.py` (includes base + yfinance)
- **`requirements-dev.txt`** - Development tools (pytest, black, flake8, mypy)

## 2) Set It to Run Daily

### Option A — macOS/Linux (cron)
Open crontab:
```bash
crontab -e
```
Schedule run **daily at 6:30pm America/Chicago** (after U.S. market close):
```cron
30 18 * * * /usr/bin/env bash -lc 'cd /mnt/data/daily_market_automation && . .venv/bin/activate && python src/fetch_daily_prices.py >> fetch.log 2>&1'
```
> Tip: `date` and `timedatectl` can confirm your system's timezone. Adjust time if needed.

### Option B — Windows (Task Scheduler)
1. Open **Task Scheduler** → **Create Basic Task...**
2. Trigger: Daily at **6:30 PM**.
3. Action: **Start a program** → `Program/script`: `python`
   **Add arguments**: `src\fetch_daily_prices.py`
   **Start in**: full folder path of this project.
4. (Optional) Use a venv by pointing `Program/script` to the `python.exe` inside `.venv\Scripts`

### Option C — GitHub Actions (runs in the cloud)

This project includes **two automated workflows**:

#### 1. Data Fetching (`.github/workflows/daily-fetch.yml`)
Runs daily to fetch latest market data:

```yaml
name: Fetch Daily Prices
on:
  schedule:
    - cron: "35 0 * * 1-5"   # 00:35 UTC ≈ 6:35 PM America/Chicago (M-F)
  workflow_dispatch: {}      # Manual trigger
```

**What it does:**
- Fetches latest OHLCV data for all symbols
- Updates CSV files in `data/` directory
- Commits and pushes changes automatically
- Runs Monday-Friday after market close

#### 2. Chart Generation (`.github/workflows/daily-charts.yml`)
Runs automatically **after** data fetch completes:

```yaml
name: Generate Daily Charts
on:
  workflow_run:
    workflows: ["Fetch Daily Prices"]
    types: [completed]
  workflow_dispatch: {}      # Manual trigger
```

**What it does:**
- Generates visual breakout charts (includes analysis)
- Creates PNG charts in `charts/` directory
- Commits and pushes chart images
- Uploads charts as workflow artifacts (30-day retention)
- Only runs if fetch workflow succeeded

**Note**: The chart generation script (`visualize_breakouts.py`) includes the breakout analysis, so no separate detection step is needed.

#### Setup Requirements:
1. **Repository Settings** → **Actions** → **General**
   - Enable "Allow GitHub Actions to create and approve pull requests"
   - Workflow permissions: "Read and write permissions"
2. Push workflows to your repository
3. Enable workflows in the Actions tab

#### Manual Triggers:
```bash
# Trigger fetch workflow manually
gh workflow run daily-fetch.yml

# Trigger chart generation manually
gh workflow run daily-charts.yml
```

#### View Results:
- **Code tab**: See updated CSV files in `data/` and charts in `charts/`
- **Charts**: Committed to repo and viewable directly on GitHub (regenerated daily)
- **Actions tab**: View workflow runs and download chart artifacts
- **Artifacts**: Charts also available as workflow artifacts (30-day retention)

## 3) Optional Email Summary
Copy `.env.example` to `.env` and fill values, or set these environment variables before running:
```
SMTP_HOST=
SMTP_PORT=587
SMTP_USER=
SMTP_PASS=
SMTP_TO=
```
The script will send a simple summary like:
```
TQQQ: 2025-11-07  AdjClose=xx.xx  Close=yy.yy
SP500: 2025-11-07  AdjClose=aa.aa  Close=bb.bb
```

## 4) Breakout Detection

### Analyze Market Breakouts

The project includes a powerful breakout detection script that identifies:
- **Trendline Violations** - Breakouts above/below support/resistance trendlines
- **Support/Resistance Breaks** - Price breaking through key S/R levels
- **Reversal Points** - Price near previous swing highs/lows

```bash
# Activate virtual environment
source .venv/bin/activate

# Run breakout analysis
python src/detect_breakouts.py
```

### What It Detects

**🔹 Trendline Analysis:**
- Uses linear regression on recent highs/lows
- Identifies uptrends vs downtrends
- Detects bullish/bearish trendline breakouts

**🔹 Support/Resistance Analysis:**
- Calculates S/R from 20-day highs/lows
- Measures distance from current price to S/R levels
- Alerts when price breaks through resistance or support

**🔹 Reversal Point Analysis:**
- Identifies swing highs and lows (local peaks/troughs)
- Detects when price is near previous reversal points
- Signals potential trend reversals

### Example Output

```
================================================================================
📊 TQQQ - 2025-11-10
================================================================================
Current Price: $110.03 | Volume: 29,818,811

🔹 TRENDLINE ANALYSIS:
   Trend Direction: 📈 UPTREND
   Support Trendline: $113.49
   Resistance Trendline: $117.47
   🚨 BREAKOUT DETECTED: BEARISH_TRENDLINE_BREAKOUT

🔹 SUPPORT/RESISTANCE ANALYSIS:
   Support: $97.07 (13.35% away)
   Resistance: $121.37 (9.34% away)

🔹 REVERSAL POINT ANALYSIS:
   Latest Swing High: $121.37
   Latest Swing Low: $96.83
   ⚠️  NEAR_PREVIOUS_HIGH at $109.66

================================================================================
📋 SUMMARY
================================================================================
🚨 BREAKOUTS DETECTED:
   • TQQQ: BEARISH_TRENDLINE_BREAKOUT
```

### Customize Detection Parameters

Edit `src/detect_breakouts.py` to adjust:

```python
LOOKBACK_DAYS = 60               # Analysis period (default: 60 days)
SUPPORT_RESISTANCE_WINDOW = 20   # S/R calculation window (default: 20 days)
BREAKOUT_THRESHOLD = 0.02        # Breakout threshold (default: 2%)

# Confirmation Filters (see docs/breakout-confirmation.md for details)
CONFIRMATION_CONFIG = {
    'percentage_threshold': 0.02,   # 2% move required
    'point_threshold': 2.0,          # $2 move required
    'multiple_closes': 1,            # Consecutive closes needed
    'time_bars': 1,                  # Bars to confirm
    'volume_multiplier': 1.2,        # Volume surge (1.2x average)
}
```

### Confirmation Filters

The system uses **6 sophisticated filters** to validate breakouts and reduce false signals:

1. **✅ Intrabar Close** - Close must be beyond level (not just wick)
2. **✅ Multiple Closes** - N consecutive closes required
3. **✅ Time/Bar Confirmation** - Sustained for N bars
4. **✅ Percentage Move** - Minimum % threshold
5. **✅ Point Move** - Minimum $ threshold
6. **✅ Volume Surge** - Above average volume

**Scoring:** Breakout is **CONFIRMED** if 4+ out of 6 filters pass (66% threshold)

📚 **See detailed documentation:** `docs/breakout-confirmation.md`

### Add More Symbols

The system **automatically discovers** all CSV files in the `data/` directory!

#### Method 1: Auto-Discovery (Default - Recommended) ✅

Simply add new CSV files to `data/` folder:

```bash
# Add new symbol data
python src/fetch_daily_prices.py  # Will fetch all configured symbols

# Analysis automatically includes all CSV files
python src/detect_breakouts.py    # Auto-discovers: AAPL, SP500, TQQQ, UBER, etc.
python src/visualize_breakouts.py # Creates charts for all discovered symbols
```

**Benefits:**
- ✅ No code changes needed
- ✅ Automatically analyzes all available data
- ✅ Easy to add/remove symbols (just add/delete CSV files)
- ✅ Scales automatically

#### Method 2: Hardcode Specific Symbols (Optional)

If you want to analyze only specific symbols, edit `src/detect_breakouts.py`:

```python
# Around line 24-28
# Comment out auto-discovery:
# SYMBOLS = None

# Uncomment and customize:
SYMBOLS = ["TQQQ", "AAPL"]  # Only analyze these
```

#### Method 3: Add Symbols to Fetch Script

To add new symbols to fetch, edit `src/fetch_daily_prices.py`:

```python
# Around line 33
SYMBOLS = {
    "TQQQ": "TQQQ",
    "SP500": "^GSPC",
    "AAPL": "AAPL",
    "UBER": "UBER",
    "TSLA": "TSLA",     # Add Tesla
    "NVDA": "NVDA",     # Add Nvidia
    "MSFT": "MSFT",     # Add Microsoft
}
```

Then fetch data:
```bash
python src/fetch_daily_prices.py
# Creates: data/TSLA.csv, data/NVDA.csv, data/MSFT.csv

# Analysis automatically picks them up!
python src/detect_breakouts.py  # Now includes 7 symbols
```

### Visualize Breakouts with Charts

Create visual charts showing trendlines, support/resistance levels, and breakout alerts:

```bash
# Generate charts for all symbols
python src/visualize_breakouts.py
```

**Charts include:**
- 📊 Candlestick price action
- 📈 Support and resistance trendlines (linear regression)
- 🔵 Horizontal support level
- 🔴 Horizontal resistance level
- 🔺 Swing high markers (red triangles)
- 🔻 Swing low markers (green triangles)
- 🚨 Breakout alert annotations
- 📊 Price info and statistics

**Charts are saved to:** `charts/SYMBOL_breakout.png`

Example:
- `charts/TQQQ_breakout.png`
- `charts/SP500_breakout.png`
- `charts/AAPL_breakout.png`
- `charts/UBER_breakout.png`

> 📌 **Note:** Charts are **committed to the repository** and **regenerated daily** by GitHub Actions. You can view the latest charts directly in the repo or download them as workflow artifacts.

### Combined Analysis Workflow

```bash
# 1. Fetch latest data
python src/fetch_daily_prices.py

# 2. Option A: Text-based analysis only
python src/detect_breakouts.py

# 2. Option B: Generate visual charts (includes analysis)
python src/visualize_breakouts.py

# 3. View charts
open charts/TQQQ_breakout.png
```

**Note**: `visualize_breakouts.py` automatically performs the breakout analysis, so you don't need to run both scripts unless you want the text output from `detect_breakouts.py`.

## 5) Trading Signal Exports 🎯

### Overview

The **Trading Signal Export** system generates structured JSON/CSV files with confirmed breakouts - **NO PASSWORDS OR SECRETS REQUIRED**! Perfect for public repos.

**Why This is Better Than Email/Slack:**
- ✅ **No credentials needed** - Safe for public repositories
- ✅ **Programmatic access** - JSON/CSV ready for automation
- ✅ **Git history** - Track signals over time
- ✅ **Multi-platform** - Consume from anywhere with HTTP
- ✅ **Free & unlimited** - No API rate limits
- ✅ **Automated daily updates** - GitHub Actions generates signals

### Generate Signals

```bash
# Activate virtual environment
source .venv/bin/activate

# Generate trading signals
python src/export_signals.py
```

**Output Files:**
- `data/trading_signals.json` - Detailed signals with confirmation scores
- `data/trading_signals.csv` - Simple tabular format

### Signal Format

**JSON Structure:**
```json
{
  "summary": {
    "generated_at": "2025-11-10T17:30:00",
    "total_symbols_analyzed": 4,
    "confirmed_breakouts": 2,
    "buy_signals": 1,
    "sell_signals": 1,
    "watch_signals": 0
  },
  "signals": [
    {
      "symbol": "TQQQ",
      "signal": "SELL",
      "breakout_type": "BEARISH_TRENDLINE_BREAKOUT_CONFIRMED",
      "price": 110.03,
      "timestamp": "2025-11-10T00:00:00",
      "confirmation_score": 5,
      "filters_passed": {
        "intrabar_close": true,
        "multiple_closes": true,
        "time_bars": true,
        "percentage_move": true,
        "point_move": true,
        "volume_surge": false
      },
      "details": {
        "support": 97.07,
        "resistance": 121.37,
        "trend_direction": "UPTREND",
        "volume": 29818811,
        "volume_ratio": 1.15,
        "swing_high": 121.37,
        "swing_low": 96.83
      },
      "technical_levels": {
        "support_trendline": 113.49,
        "resistance_trendline": 117.47
      }
    }
  ]
}
```

**CSV Format:**
```csv
Symbol,Signal,Price,Breakout,Score,Trend,Volume_Ratio,Timestamp
TQQQ,SELL,110.03,BEARISH_TRENDLINE_BREAKOUT_CONFIRMED,5,UPTREND,1.15,2025-11-10T00:00:00
AAPL,BUY,225.50,RESISTANCE_BREAK_CONFIRMED,6,UPTREND,1.45,2025-11-10T00:00:00
```

### Automated Daily Signal Generation

Signals are **automatically generated daily** by GitHub Actions after market close!

**Workflow:** `daily-charts.yml`
1. Fetches latest market data
2. Generates breakout charts
3. **Exports trading signals** (JSON + CSV)
4. **Commits signals to repo** (viewable on GitHub)
5. Creates workflow summary with signal table

**View on GitHub:**
- Browse: `data/trading_signals.json` directly on GitHub
- Raw URL: `https://raw.githubusercontent.com/YOUR_USERNAME/daily_market_automation/main/data/trading_signals.json`

### Consuming Signals (No Auth Required!)

#### Option 1: Python Script

Use the included consumption script:

```bash
# Fetch signals from your public repo (update repo name first!)
python scripts/fetch_signals.py --repo YOUR_USERNAME/daily_market_automation

# Filter for BUY signals only
python scripts/fetch_signals.py --repo YOUR_USERNAME/daily_market_automation --signal BUY

# High-confidence signals only (score >= 5)
python scripts/fetch_signals.py --repo YOUR_USERNAME/daily_market_automation --min-score 5
```

**Before first use:** Edit `scripts/fetch_signals.py` and replace `your-username` with your GitHub username.

#### Option 2: Shell Script

```bash
# Quick view in terminal
REPO="YOUR_USERNAME/daily_market_automation" ./scripts/view_signals.sh
```

#### Option 3: Direct curl/wget

```bash
# Fetch JSON (works from anywhere, no auth!)
curl -s https://raw.githubusercontent.com/YOUR_USERNAME/daily_market_automation/main/data/trading_signals.json

# With jq for pretty printing
curl -s https://raw.githubusercontent.com/YOUR_USERNAME/daily_market_automation/main/data/trading_signals.json | jq '.signals[]'

# Fetch CSV
curl -s https://raw.githubusercontent.com/YOUR_USERNAME/daily_market_automation/main/data/trading_signals.csv
```

#### Option 4: Google Sheets / Excel

In Google Sheets, use `IMPORTDATA`:
```
=IMPORTDATA("https://raw.githubusercontent.com/YOUR_USERNAME/daily_market_automation/main/data/trading_signals.csv")
```

#### Option 5: Custom Integration

```python
import requests

# Fetch from your public repo (no auth needed!)
url = "https://raw.githubusercontent.com/YOUR_USERNAME/daily_market_automation/main/data/trading_signals.json"
response = requests.get(url)
data = response.json()

# Process signals
for signal in data['signals']:
    if signal['signal'] == 'BUY' and signal['confirmation_score'] >= 5:
        print(f"🟢 Strong BUY: {signal['symbol']} @ ${signal['price']}")
        # Add your logic here: send notification, execute trade, etc.
```

### Signal Types

| Signal | Meaning | Action |
|--------|---------|--------|
| 🟢 **BUY** | Bullish breakout / Resistance break | Consider long position |
| 🔴 **SELL** | Bearish breakout / Support break | Consider short or exit |
| ⚪ **WATCH** | Reversal point / Uncertain | Monitor closely |

### Confirmation Score

Signals include a **confirmation score (0-6)** based on:
1. ✅ Intrabar close confirmation
2. ✅ Multiple consecutive closes
3. ✅ Time/bar sustainability
4. ✅ Percentage move threshold
5. ✅ Point/dollar move threshold
6. ✅ Volume surge confirmation

**Score >= 4** = CONFIRMED breakout (66% filters passed)

### Use Cases

**🔔 Morning Check (Before Market Open):**
```bash
# Quick check for new signals
curl -s https://raw.githubusercontent.com/YOUR/repo/main/data/trading_signals.csv | grep BUY
```

**📱 Mobile/Tablet:**
- Bookmark the raw JSON/CSV URL
- View directly in browser
- Use with iOS Shortcuts for notifications

**🤖 Trading Bots:**
- Poll the JSON URL every N minutes
- Parse signals and execute trades
- No webhook setup needed!

**📊 Spreadsheet Dashboard:**
- Import CSV into Google Sheets
- Add formulas for filtering/alerting
- Auto-refreshes on page load

**💬 Telegram Bot:**
- Simple Python script sends signals to your phone
- No server needed - runs locally or via GitHub Actions
- **Automated via GitHub Actions** - Daily notifications after market close
- See `TELEGRAM_QUICKSTART.md` for 5-minute setup
- See `docs/github-secrets-setup.md` for GitHub automation

**💬 Slack/Discord Bot:**
- Fetch JSON periodically
- Post new signals to channel
- No complex webhooks!

### Files Updated Daily

After GitHub Actions runs:
- ✅ `data/trading_signals.json` - Latest signals (committed to repo)
- ✅ `data/trading_signals.csv` - Latest signals (committed to repo)
- ✅ `charts/*.png` - Latest breakout charts
- ✅ Workflow summary with signal table in Actions tab

### Example Workflow Summary

GitHub Actions creates a nice summary table:

| Symbol | Signal | Price | Score | Volume | Breakout |
|--------|--------|-------|-------|--------|----------|
| 🟢 AAPL | BUY | $225.50 | 6/6 | 1.45x | RESISTANCE_BREAK_CONFIRMED |
| 🔴 TQQQ | SELL | $110.03 | 5/6 | 1.15x | BEARISH_TRENDLINE_BREAKOUT_CONFIRMED |

### Security Note 🔒

**This system is 100% safe for public repos because:**
- No passwords, API keys, or secrets required
- All data is already public (market prices)
- Signals are analysis results, not proprietary data
- Anyone can view your signals (make repo private if concerned)
- No execution - signals are informational only

---

## 6) Testing

### Test Incremental Fetching
To verify that incremental fetching works correctly:

```bash
# Run the test script (it will trim AAPL.csv and backup the original)
python tests/test_incremental.py

# Now run the fetch script - it should only fetch missing days
python src/fetch_daily_prices.py

# Restore original if needed
mv data/AAPL.csv.backup data/AAPL.csv
```

## Notes
- **Incremental Fetching**: Script only downloads NEW data when CSV exists (much faster!)
- CSVs are de-duplicated by date and always keep the latest data for a given day.
- If Yahoo briefly fails, the script auto-retries and logs errors to stdout (or `fetch.log` with cron).
- All automation scripts should be placed in `src/` directory.
- Shared utilities go in `src/common/`.
- See `docs/architecture.md` for more details on project structure.
