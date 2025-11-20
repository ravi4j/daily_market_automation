# Initial Bulk Fetch Guide

## Overview

To enable intelligent symbol selection based on trading volume, we need historical data for ALL ~23,888 US symbols. This is a **ONE-TIME** overnight process.

## Why Do This?

**Problem**: Major stocks like NVDA, ORCL, TSLA were missing from scans because they didn't have CSV files.

**Solution**:
1. Download 2 years of data for ALL symbols ONCE (overnight)
2. Daily scanner updates incrementally (only fetches latest day - FAST!)
3. Sort by volume from CSV first row (INSTANT!)

## Step 1: Initial Bulk Fetch (ONE-TIME, ~6-8 hours)

```bash
# Activate virtual environment
source .venv/bin/activate  # macOS/Linux
# or
.venv\Scripts\activate     # Windows

# Run bulk fetch (overnight)
python scripts/initial_bulk_fetch.py
```

This will:
- Download 2 years of data for ~23,888 symbols
- Save to `data/market_data/stocks/` and `data/market_data/etfs/`
- Take 6-8 hours with rate limiting (1 call/second to Yahoo Finance)
- Use ~500 MB disk space

### Resume After Interruption

If the script gets interrupted, you can resume:

```bash
python scripts/initial_bulk_fetch.py --resume
```

This will skip symbols that already have CSVs.

## Step 2: Daily Updates (FAST, ~2-5 minutes)

After the initial bulk fetch, daily updates are FAST because we only fetch the latest day:

```bash
# Run daily scanner (incremental updates built-in)
python scripts/master_daily_scan.py --mode daily
```

The scanner automatically:
1. Sorts symbols by volume (reads first row of existing CSVs)
2. Selects top 600 intelligent candidates
3. Updates CSVs incrementally (only fetches new data)
4. Performs deep analysis on candidates

## How Volume-Based Sorting Works

1. **Read first row**: Each CSV is sorted descending (newest first), so first row = latest volume
2. **Sort symbols**: Place high-volume symbols (NVDA, AAPL, TSLA) at the top
3. **Select top 600**: Intelligent selector picks from top of sorted list
4. **Zero-volume symbols**: Symbols without CSVs get volume=0, placed at end

## Expected Results

After bulk fetch:

✅ **NVDA** (19,776 → Top 10) - High volume stock now prioritized
✅ **ORCL** (14,836 → Top 50) - Large-cap stocks now included
✅ **AAPL** (22,267 → Top 5) - Major stocks always scanned
✅ All S&P 500, NASDAQ-100, high-volume stocks included

## Monitoring Progress

The script saves progress every 100 symbols:
```bash
cat data/metadata/bulk_fetch_progress.txt
```

## GitHub Actions

After bulk fetch completes locally, commit the CSVs:

```bash
git add data/market_data/
git commit -m "Initial bulk fetch: 23,888 symbols with 2y data"
git push
```

GitHub Actions will then handle daily incremental updates automatically.

## Disk Space

- Initial: ~500 MB (23,888 CSVs × 2 years × ~20 KB each)
- Growth: ~2-3 MB per day (incremental)
- Cleanup: Old data (>2 years) can be purged periodically

## FAQ

**Q: Why not use market cap from Finnhub?**
A: Would take 23,888 API calls (6+ hours) and hit rate limits. Volume from CSVs is instant and reflects actual trading activity.

**Q: What if a symbol fails to fetch?**
A: It's skipped and gets volume=0 (placed at end). The pre-screening will try to fetch it again during daily runs.

**Q: Can I run this in the background?**
A: Yes! Use `nohup` or `screen`:
```bash
nohup python scripts/initial_bulk_fetch.py > bulk_fetch.log 2>&1 &
```

**Q: How often should I run bulk fetch?**
A: Only ONCE! Daily scanner handles incremental updates automatically.

## Next Steps

After bulk fetch completes:
1. Test the scanner: `python scripts/master_daily_scan.py --mode daily`
2. Verify NVDA, ORCL are now detected: Check `signals/master_scan_results.json`
3. Commit CSVs to GitHub
4. Sit back and enjoy intelligent, volume-based symbol selection! 🚀
