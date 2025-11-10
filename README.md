# Daily Market Automation (TQQQ & S&P 500)

This small project fetches **daily OHLCV** data for:
- `TQQQ` (ProShares UltraPro QQQ)
- `^GSPC` (S&P 500 index)

and writes/updates CSVs at `data/TQQQ.csv` and `data/SP500.csv`.

## 1) Quick Start

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python fetch_daily_prices.py
```

You should see files in `data/` after running.

## 2) Set It to Run Daily

### Option A — macOS/Linux (cron)
Open crontab:
```bash
crontab -e
```
Schedule run **daily at 6:30pm America/Chicago** (after U.S. market close):
```cron
30 18 * * * /usr/bin/env bash -lc 'cd /mnt/data/daily_market_automation && . .venv/bin/activate && python fetch_daily_prices.py >> fetch.log 2>&1'
```
> Tip: `date` and `timedatectl` can confirm your system's timezone. Adjust time if needed.

### Option B — Windows (Task Scheduler)
1. Open **Task Scheduler** → **Create Basic Task...**
2. Trigger: Daily at **6:30 PM**.
3. Action: **Start a program** → `Program/script`: `python`  
   **Add arguments**: `fetch_daily_prices.py`  
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
      - run: pip install -r requirements.txt
      - run: python fetch_daily_prices.py
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

## Notes
- CSVs are de-duplicated by date and always keep the latest data for a given day.
- If Yahoo briefly fails, the script auto-retries and logs errors to stdout (or `fetch.log` with cron).
