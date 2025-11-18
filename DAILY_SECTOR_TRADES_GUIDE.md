# 🎯 Daily Sector Trades - Complete Guide

## 🚀 **What This Does**

**Identifies the BEST 1-2 trades per sector DAILY** using a sophisticated multi-signal scoring system:

- 📰 **News Sentiment (30%)** - Recent news and price drops
- 📊 **Technical Analysis (40%)** - RSI, MACD, Bollinger Bands, Volume, Trend
- 💼 **Fundamentals (20%)** - P/E ratio, Profit margins, Analyst ratings
- 🏢 **Insider Activity (10%)** - Corporate insider buying/selling

**Result**: Top-ranked trades across all sectors with complete trade setups!

---

## 🎓 **Scoring System Explained**

### **Composite Score = Weighted Average**

```
Total Score (0-100) = 
    News Sentiment     × 30% +
    Technical Analysis × 40% +
    Fundamentals       × 20% +
    Insider Activity   × 10%
```

### **1. News Sentiment (30%)**

**What it checks:**
- Recent news headlines (negative news = opportunity)
- 5-day price change (bigger drop = higher score)
- Sentiment analysis (FinBERT if enabled)

**Example:**
```
AAPL drops -5.2% on supply chain concerns
News Score: 75/100 (good buying opportunity)
```

### **2. Technical Analysis (40%) - MOST IMPORTANT**

**What it checks:**

| Indicator | Points | Good Signal |
|-----------|--------|-------------|
| **RSI** | 20 | RSI < 30 (oversold) = 20 pts |
| **MACD** | 20 | Bullish crossover = 20 pts |
| **Bollinger Bands** | 20 | Near lower band = 20 pts |
| **Volume** | 15 | Volume > 1.5x average = 15 pts |
| **Trend** | 15 | Price above SMA20 & SMA50 = 15 pts |
| **ADX** | 10 | ADX > 25 (strong trend) = 10 pts |

**Example:**
```
NVDA Technical Analysis:
- RSI: 28 (oversold) → +20 pts
- MACD: Bullish crossover → +20 pts
- Near BB lower band → +20 pts
- Volume 1.8x average → +15 pts
- Price above SMAs → +15 pts
- ADX 28 → +10 pts
Total: 100/100 (perfect technical setup!)
```

### **3. Fundamentals (20%)**

**What it checks:**

| Metric | Points | Good Signal |
|--------|--------|-------------|
| **P/E Ratio** | 5 | 10 < P/E < 30 (reasonable) |
| **Profit Margins** | 5 | > 15% (strong) |
| **Analyst Rating** | 5 | Buy or Strong Buy |
| **Distance from 52W High** | 5 | > 20% below (room to grow) |

**Example:**
```
MSFT Fundamentals:
- P/E: 28 (reasonable) → +5 pts
- Profit Margins: 35% → +5 pts
- Analysts: Strong Buy → +5 pts
- 25% below 52W high → +5 pts
Total: 100/100
```

### **4. Insider Activity (10%)**

**What it checks:**
- Insider buying/selling in last 3 months
- Transaction size and frequency
- Sentiment: STRONG_BUY, BUY, NEUTRAL, SELL, STRONG_SELL

**Example:**
```
AAPL Insider Activity:
- 3 executives bought $5M in shares
- Sentiment: STRONG_BUY
Insider Score: 100/100
```

---

## 📊 **Score Interpretation**

| Total Score | Confidence | Recommendation | Action |
|-------------|------------|----------------|--------|
| **80-100** | ⭐⭐⭐ HIGH | **STRONG BUY** | High priority, enter position |
| **60-79** | ⭐⭐ MEDIUM | **BUY** | Good opportunity, consider |
| **40-59** | ⭐ LOW | **WATCH** | Monitor, wait for better setup |
| **< 40** | - | **SKIP** | Not qualified |

---

## 🎯 **Example Output**

### **Daily Telegram Alert:**

```
🎯 DAILY SECTOR TRADES
November 18, 2024

10 trades across 5 sectors
━━━━━━━━━━━━━━━━━━━━

🏢 Technology

1. NVDA - NVIDIA Corporation ⭐⭐⭐
   Score: 88/100 | STRONG BUY
   Price: $485.00

   Signals:
   📰 News: Supply chain concerns (temporary)
   📊 RSI oversold (28)
   📊 MACD bullish crossover
   📊 Near BB lower band (15%)
   💼 Strong margins (25%)
   🏢 Strong insider buying

   📊 RSI 28 | MACD ✓ | Vol 1.8x

   Trade Setup:
   Entry: $485.00
   Stop: $475.00
   Target: $505.00
   R:R = 1:2.0

2. AMD - Advanced Micro Devices ⭐⭐
   Score: 72/100 | BUY
   Price: $125.00

   [Similar format...]
━━━━━━━━━━━━━━━━━━━━

🏢 Healthcare

1. JNJ - Johnson & Johnson ⭐⭐⭐
   Score: 78/100 | STRONG BUY
   Price: $155.00

   [Similar format...]
━━━━━━━━━━━━━━━━━━━━

💡 Daily Trading Strategy:
• Review top 1-2 from each sector
• Focus on HIGH confidence (⭐⭐⭐)
• Diversify across sectors
• Set stop losses immediately
```

---

## 🚀 **Usage**

### **Basic Usage:**

```bash
# Find best 2 trades per sector
python scripts/daily_sector_trades.py

# Find only 1 trade per sector (more selective)
python scripts/daily_sector_trades.py --max-per-sector 1

# Minimum score 70 (only high-quality trades)
python scripts/daily_sector_trades.py --min-score 70

# Specific sectors only
python scripts/daily_sector_trades.py --sectors Technology Healthcare
```

### **Output Files:**

1. **`signals/daily_sector_trades.json`** - Complete results with all scores
2. **Telegram Alert** - Formatted message with top trades

---

## 📅 **Daily Workflow**

### **Morning Routine:**

```bash
# 7:00 AM - Pre-market gaps
python scripts/send_premarket_alerts.py

# What you get:
# - Gap protection (your positions)
# - Gap opportunities (new trades)
```

### **After Market Close:**

```bash
# 4:30 PM - Update data
python src/fetch_daily_prices.py  # Fast (<2 min)

# 5:00 PM - Scan for tomorrow's trades
python scripts/daily_sector_trades.py

# What you get:
# - Top 1-2 trades per sector
# - Complete trade setups
# - Entry/Stop/Target prices
```

### **Evening Review:**

1. Check Telegram alerts
2. Review top trades (focus on ⭐⭐⭐)
3. Select 3-5 trades across different sectors
4. Plan entries for tomorrow
5. Set alerts at entry prices

---

## 💡 **How to Use the Results**

### **Strategy 1: High Confidence Only**

```
Filter: Only ⭐⭐⭐ (HIGH confidence)
Target: 3-5 trades total
Diversification: 1 per sector maximum

Example Daily Picks:
✅ NVDA (Technology) - 88/100
✅ JNJ (Healthcare) - 78/100
✅ JPM (Financial Services) - 80/100

Result: 3 high-quality trades, 3 different sectors
```

### **Strategy 2: Sector Rotation**

```
Week 1: Focus on top 2 sectors
Week 2: Rotate to next 2 sectors
Week 3: Rotate again

Example:
Week 1: Technology + Healthcare
Week 2: Financials + Energy
Week 3: Industrials + Consumer

Result: Balanced exposure over time
```

### **Strategy 3: Score-Based Position Sizing**

```
Score 80-100: 3% of portfolio
Score 70-79:  2% of portfolio
Score 60-69:  1% of portfolio

Example ($10,000 portfolio):
NVDA (88): $300 position
AMD (72):  $200 position
AAPL (65): $100 position

Result: Risk-adjusted position sizing
```

---

## 🔍 **Understanding the Signals**

### **Technical Signals Explained:**

**"RSI oversold (28)"**
- RSI below 30 = oversold condition
- Stock may be due for bounce
- Good entry point

**"MACD bullish crossover"**
- MACD line crossed above signal line
- Momentum turning positive
- Bullish signal

**"Near BB lower band (15%)"**
- Price is 15% into Bollinger Band range
- Near lower support level
- Often bounces from here

**"High volume (1.5x avg)"**
- Trading volume 50% above average
- Increased interest/conviction
- More likely to move

**"Strong uptrend (above SMAs)"**
- Price above 20-day and 50-day moving averages
- Clear uptrend intact
- Follow the trend

---

## 📈 **Real-World Example**

### **Scenario: Monday Evening Analysis**

**You run the scanner:**
```bash
python scripts/daily_sector_trades.py
```

**Top 3 Results:**

```
1. NVDA (Technology) - 88/100 ⭐⭐⭐
   Entry: $485, Stop: $475, Target: $505
   Signals: RSI oversold, MACD crossover, insider buying

2. JNJ (Healthcare) - 78/100 ⭐⭐⭐
   Entry: $155, Stop: $152, Target: $161
   Signals: Regulatory concerns temporary, strong fundamentals

3. JPM (Financials) - 76/100 ⭐⭐
   Entry: $145, Stop: $142, Target: $151
   Signals: Interest rate concerns, but oversold
```

**Your Decision:**
- Pick all 3 (diversified across sectors)
- Capital allocation: $1,000 per trade
- Total risk: $30 + $30 + $30 = $90 (3%)

**Tuesday Morning:**
- Set buy limit orders at entry prices
- Set stop loss orders immediately after fill
- Set target limit orders

**Result (2 weeks later):**
- NVDA: Hit target (+4.1%) = +$41
- JNJ: Hit target (+3.9%) = +$39
- JPM: Stopped out (-2.1%) = -$21
- Net: +$59 (+5.9% on capital)

**Win rate: 66% (2 out of 3)**
**Risk/Reward: Excellent**

---

## 🎓 **Advanced Tips**

### **Tip 1: Combine Multiple Scans**

```bash
# Morning: Gap opportunities
python scripts/send_premarket_alerts.py

# Afternoon: News opportunities
python scripts/send_news_opportunities.py

# Evening: Daily sector trades
python scripts/daily_sector_trades.py

# Compare: Look for symbols that appear in multiple scans!
```

If NVDA appears in:
- ✅ Gap down opportunity (pre-market)
- ✅ News opportunity (afternoon)
- ✅ Daily sector trade (evening)

**= TRIPLE CONFIRMATION! Very strong signal!**

### **Tip 2: Track Your Success by Sector**

```
Week 1-4 Results:
Technology: 8 wins / 12 trades = 67% win rate
Healthcare: 6 wins / 8 trades = 75% win rate
Financials: 4 wins / 8 trades = 50% win rate

Adjustment: Focus more on Healthcare, less on Financials
```

### **Tip 3: Use Score Thresholds**

```bash
# Conservative (only best trades)
python scripts/daily_sector_trades.py --min-score 75

# Moderate (default)
python scripts/daily_sector_trades.py --min-score 60

# Aggressive (more trades, lower quality)
python scripts/daily_sector_trades.py --min-score 50
```

### **Tip 4: Sector Focus Days**

```
Monday: Scan all sectors, identify best performing
Tuesday: Focus on top 3 sectors only
Wednesday: Scan all sectors again
Thursday: Focus on previously skipped sectors
Friday: Review week, prepare for next week
```

---

## 🔧 **Configuration**

### **Adjust Component Weights:**

Edit `scripts/daily_sector_trades.py` line ~267:

```python
# Default weights
composite_score = (
    news_score * 0.30 +        # News: 30%
    tech_score * 0.40 +        # Technical: 40%
    fundamental_score * 0.20 + # Fundamentals: 20%
    insider_score * 0.10       # Insider: 10%
)

# Example: More weight on technicals
composite_score = (
    news_score * 0.20 +        # News: 20%
    tech_score * 0.50 +        # Technical: 50%
    fundamental_score * 0.20 + # Fundamentals: 20%
    insider_score * 0.10       # Insider: 10%
)
```

### **Adjust Minimum Threshold:**

Line ~365:
```python
# Default: minimum 40 score
if trade and trade['total_score'] >= 40:

# More selective: minimum 60 score
if trade and trade['total_score'] >= 60:
```

---

## 📊 **JSON Output Format**

**`signals/daily_sector_trades.json`:**

```json
{
  "date": "2024-11-18",
  "timestamp": "2024-11-18T17:00:00",
  "total_trades": 10,
  "sectors_covered": 5,
  "trades": [
    {
      "symbol": "NVDA",
      "sector": "Technology",
      "company_name": "NVIDIA Corporation",
      "total_score": 88.0,
      "confidence": "HIGH",
      "recommendation": "STRONG BUY",
      
      "news_score": 75.0,
      "technical_score": 100.0,
      "fundamental_score": 85.0,
      "insider_score": 75.0,
      
      "signals": [
        "📰 News: Supply chain concerns (temporary)",
        "📊 RSI oversold (28)",
        "📊 MACD bullish crossover",
        "📊 Near BB lower band (15%)",
        "💼 Strong margins (25%)",
        "🏢 Strong insider buying"
      ],
      
      "current_price": 485.00,
      "entry": 485.00,
      "stop": 475.00,
      "target": 505.00,
      "risk_reward": 2.0,
      
      "rsi": 28.0,
      "macd_bullish": true,
      "volume_ratio": 1.8
    }
  ]
}
```

---

## 🎯 **Integration with Existing Features**

### **Works With:**

1. ✅ **Pre-Market Gap Monitor**
   - Morning: Gap opportunities
   - Evening: Daily sector trades
   - Compare: Look for overlap

2. ✅ **News Scanner**
   - Uses same NewsMonitor
   - Adds technical + fundamental scoring
   - More complete analysis

3. ✅ **Insider Tracker**
   - Includes insider data in scoring
   - 10% weight in composite score

4. ✅ **Auto-Add Portfolio**
   - Can auto-add high-score trades
   - Ensures sector diversification

---

## ✅ **Prerequisites**

Before running daily_sector_trades.py:

1. ✅ Symbol metadata fetched
   ```bash
   python scripts/fetch_symbol_metadata.py --sp500
   ```

2. ✅ Historical data available
   ```bash
   python scripts/fetch_initial_sector_data.py --period 2y
   ```

3. ✅ Daily data updated
   ```bash
   python src/fetch_daily_prices.py
   ```

4. ✅ Environment variables set
   ```bash
   export TELEGRAM_BOT_TOKEN='your_token'
   export TELEGRAM_CHAT_ID='your_chat_id'
   export FINNHUB_API_KEY='your_key'  # Optional for insider data
   ```

---

## 🎉 **Summary**

**What You Get:**
✅ Best 1-2 trades per sector DAILY
✅ Multi-signal scoring (News + Technical + Fundamental + Insider)
✅ Complete trade setups (Entry/Stop/Target)
✅ Confidence ratings (HIGH/MEDIUM/LOW)
✅ Telegram alerts with all details
✅ JSON export for tracking

**Benefits:**
- 🎯 **Focused Picks** - Only the best from each sector
- 🏢 **Diversified** - Spread across sectors
- 📊 **Data-Driven** - Multiple signals combined
- ⚡ **Automated** - Runs daily after market close
- 📱 **Convenient** - Telegram delivery

**Next Steps:**
1. Run your first scan tonight!
2. Review results tomorrow morning
3. Paper trade for 2 weeks
4. Track win rate by sector
5. Start real trading with small size

---

**Questions? Issues?**

See [README.md](README.md) or [SECTOR_SCANNING_QUICKSTART.md](SECTOR_SCANNING_QUICKSTART.md)

**Happy Trading! Find the best, skip the rest! 🎯📈**

