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
- 📧 **Email Notifications** - Optional daily summary emails
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
│   ├── fetch_daily_prices.py  # Main market data fetching script
│   └── common/           # Shared utilities for future scripts
├── tests/                # Test files
│   └── test_incremental.py
├── scripts/              # Helper scripts
│   └── setup.sh          # Automated setup script
├── data/                 # CSV output files
│   ├── AAPL.csv
│   ├── TQQQ.csv
│   ├── SP500.csv
│   └── UBER.csv
├── docs/                 # Documentation
│   └── architecture.md
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
Create this file at `.github/workflows/daily.yml` (already included here):
```yaml
name: Fetch Daily Prices
on:
  schedule:
    - cron: "35 0 * * 1-5"   # 00:35 UTC ≈ 6:35 PM America/Chicago (M-F)
  workflow_dispatch: {}
jobs:
  fetch:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install -r requirements-fetch.txt
      - run: python src/fetch_daily_prices.py
      - name: Commit updated data
        run: |
          git config user.name "automation-bot"
          git config user.email "bot@example.com"
          git add data/*.csv
          git commit -m "Update daily data" || echo "No changes"
          git push
```
> Requires a GitHub repository with proper permissions (write access for the workflow, or a PAT).

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

## 4) Testing

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
