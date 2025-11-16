# Data Directory Structure

Organized data storage for the Daily Market Automation system.

---

## 📁 Directory Structure

```
data/
├── market_data/       # Daily OHLCV price data (CSV files)
├── metadata/          # Reference data (S&P 500 lists, symbols)
├── cache/             # Temporary cached data (API responses, fundamentals)
└── README.md          # This file
```

---

## 📊 market_data/

**Purpose:** Historical and daily OHLCV (Open, High, Low, Close, Volume) price data

**Contents:**
- `AAPL.csv` - Apple Inc. daily prices
- `TQQQ.csv` - ProShares UltraPro QQQ daily prices
- `SP500.csv` - S&P 500 Index daily prices
- `UBER.csv` - Uber Technologies daily prices
- `SQQQ.csv` - ProShares UltraPro Short QQQ daily prices
- Additional symbol CSV files...

**Format:**
```csv
Date,Open,High,Low,Close,Volume
2024-01-01,150.25,152.30,149.80,151.50,1000000
```

**Updated by:**
- `src/fetch_daily_prices.py` - Daily incremental updates
- `.github/workflows/daily-fetch.yml` - Automated via GitHub Actions

---

## 📋 metadata/

**Purpose:** Reference data and static lists

**Contents:**
- `sp500_symbols.json` - Current S&P 500 constituent list with sectors
- `sp500_comprehensive.txt` - Fallback S&P 500 list (331 stocks)

**Format (sp500_symbols.json):**
```json
{
  "last_updated": "2024-11-15T16:56:00",
  "count": 503,
  "symbols": [
    {
      "symbol": "AAPL",
      "company": "Apple Inc.",
      "sector": "Information Technology"
    }
  ]
}
```

**Updated by:**
- `scripts/fetch_sp500_list.py` - Fetches from Finnhub/Wikipedia
- `.github/workflows/weekly-sp500-scan.yml` - Weekly updates

---

## 💾 cache/

**Purpose:** Temporary cached data to reduce API calls

**Contents:**
- `fundamentals_*.json` - Cached fundamental data (24h TTL)
- `sp500_list.json` - Cached S&P 500 list (7 days TTL)
- Other temporary cache files...

**TTL (Time-to-Live):**
- Fundamentals: 24 hours
- S&P 500 list: 7 days

**Managed by:**
- `src/finnhub_data.py` - DataCache class
- Automatic cleanup on expiration

**Note:** This directory is in `.gitignore` - cache is not committed to Git

---

## 🔄 Migration from Old Structure

**Old Structure:**
```
data/
├── AAPL.csv
├── TQQQ.csv
├── sp500_symbols.json
└── ...
```

**New Structure:**
```
data/
├── market_data/
│   ├── AAPL.csv
│   └── TQQQ.csv
├── metadata/
│   └── sp500_symbols.json
└── cache/
    └── (temporary files)
```

**All scripts have been updated to use new paths automatically.**

---

## 🛠️ Maintenance

### Clean Cache
```bash
# Remove all cached data
rm -rf data/cache/*
```

### Update S&P 500 List
```bash
# Fetch latest S&P 500 constituents
python scripts/fetch_sp500_list.py
```

### Verify Data Integrity
```bash
# Check all CSV files
for file in data/market_data/*.csv; do
  echo "Checking $file..."
  head -n 1 "$file"
  tail -n 1 "$file"
done
```

---

## 📏 Size Guidelines

**Expected Sizes:**
- Each CSV file: ~200KB (15 years of daily data)
- sp500_symbols.json: ~40KB
- cache/ total: < 10MB (auto-cleaned)

---

## 🔒 .gitignore Rules

```gitignore
# Ignore cache directory
data/cache/*
!data/cache/.gitkeep

# Keep structure but ignore large CSVs (optional)
# data/market_data/*.csv
```

---

## 🚀 Quick Reference

| Directory | Purpose | Updated By | Committed to Git |
|-----------|---------|------------|------------------|
| `market_data/` | Daily prices | fetch_daily_prices.py | ✅ Yes |
| `metadata/` | Reference lists | fetch_sp500_list.py | ✅ Yes |
| `cache/` | Temporary cache | finnhub_data.py | ❌ No |

---

**Last Updated:** November 16, 2024

