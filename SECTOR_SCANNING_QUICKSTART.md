# 🎯 Sector-Based Scanning - Quick Start Guide

## 🚀 **What This Does**

This new system gives you:
1. 📊 **Symbol Metadata** - Exchange, sector, industry for each symbol
2. 📥 **Fast Initial Fetch** - Download 2 years of data ONCE
3. ⚡ **Incremental Updates** - Daily updates take < 2 minutes (only today's data)
4. 🏢 **Sector Scanning** - Find 1-2 opportunities per sector (diversified portfolio)

---

## ⚡ **Quick Start (5 Minutes)**

### **Step 1: Fetch Symbol Metadata**

```bash
# Option A: Your portfolio symbols (from config/symbols.yaml)
python scripts/fetch_symbol_metadata.py

# Option B: All S&P 500 symbols
python scripts/fetch_symbol_metadata.py --sp500

# Option C: Specific symbols
python scripts/fetch_symbol_metadata.py --symbols AAPL MSFT NVDA GOOGL
```

**Output**: `data/metadata/symbol_metadata.csv`

**Example:**
```csv
symbol,company_name,exchange,sector,industry,market_cap
AAPL,Apple Inc.,NMS,Technology,Consumer Electronics,2800000000000
MSFT,Microsoft Corporation,NMS,Technology,Software - Infrastructure,2300000000000
TQQQ,ProShares UltraPro QQQ,NGM,Unknown,Unknown,0
```

**What you get:**
- ✅ US Exchange info (NMS=NASDAQ, NYQ=NYSE, etc.)
- ✅ GICS Sector classification
- ✅ Industry sub-classification
- ✅ Market cap, country, currency
- ✅ Quote type (EQUITY, ETF, INDEX)

---

### **Step 2: Fetch Initial Historical Data**

```bash
# Fetch 2 years of data (ONE TIME, ~10-15 min for 500 stocks)
python scripts/fetch_initial_sector_data.py --period 2y

# Or fetch 1 year only (faster)
python scripts/fetch_initial_sector_data.py --period 1y
```

**Output**: `data/market_data/*.csv` (one CSV per symbol)

**Example Output:**
```
================================================================================
INITIAL SECTOR DATA FETCHER
================================================================================

📋 Loading symbol metadata...
✅ Loaded metadata for 503 symbols

🔍 Fetching 2y of historical data...
================================================================================

📊 Found 11 sectors
================================================================================

🏢 Technology (72 symbols)
------------------------------------------------------------
   📥 AAPL: Fetching 2y of data...
   ✅ AAPL: Saved 504 rows
   📥 MSFT: Fetching 2y of data...
   ✅ MSFT: Saved 504 rows
   ...

🏢 Healthcare (64 symbols)
------------------------------------------------------------
   📥 JNJ: Fetching 2y of data...
   ✅ JNJ: Saved 504 rows
   ...

================================================================================
SUMMARY
================================================================================
✅ Successfully fetched: 498 symbols
❌ Failed: 5 symbols
```

---

### **Step 3: Scan by Sector**

```bash
# Find top 2 opportunities per sector (diversified)
python scripts/scan_by_sector.py --max-per-sector 2

# Or specific sectors only
python scripts/scan_by_sector.py --sectors Technology Healthcare Financials

# Or find only 1 per sector
python scripts/scan_by_sector.py --max-per-sector 1
```

**Output**: `signals/sector_opportunities.json` + Telegram alert

**Example Telegram Alert:**
```
🎯 SECTOR OPPORTUNITIES
Diversified across 5 sectors

Total: 10 opportunities
━━━━━━━━━━━━━━━━━━━━

🏢 Technology

1. NVDA - NVIDIA Corporation
   Score: 88/100
   Price: $485.00
   Drop: -5.2%
   Reason: Supply chain concerns

2. AMD - Advanced Micro Devices
   Score: 82/100
   Price: $125.00
   Drop: -4.8%
   Reason: Earnings miss
━━━━━━━━━━━━━━━━━━━━

🏢 Healthcare

1. JNJ - Johnson & Johnson
   Score: 78/100
   Price: $155.00
   Drop: -3.5%
   Reason: Regulatory concerns

2. PFE - Pfizer Inc.
   Score: 75/100
   Price: $28.50
   Drop: -6.2%
   Reason: Drug trial results
━━━━━━━━━━━━━━━━━━━━

💡 Diversification Strategy:
• Pick 1-2 from each sector
• Spread risk across industries
• Monitor daily for changes
```

---

## 📊 **Daily Updates (FAST!)**

After initial setup, daily updates are **incremental** (only today's data):

```bash
# Your existing daily fetch (now uses metadata!)
python src/fetch_daily_prices.py

# Takes < 2 minutes (vs 15 minutes if fetching all history)
```

**How it works:**
1. Reads last date from each CSV
2. Only fetches data from last date → today
3. Appends to existing CSV
4. ✅ **10x faster!**

---

## 🎯 **Use Cases**

### **Use Case 1: Your Current Portfolio**

```bash
# Current symbols: TQQQ, AAPL, UBER, SP500, SQQQ

# 1. Fetch metadata
python scripts/fetch_symbol_metadata.py

# 2. View their exchanges and sectors
cat data/metadata/symbol_metadata.csv

# Output:
# TQQQ - NGM (NASDAQ Global Market) - ETF
# AAPL - NMS (NASDAQ) - Technology
# UBER - NYQ (NYSE) - Technology
# ^GSPC - Unknown (INDEX)
# SQQQ - NGM (NASDAQ Global Market) - ETF
```

### **Use Case 2: Scan All S&P 500 by Sector**

```bash
# 1. Fetch S&P 500 list (if not already done)
python scripts/fetch_sp500_list.py

# 2. Fetch metadata for all 500
python scripts/fetch_symbol_metadata.py --sp500

# 3. Fetch 2y of historical data (ONE TIME)
python scripts/fetch_initial_sector_data.py --period 2y

# 4. Scan for opportunities (2 per sector)
python scripts/scan_by_sector.py --max-per-sector 2

# Result: ~20 opportunities across 11 sectors
```

### **Use Case 3: Diversify Your Portfolio**

```bash
# Current: Only Technology stocks (AAPL, UBER, TQQQ)
# Goal: Add Healthcare, Financials, Energy

# 1. Scan specific sectors
python scripts/scan_by_sector.py --sectors Healthcare "Financial Services" Energy

# 2. Review opportunities
cat signals/sector_opportunities.json

# 3. Pick 1-2 from each sector
# Example result:
#   Technology: AAPL (existing)
#   Healthcare: JNJ (new)
#   Financials: JPM (new)
#   Energy: XOM (new)
```

---

## 📍 **US Exchange Codes**

| Code | Exchange | Description |
|------|----------|-------------|
| **NMS** | NASDAQ National Market | Main NASDAQ (AAPL, MSFT, GOOGL) |
| **NGM** | NASDAQ Global Market | NASDAQ tier (ETFs like TQQQ) |
| **NYQ** | NYSE | New York Stock Exchange (JPM, XOM) |
| **PCX** | NYSE Arca | ETFs and options |
| **BTS** | NASDAQ Capital Market | Smaller NASDAQ tier |

---

## 🏢 **GICS Sectors (11 Total)**

The system classifies stocks into these standard sectors:

1. **Technology** - Software, hardware, semiconductors
2. **Healthcare** - Pharmaceuticals, biotech, equipment
3. **Financial Services** - Banks, insurance, investment
4. **Communication Services** - Telecom, media, entertainment
5. **Consumer Cyclical** - Retail, autos, leisure
6. **Industrials** - Aerospace, machinery, transportation
7. **Consumer Defensive** - Food, beverages, household
8. **Energy** - Oil & gas, renewable energy
9. **Utilities** - Electric, water, gas utilities
10. **Real Estate** - REITs, development
11. **Basic Materials** - Chemicals, metals, mining

---

## 💡 **Pro Tips**

### **Tip 1: Update Metadata Weekly**

```bash
# Refresh metadata once per week (market caps, sectors can change)
python scripts/fetch_symbol_metadata.py --sp500 --force
```

### **Tip 2: Sector Rotation Strategy**

```bash
# Week 1: Scan all sectors
python scripts/scan_by_sector.py --max-per-sector 2

# Week 2: Focus on best performing sectors
python scripts/scan_by_sector.py --sectors Technology Healthcare --max-per-sector 3
```

### **Tip 3: Combine with Other Scanners**

```bash
# 1. News scanner (price drops)
python scripts/send_news_opportunities.py

# 2. Sector scanner (diversification)
python scripts/scan_by_sector.py

# 3. Pre-market scanner (gaps)
python scripts/send_premarket_alerts.py

# Result: 3 different opportunity sources!
```

### **Tip 4: Filter by Market Cap**

Edit `scripts/scan_by_sector.py` to add market cap filter:

```python
# In scan_sector function, add this filter:
symbols_with_mcap = metadata_df[
    (metadata_df['sector'] == sector) & 
    (metadata_df['market_cap'] > 10_000_000_000)  # > $10B
]['symbol'].tolist()
```

---

## 🚀 **Complete Workflow**

### **Initial Setup (ONE TIME)**

```bash
# 1. Fetch S&P 500 symbols
python scripts/fetch_sp500_list.py

# 2. Fetch metadata (exchange, sector, industry)
python scripts/fetch_symbol_metadata.py --sp500

# 3. Fetch 2 years of historical data
python scripts/fetch_initial_sector_data.py --period 2y

# Total time: ~15-20 minutes for 500 stocks
```

### **Daily Routine**

```bash
# Morning (7 AM)
python scripts/send_premarket_alerts.py  # Gap protection + opportunities

# After market close (4:30 PM)
python src/fetch_daily_prices.py         # Fast incremental update (< 2 min)
python scripts/scan_by_sector.py         # Find diversified opportunities

# Evening
# Review Telegram alerts, make trading plan for tomorrow
```

---

## 📁 **File Structure**

```
daily_market_automation/
├── data/
│   ├── metadata/
│   │   ├── symbol_metadata.csv       # NEW! Exchange, sector, industry
│   │   ├── sp500_symbols.json        # S&P 500 list
│   │   └── sp500_comprehensive.txt
│   ├── market_data/
│   │   ├── AAPL.csv                  # Historical OHLCV data
│   │   ├── MSFT.csv
│   │   └── ... (one per symbol)
│   └── cache/                        # Finnhub cache
├── scripts/
│   ├── fetch_symbol_metadata.py      # NEW! Fetch metadata
│   ├── fetch_initial_sector_data.py  # NEW! Initial data fetch
│   ├── scan_by_sector.py             # NEW! Sector scanner
│   ├── fetch_sp500_list.py           # S&P 500 list fetcher
│   └── send_news_opportunities.py    # News scanner
├── signals/
│   └── sector_opportunities.json     # NEW! Scan results
└── config/
    └── symbols.yaml                  # Your portfolio
```

---

## 🎓 **Advanced: Add Sector to Existing Scanners**

You can enhance your news scanner to show sectors:

```python
# In scripts/send_news_opportunities.py
# Load metadata
metadata_df = pd.read_csv('data/metadata/symbol_metadata.csv')

# Add sector to each opportunity
for opp in opportunities:
    sector_row = metadata_df[metadata_df['symbol'] == opp['symbol']]
    if not sector_row.empty:
        opp['sector'] = sector_row.iloc[0]['sector']
```

---

## ❓ **Troubleshooting**

### **Problem: "Metadata file not found"**

```bash
# Solution: Run metadata fetcher first
python scripts/fetch_symbol_metadata.py --sp500
```

### **Problem: "No data for symbol XYZ"**

Some symbols may not have data:
- Delisted stocks
- Very new IPOs
- Index symbols (like ^GSPC)

**Solution**: Skip them or filter out

### **Problem: "Sector showing as Unknown"**

- ETFs and Indexes don't have sectors
- Some small stocks may not have sector data

**Solution**: This is normal, they're filtered in sector scanning

---

## 🎉 **Summary**

**You now have:**
✅ Symbol metadata (exchange, sector, industry) cached locally
✅ Fast initial data fetch (ONE TIME)
✅ Super-fast daily updates (< 2 minutes)
✅ Sector-based opportunity scanner
✅ Diversified portfolio management (1-2 per sector)

**Benefits:**
- 🚀 **10x faster** daily updates
- 🏢 **Sector diversification** built-in
- 📊 **Exchange info** for all symbols
- 🎯 **No missed opportunities** across sectors

---

**Questions? Issues?**

See [README.md](README.md) or open a GitHub issue!

**Happy Sector Scanning! Diversify and conquer! 📈💰**

