# Data Directory Structure

This directory contains all data files for the Daily Market Automation system.

## 📁 Structure

```
data/
├── market_data/          # Historical OHLCV price data (CSV files)
├── metadata/             # S&P 500 lists, SQLite databases, configurations
└── cache/                # Temporary cache files (24h expiry)
```

## 📊 Subdirectories

### `market_data/`
Contains CSV files with historical price data for each symbol.

**Format**: `{SYMBOL}.csv`

**Example**:
- `AAPL.csv` - Apple historical data
- `TQQQ.csv` - ProShares UltraPro QQQ data
- `NVDA.csv` - NVIDIA historical data

**Columns**:
- Date (index)
- Open, High, Low, Close, Volume

**Git**: ✅ Committed to repository (incremental updates)

---

### `metadata/`
Contains metadata files, SQLite databases, and configuration data.

**Files**:
- `sp500_symbols.json` - Complete S&P 500 list with sectors
- `sp500_comprehensive.txt` - Fallback comprehensive list
- **`news_correlation.db`** - SQLite database for historical news correlation tracking

#### 🗄️ SQLite Database

##### `news_correlation.db`
**Purpose**: Tracks historical news events and price movements to predict rebound probability

**Location**: `data/metadata/news_correlation.db`

**Tables**:
1. **news_events** - Historical news events
   - Columns: symbol, date, headline, sentiment, category, drop_pct
   
2. **price_movements** - Price movements after news events
   - Columns: event_id, days_after, price_change_pct, outcome
   
3. **correlations** - Aggregated patterns
   - Columns: category, sentiment, avg_rebound_pct, success_rate, sample_size

**Size**: Grows over time (~1-10 MB typical)

**Backup**: ⚠️ Important! Contains valuable historical correlation data

**Git**: ✅ **Committed** to repository (contains valuable learning data)

---

### `cache/`
Temporary cache files for API responses.

**Files**:
- `finnhub_fundamentals_{SYMBOL}.json` - Cached fundamentals (24h)
- `finnhub_insider_{SYMBOL}.json` - Cached insider data (24h)
- `auto_analysis_cache.json` - Auto-analysis cooldown tracking

**Git**: ❌ Ignored (not committed)

---

## 🗄️ SQLite Database Details

### Accessing `news_correlation.db`

**Python:**
```python
from src.news_correlation import NewsCorrelationTracker

tracker = NewsCorrelationTracker()
# Database automatically created at data/metadata/news_correlation.db

# Query correlations
correlations = tracker.get_correlations()
for corr in correlations:
    print(f"{corr.category}: {corr.success_rate*100:.1f}% success")
```

**SQLite CLI:**
```bash
# Open database
sqlite3 data/metadata/news_correlation.db

# List tables
.tables

# View events
SELECT * FROM news_events LIMIT 10;

# View correlations (sorted by success rate)
SELECT category, sentiment, success_rate, sample_size 
FROM correlations 
ORDER BY success_rate DESC;

# Exit
.quit
```

**Database Browser:**
- Download: https://sqlitebrowser.org/
- Open: `data/metadata/news_correlation.db`
- Browse tables, run queries, export data

---

## 🔧 File Management

### Backup Important Files
```bash
# Backup everything
cp -r data/ data_backup/

# Backup just the database
cp data/metadata/news_correlation.db data/metadata/news_correlation.db.backup
```

### Cleanup Cache
```bash
# Safe to delete - regenerates automatically
rm -rf data/cache/*
```

### Update Commands
```bash
# Fetch symbol data
python scripts/fetch_symbol_data.py NVDA

# Update S&P 500 list
python scripts/fetch_sp500_list.py

# Update news correlations
python scripts/update_news_correlations.py
```

---

## 📈 Data Sources

| Data Type | Source | File/DB |
|-----------|--------|---------|
| Price Data | Yahoo Finance | `market_data/*.csv` |
| S&P 500 List | Finnhub/Wikipedia | `metadata/sp500_symbols.json` |
| Fundamentals | Finnhub API | Cache (24h) |
| Insider Data | Finnhub API | Cache (24h) |
| News | Yahoo Finance | Not stored |
| Correlations | Self-learning | `metadata/news_correlation.db` |

---

## 💾 Directory Sizes (Typical)

| Directory | Size | Files | Notes |
|-----------|------|-------|-------|
| market_data/ | 5-50 MB | 4-500 CSVs | Depends on symbols & history |
| metadata/ | 1-15 MB | 3-5 files | SQLite DB grows over time |
| cache/ | 50-500 KB | Varies | Auto-cleaned after 24h |

**SQLite DB Growth**:
- Week 1: ~100 KB
- Month 1: ~1 MB
- Year 1: ~5-10 MB
- Year 2+: ~10-20 MB

---

## 🛠️ Troubleshooting

### View Database Stats
```bash
sqlite3 data/metadata/news_correlation.db "
SELECT 
    (SELECT COUNT(*) FROM news_events) as total_events,
    (SELECT COUNT(*) FROM price_movements) as total_movements,
    (SELECT COUNT(*) FROM correlations) as total_patterns;
"
```

### Database Locked Error
```bash
# Close all connections
pkill -f news_correlation

# Or wait a few seconds and retry
```

### Corrupted Database
```bash
# Backup first!
cp data/metadata/news_correlation.db data/metadata/news_correlation.db.backup

# Check integrity
sqlite3 data/metadata/news_correlation.db "PRAGMA integrity_check;"

# If corrupted, rebuild from git
git checkout data/metadata/news_correlation.db
```

### Optimize Database
```bash
# Reclaim space
sqlite3 data/metadata/news_correlation.db "VACUUM;"

# Update statistics for better query performance
sqlite3 data/metadata/news_correlation.db "ANALYZE;"
```

---

## 🔒 Security & Privacy

✅ **Safe for Public Repos**: Contains only:
- Public market data
- Public news headlines  
- Statistical correlations

❌ **No Sensitive Data**:
- No API keys
- No personal information
- No proprietary data

The SQLite database can be safely committed to GitHub.

---

## 📚 Related Documentation

- [`NEWS_CORRELATION_QUICKSTART.md`](../NEWS_CORRELATION_QUICKSTART.md) - Using correlation data
- [`src/news_correlation.py`](../src/news_correlation.py) - Implementation details
- [`scripts/update_news_correlations.py`](../scripts/update_news_correlations.py) - Update script

---

**SQLite Database Location**: `data/metadata/news_correlation.db` ✅
