# 📊 ETF-Only Trading - Quick Start Guide

## 🎯 **What This Does**

**Scans ONLY ETFs** (no individual stocks) for best daily opportunities!

**Why ETFs?**
- ✅ Lower risk (diversified)
- ✅ No earnings surprises
- ✅ More predictable patterns
- ✅ Better for technical analysis
- ✅ Smoother price action

---

## ⚡ **5-Minute Setup**

### **Step 1: Fetch ETF Metadata**

```bash
# Option A: Recommended daily trading ETFs (8 ETFs)
python scripts/fetch_symbol_metadata.py --symbols SPY QQQ XLK XLF XLE IWM TQQQ SQQQ

# Option B: All 11 sector ETFs
python scripts/fetch_symbol_metadata.py --symbols XLK XLV XLF XLE XLI XLY XLP XLU XLRE XLB XLC

# Option C: Your leveraged favorites
python scripts/fetch_symbol_metadata.py --symbols TQQQ SQQQ UPRO SPXU TNA TZA
```

### **Step 2: Fetch Historical Data**

```bash
# Fetch 2 years of data (ONE TIME)
python scripts/fetch_initial_sector_data.py --period 2y
```

### **Step 3: Run Daily ETF Scanner**

```bash
# Scan recommended ETFs (default)
python scripts/daily_etf_trades.py

# Or scan specific ETFs
python scripts/daily_etf_trades.py --etfs SPY QQQ TQQQ

# Or scan all sector ETFs
python scripts/daily_etf_trades.py --category recommended_sector_rotation
```

---

## 📊 **What You Get**

```
📊 DAILY ETF TRADES
ETFs Only - No Individual Stocks
November 18, 2024

8 ETF trades across 4 categories
━━━━━━━━━━━━━━━━━━━━

📊 Technology

1. XLK ⭐⭐⭐
   Score: 88/100 | STRONG BUY
   Price: $185.00
   
   Signals:
   📊 RSI oversold (32)
   📊 MACD bullish crossover
   📊 High volume (1.7x)
   
   Trade Setup:
   Entry: $185.00
   Stop: $182.00
   Target: $191.00
   R:R = 1:2.0

📊 3x Long Nasdaq

1. TQQQ ⭐⭐⭐
   Score: 85/100 | STRONG BUY
   Price: $65.50
   [Similar format...]

💡 ETF Trading Strategy:
• Focus on HIGH confidence (⭐⭐⭐)
• Diversify across categories
• Lower risk than individual stocks
• Leveraged ETFs (3x) = SHORT-TERM only!
```

---

## 🎯 **ETF Categories Available**

### **1. Recommended Daily Trading (Default)**
```bash
python scripts/daily_etf_trades.py
```
**ETFs**: SPY, QQQ, XLK, XLF, XLE, IWM, TQQQ, SQQQ
**Why**: Most liquid, tightest spreads, best for daily trading

### **2. Sector Rotation (11 sectors)**
```bash
python scripts/daily_etf_trades.py --category recommended_sector_rotation
```
**ETFs**: XLK, XLV, XLF, XLE, XLI, XLY, XLP, XLU, XLRE, XLB, XLC
**Why**: Pure sector exposure, rotate based on strength

### **3. Leveraged Long (3x)**
```bash
python scripts/daily_etf_trades.py --category leveraged_long
```
**ETFs**: TQQQ, UPRO, TNA, UDOW, TECL, FAS
**Why**: 3x returns on bullish moves (SHORT-TERM only!)

### **4. Leveraged Short (3x Inverse)**
```bash
python scripts/daily_etf_trades.py --category leveraged_short
```
**ETFs**: SQQQ, SPXU, TZA, SDOW, TECS, FAZ
**Why**: Profit from market declines, hedging

### **5. Index ETFs**
```bash
python scripts/daily_etf_trades.py --category index_etfs
```
**ETFs**: SPY, QQQ, IWM, DIA, VOO, VTI
**Why**: Broad market exposure, lower volatility

### **6. Conservative (Lower Risk)**
```bash
python scripts/daily_etf_trades.py --category conservative
```
**ETFs**: SPY, XLU, XLP, VTI
**Why**: Defensive sectors, lower volatility

### **7. Aggressive (Higher Risk)**
```bash
python scripts/daily_etf_trades.py --category aggressive
```
**ETFs**: TQQQ, SQQQ, UPRO, SPXU, TNA, QQQ
**Why**: Higher volatility, bigger moves

---

## 💡 **Common Commands**

```bash
# Scan recommended ETFs (default)
python scripts/daily_etf_trades.py

# Scan specific ETFs
python scripts/daily_etf_trades.py --etfs SPY QQQ TQQQ SQQQ

# Scan all sector ETFs
python scripts/daily_etf_trades.py --category recommended_sector_rotation

# Scan ALL ETFs from universe (~60 ETFs)
python scripts/daily_etf_trades.py --all

# High quality only (score >= 70)
python scripts/daily_etf_trades.py --min-score 70

# More trades per category
python scripts/daily_etf_trades.py --max-per-category 3
```

---

## 🎓 **ETF Trading Strategies**

### **Strategy 1: Sector Rotation**
```
Use sector ETFs to rotate into strong sectors:

Daily Scan Results:
1. XLK (Technology) - 88/100 ⭐⭐⭐
2. XLE (Energy) - 82/100 ⭐⭐⭐
3. XLV (Healthcare) - 75/100 ⭐⭐

Action: Buy top 2 sectors (XLK, XLE)
Hold for: 1-2 weeks
Exit when: New scan shows other sectors stronger
```

### **Strategy 2: Leveraged ETF Day Trading**
```
Your TQQQ/SQQQ are PERFECT for this!

TQQQ (3x Nasdaq Long):
- When: QQQ or XLK score > 75
- Entry: At opening bell
- Stop: 3% below entry (tight!)
- Target: 5-10% gain (same day or next day)
- Hold: 1-3 days maximum

SQQQ (3x Nasdaq Short):
- When: Market showing weakness
- Use as hedge when market score < 40
```

### **Strategy 3: Index ETF Swing Trading**
```
SPY, QQQ, IWM for longer holds:

Entry: Score > 80
Hold: 1-2 weeks
Stop: 2-3% below entry
Target: 5-8% gain

Lower volatility = Can use larger position size
```

---

## 📈 **Real Example: Today's Scan**

```bash
# Run the scanner
python scripts/daily_etf_trades.py
```

**Results:**
```
Top 3 ETF Trades:

1. XLK (Technology) - 88/100 ⭐⭐⭐
   Entry: $185, Stop: $182, Target: $191
   
2. TQQQ (3x Nasdaq) - 85/100 ⭐⭐⭐
   Entry: $65.50, Stop: $64.00, Target: $68.50
   
3. SPY (S&P 500) - 78/100 ⭐⭐⭐
   Entry: $452, Stop: $448, Target: $460
```

**Your Decision:**
- Pick all 3 (diversified)
- $1,000 per trade = $3,000 total
- Risk: 2% per trade = $60 total

**Next Morning (9:30 AM):**
```
Buy 5 XLK @ $185
Buy 15 TQQQ @ $65.50
Buy 2 SPY @ $452

Set stops immediately:
XLK stop @ $182
TQQQ stop @ $64.00
SPY stop @ $448
```

---

## ⚠️ **Important ETF Rules**

### **1. Leveraged ETFs Decay Over Time**
```
TQQQ, SQQQ, etc. have DAILY reset
✅ Good for: 1-3 days (short-term)
❌ Bad for: Weeks to months (long-term)

Example:
Day 1: QQQ +1%, TQQQ +3% ✓
Day 2: QQQ -1%, TQQQ -3% ✓
Day 3: QQQ +1%, TQQQ +3% ✓
Net: QQQ +1.03%, TQQQ +2.73% (not 3x!)

Decay happens over time!
```

### **2. ETF Position Sizing**
```
Individual Stock: 1-2% risk per trade
Regular ETF: 2-3% risk per trade (lower volatility)
Leveraged 3x ETF: 1% risk per trade (3x moves!)

Example ($10,000 account):
XLK: Risk $200 (2%)
SPY: Risk $200 (2%)
TQQQ: Risk $100 (1%) ← Only 1% due to 3x leverage
```

### **3. Best Times to Trade ETFs**
```
Market Open (9:30-10:00 AM): ✅ Good liquidity
Mid-Day (10:00-3:00 PM): ⚠️  Lower volume
Market Close (3:30-4:00 PM): ✅ Good liquidity

Avoid: First 5 minutes (wild swings)
Best: 9:35-10:00 AM and 3:30-3:55 PM
```

---

## 📊 **ETF Universe**

All ETFs are configured in `config/etf_universe.yaml`:

**Sector ETFs (11):** XLK, XLV, XLF, XLE, XLI, XLY, XLP, XLU, XLRE, XLB, XLC
**Index ETFs (6):** SPY, QQQ, IWM, DIA, VOO, VTI
**Leveraged Long (6):** TQQQ, UPRO, TNA, UDOW, TECL, FAS
**Leveraged Short (6):** SQQQ, SPXU, TZA, SDOW, TECS, FAZ

**Total: ~60 ETFs available**

---

## 🚀 **Daily Routine**

```
Morning (7-9 AM):
→ Pre-market gap alerts (automatic)

After Market Close (4:30 PM):
→ Update data (automatic)

Evening (5:00 PM):
→ Run ETF scanner
python scripts/daily_etf_trades.py

→ Check Telegram alert
→ Select top 3-5 ETFs (⭐⭐⭐)
→ Plan tomorrow's entries

Next Morning (9:30 AM):
→ Execute planned ETF trades
→ Set stop losses IMMEDIATELY
```

---

## 💡 **Why ETFs Are Better**

| Factor | Individual Stocks | ETFs |
|--------|------------------|------|
| **Risk** | High (single company) | Lower (20-100 stocks) |
| **Earnings** | Can gap 10-20% | N/A (no earnings) |
| **Volatility** | High | Moderate |
| **Predictability** | Low | Higher |
| **Technical Analysis** | Works sometimes | Works better |
| **After-Hours Risk** | High | Lower |
| **Sector Exposure** | One company | Entire sector |

**Bottom Line: ETFs are more predictable and lower risk!**

---

## 📁 **Output Files**

```
signals/
└── daily_etf_trades.json    # Your ETF scan results

Example:
{
  "date": "2024-11-18",
  "total_trades": 8,
  "categories_covered": 4,
  "trades": [
    {
      "symbol": "XLK",
      "sector": "Technology",
      "total_score": 88.0,
      "entry": 185.00,
      "stop": 182.00,
      "target": 191.00
    }
  ]
}
```

---

## ✅ **Quick Test**

```bash
# 1. Fetch metadata for your favorites
python scripts/fetch_symbol_metadata.py --symbols TQQQ SQQQ SPY QQQ

# 2. View their details
cat data/metadata/symbol_metadata.csv | grep -E "TQQQ|SQQQ|SPY|QQQ"

# 3. Run ETF scanner
python scripts/daily_etf_trades.py --etfs TQQQ SQQQ SPY QQQ

# 4. Check results
cat signals/daily_etf_trades.json
```

---

## 🎉 **Summary**

**✅ NEW: ETF-Only Scanner Ready!**

- [x] 60+ ETFs configured
- [x] Multiple categories (sector, index, leveraged)
- [x] Same multi-signal scoring system
- [x] Complete trade setups
- [x] Telegram alerts
- [x] JSON exports

**Benefits:**
- 📊 Lower risk than stocks
- 🎯 More predictable patterns
- ⚡ No earnings surprises
- 🏢 Pure sector exposure
- 💰 Better for technical trading

**Your favorites work great:**
- ✅ TQQQ (3x Nasdaq Long)
- ✅ SQQQ (3x Nasdaq Short)

---

**Run it tonight and get your first ETF-only picks! 📊📈💰**

