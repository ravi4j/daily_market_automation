# How Symbol Ranking Works

## The Problem We Solved

❌ **Before**: Tried to fetch volume for all 23,888 symbols daily
- Yahoo Finance rate limits: ~60 requests/min
- Would take: 23,888 ÷ 60 = 398 minutes = **6.6 hours**
- Hit rate limits, got bad data, missed NVDA/AMD/NFLX

✅ **Now**: Pre-rank symbols nightly, use cached rankings daily
- Nightly job: Ranks all symbols once (runs 2 AM)
- Daily scan: Reads from CSV (instant, no API calls)
- Always includes major stocks (NVDA, AAPL, AMD, etc.)

---

## How It Works

### 1. Base Universe (Curated List)
**File**: `data/metadata/base_universe.txt`

Contains ~100 most important symbols:
- Top tech: AAPL, MSFT, NVDA, TSLA, AMD, GOOGL, AMZN
- Major finance: JPM, V, MA, BAC, GS
- Healthcare: UNH, LLY, JNJ, ABBV
- Major ETFs: SPY, QQQ, IWM, TLT

**Why?** Ensures we always scan the most liquid/important symbols, even if Finnhub is down.

---

### 2. Nightly Ranking Job
**Script**: `scripts/nightly_rank_symbols.py`  
**When**: 2 AM daily (GitHub Action)  
**What it does**:

1. Loads base universe (100 symbols)
2. Fetches additional symbols from Finnhub (up to 500 stocks, 200 ETFs)
3. For each symbol:
   - Fetches 5-day price history (yfinance)
   - Gets volume, market cap, price
4. Ranks by volume (primary) and market cap (secondary)
5. Saves to 2 CSV files:
   - `data/metadata/ranked_stocks.csv`
   - `data/metadata/ranked_etfs.csv`

**Output Example** (`ranked_stocks.csv`):
```csv
symbol,volume,avg_volume,market_cap,price,rank
NVDA,309771315,193471804,4336595501056.0,177.82,1
GOOGL,86571249,37052473,3917544685568.0,323.44,2
TSLA,71460096,89898242,1394848563200.0,419.40,3
AMD,69406159,58700284,335588229120.0,206.13,4
```

**Time**: ~500 symbols × 1 sec = 8 minutes

---

### 3. Daily Scanner Uses Rankings
**Script**: `scripts/master_daily_scan.py`  
**Method**: `_filter_tier_daily()`

**What it does**:
1. Reads `ranked_stocks.csv` and `ranked_etfs.csv`
2. Selects top N symbols:
   - 80% stocks (e.g., 480 out of 600)
   - 20% ETFs (e.g., 120 out of 600)
3. Fetches CSV data ONLY for selected symbols
4. Runs analysis
5. Deletes CSVs (cleanup)

**Why it's fast**:
- ✅ No API calls for volume fetching
- ✅ Reads pre-sorted rankings (instant)
- ✅ Only fetches 600 CSVs (not 23,888)

---

## Testing

### Test Nightly Ranking (20 stocks, 10 ETFs):
```bash
python scripts/nightly_rank_symbols.py --test
```

### Test Daily Scanner (10 symbols):
```bash
python scripts/master_daily_scan.py --test --no-cleanup
```

---

## Results

### Before (Volume-First, No Caching):
- Time: Rate limited after ~100 symbols
- Symbols: MGRT, ALDX (low-volume junk)
- Missed: NVDA, AMD, NFLX (all fell >2% today)

### After (Nightly Rankings):
- Time: Instant (reads CSV)
- Symbols: NVDA, GOOGL, TSLA, AMD, AAPL (top volume)
- Captured: All major fallers

---

## GitHub Actions

### Nightly Ranking
**File**: `.github/workflows/nightly-rank.yml`  
**Schedule**: 2 AM UTC daily  
**What**: Runs `nightly_rank_symbols.py`, commits rankings

### Daily Scan
**File**: `.github/workflows/daily-scan.yml`  
**Schedule**: 10 PM CT (after market close)  
**What**: Runs `master_daily_scan.py` (uses rankings)

---

## Updating Base Universe

To add/remove symbols from base universe:

1. Edit `data/metadata/base_universe.txt`
2. Format: `SYMBOL|type` (e.g., `NVDA|stock`, `SPY|etf`)
3. Commit changes
4. Next nightly job will include your changes

---

## Configuration

**File**: `config/master_config.yaml`

```yaml
scanning:
  max_symbols_per_run: 600  # How many to analyze daily
  
  intelligent_filters:
    min_volume: 500000      # Minimum daily volume
    min_price: 5.0          # Minimum stock price
```

---

## Why This Approach Works

1. **No Rate Limits**: Yahoo Finance sees only 1 request per symbol per night
2. **Fast Daily Scans**: Reads CSV instead of making 23,888 API calls
3. **Always Includes Leaders**: Base universe ensures NVDA, AAPL, etc.
4. **Catches Fallers**: Top volume stocks (where falls matter) always scanned
5. **Configurable**: Change max_symbols in config, no code changes

---

## What Gets Committed

✅ **Committed to Git**:
- `data/metadata/ranked_stocks.csv` (updated nightly)
- `data/metadata/ranked_etfs.csv` (updated nightly)
- `data/metadata/base_universe.txt` (manually updated)

❌ **NOT Committed** (deleted after analysis):
- `data/market_data/stocks/*.csv` (temporary)
- `data/market_data/etfs/*.csv` (temporary)

