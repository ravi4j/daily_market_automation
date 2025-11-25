# 🧠 How the Master Scanner Selects Symbols

## Overview

The master scanner uses a **3-phase intelligent selection process** to find the best opportunities from the entire US market:

1. **Universe Fetching** - Get all available symbols
2. **Intelligent Pre-Screening** - Quick filter for promising candidates
3. **Deep Multi-Signal Analysis** - Comprehensive scoring

---

## Phase 1: Universe Fetching

### Data Source: Finnhub API

The scanner fetches **ALL US market symbols** from Finnhub API:

```python
# Fetches from Finnhub:
- All Common Stocks (NYSE, NASDAQ, AMEX)
- All ETFs (Exchange Traded Products)
- Total: ~10,000 symbols
```

### Tiered Approach (Configurable)

You can control how many symbols to scan via `config/master_config.yaml`:

```yaml
scanning:
  strategy:
    tier: "daily"  # Options: daily, weekly, monthly, full
```

**Tier Options:**

| Tier | Symbols | Description | Scan Time |
|------|---------|-------------|-----------|
| **daily** | ~600 | S&P 500 + Top 100 ETFs | ~5 min |
| **weekly** | ~2,000 | Russell 2000 + All sector ETFs | ~20 min |
| **monthly** | ~10,000 | Full market scan | ~60 min |
| **full** | ~10,000 | Everything (deep dive) | ~60 min |

### Quality Filters

Before pre-screening, basic quality filters are applied:

```yaml
scanning:
  intelligent_filters:
    exchanges: ["NYSE", "NASDAQ", "AMEX"]  # US exchanges only
    exclude_otc: true                       # Skip OTC/pink sheets
    max_symbols_per_run: 600                # Cap for speed
```

**Result**: ~600 high-quality symbols ready for pre-screening

---

## Phase 2: Intelligent Pre-Screening (FAST)

This is where the **magic happens**! The scanner quickly filters the universe to find **promising candidates**.

### Goal
Find symbols with characteristics of good buying opportunities WITHOUT doing full analysis (which is slow).

### Pre-Screening Rules

The scanner looks for **5 specific signals**:

#### Rule 1: Price Drop (Opportunity Zone)
```python
# Look for: 3-10% price drop in last 10 days
price_drop = -10% <= change <= -3%

Why:
- Too small (<3%) = not interesting
- Too large (>10%) = might be crashing
- Sweet spot: 3-10% = potential buy opportunity
```

#### Rule 2: Volume Spike (Interest/Activity)
```python
# Look for: Volume 20%+ above average
volume_spike = recent_volume / avg_volume > 1.2

Why:
- High volume = institutions/traders are interested
- Something is happening (news, earnings, etc.)
- Confirms the price move is meaningful
```

#### Rule 3: Price Filter (No Penny Stocks)
```python
# Require: Price above $5
price >= $5.00

Why:
- Penny stocks are too volatile/risky
- Low liquidity
- Often manipulation targets
```

#### Rule 4: Volume Filter (Liquidity)
```python
# Require: Average daily volume > 500K shares
avg_daily_volume >= 500,000

Why:
- Ensures you can actually buy/sell
- Tighter spreads
- More reliable price action
```

#### Rule 5: Not Crashing (Safety)
```python
# Reject: Price down > 20% in 10 days
change > -20%

Why:
- >20% drop = potential bankruptcy/fraud
- Catching falling knives is dangerous
- We want dips, not disasters
```

### Bonus Rule: Volume Explosion
```python
# Also accept: 2x volume spike (even without price drop)
if volume_ratio > 2.0:
    candidates.append(symbol)

Why:
- 2x volume = major news/event
- Could be breakout opportunity
- Worth deeper analysis
```

### Pre-Screening Performance

```
Input:  600 symbols
Speed:  Fetches only 10 days of data per symbol
Time:   ~5 minutes for 600 symbols
Output: 50-100 promising candidates

Efficiency: Rejects 80-90% of symbols quickly
```

**Result**: ~50-100 candidates that pass pre-screening

---

## Phase 3: Deep Multi-Signal Analysis

Now the scanner does **comprehensive analysis** on the 50-100 candidates:

### Multi-Signal Composite Scoring (0-100)

Each candidate gets scored across 4 dimensions:

#### 1. News Sentiment (30% weight)
```python
# FinBERT AI analyzes recent news articles
- Negative news + solid company = buy opportunity
- Avoids serious issues (bankruptcy, fraud)
- Score: 0-100 based on sentiment + context
```

#### 2. Technical Analysis (40% weight)
```python
# 6 technical indicators:
- RSI < 30 = oversold (good)
- MACD cross = momentum
- Trend = uptrend preferred
- Volume = confirmation
- Support/Resistance = entry zones
- ADX = trend strength

# Score: 0-100 based on technical setup
```

#### 3. Fundamentals (20% weight)
```python
# Company health metrics:
- P/E ratio < 25 = reasonable valuation
- Profit margin > 10% = healthy
- Revenue growth > 10% = growing
- Analyst ratings = consensus view
- Market cap = company size/stability

# Score: 0-100 based on fundamental quality
```

#### 4. Insider Activity (10% weight)
```python
# Smart money tracking:
- Insider buying = bullish signal
- Insider selling = bearish signal
- Heavy buying = STRONG_BUY boost
- Heavy selling = penalty

# Score: 0-100 based on insider sentiment
```

### Trading Strategy Confirmation (Bonus +10 points)

The scanner also checks **5 proven trading strategies**:

```python
strategies = [
    'ABC Patterns',           # Fibonacci wave entries
    'RSI + MACD Confluence', # Oversold + momentum
    'Momentum Breakout',      # Volume + price acceleration
    'Mean Reversion',         # Bollinger Band bounces
    'Trend Following'         # SMA crossovers
]

# If strategies confirm: add up to +10 points to score
```

### Composite Score Calculation

```python
composite_score = (
    news_score      * 0.30 +  # 30%
    technical_score * 0.40 +  # 40%
    fundamental_score * 0.20 +  # 20%
    insider_score   * 0.10    # 10%
) + strategy_boost  # Up to +10 bonus

# Result: 0-100 score (higher = better opportunity)
```

### Confidence Levels

```python
if score >= 80: confidence = "HIGH"
if score >= 60: confidence = "MEDIUM"
if score >= 40: confidence = "LOW"
if score < 40:  SKIP (not enough confidence)
```

### Recommendations

```python
if score >= 85: recommendation = "STRONG BUY"
if score >= 70: recommendation = "BUY"
if score >= 55: recommendation = "WATCH"
if score < 55:  recommendation = "SKIP"
```

**Result**: Top 5 opportunities with complete trade setups

---

## Complete Flow Example

### Real-World Example Walkthrough

Let's say the scanner is analyzing **NVDA** on a typical day:

#### Phase 1: Universe Fetching
```
✅ NVDA found in Finnhub API
✅ Type: Common Stock
✅ Exchange: NASDAQ ✓
✅ Included in tier: "daily" (S&P 500)
```

#### Phase 2: Pre-Screening
```
Recent 10-day data:
- Price: $485 (was $510 10 days ago)
- Change: -4.9% ✓ (in 3-10% range)
- Volume: 45M (avg 35M)
- Volume ratio: 1.29 ✓ (>1.2)
- Price: $485 ✓ (>$5)
- Avg volume: 35M ✓ (>500K)
- Drop: -4.9% ✓ (<20%)

✅ PASSES pre-screening (5/5 rules)
→ Added to candidates for deep analysis
```

#### Phase 3: Deep Analysis
```
News Sentiment: 92/100 ✓
- AI chip demand strong
- Earnings beat expectations
- No serious issues

Technical Analysis: 88/100 ✓
- RSI: 28 (oversold)
- MACD: Bullish cross
- Trend: Uptrend intact
- Volume: Confirmed
- Near support level

Fundamentals: 85/100 ✓
- P/E: 45 (tech sector ok)
- Profit margin: 45%
- Revenue growth: 122%
- Analyst rating: Strong Buy
- Market cap: $2.8T (mega cap)

Insider Activity: 90/100 ✓
- 3 executives bought shares
- No recent selling
- Sentiment: STRONG_BUY

Strategy Signals: +10 bonus ✓
- ABC Pattern: BUY signal
- RSI+MACD: BUY signal
- Mean Reversion: BUY signal

Composite Score:
= (92*0.3 + 88*0.4 + 85*0.2 + 90*0.1) + 10
= 27.6 + 35.2 + 17 + 9 + 10
= 98.8 / 100

Confidence: HIGH (98 > 80)
Recommendation: STRONG BUY (98 > 85)

Trade Setup:
- Entry: $485
- Stop Loss: $470 (3% below)
- Target: $525 (8% above)
- Risk/Reward: 2.7:1
```

#### Final Output
```
🚀 #1 OPPORTUNITY

NVDA - STRONG BUY (Score: 99/100)
Entry: $485 | Target: $525 | Stop: $470 | R/R: 2.7
🎯 Strategies: ABC Pattern, RSI+MACD, Mean Reversion
Why: Strong earnings beat, RSI oversold, insider buying
📈 Tech: 88 | 📰 News: 92 | 💼 Fund: 85 | 👔 Insider: 90
```

---

## Key Advantages

### 1. **Comprehensive Coverage**
- Scans entire US market (not just your watchlist)
- Finds opportunities you'd never discover manually
- No bias or tunnel vision

### 2. **Intelligent Filtering**
- Pre-screening eliminates 80-90% of noise
- Only analyzes promising candidates
- Fast and efficient

### 3. **Multi-Signal Confirmation**
- 4 independent signals must align
- Reduces false positives
- Higher confidence trades

### 4. **Objective Scoring**
- No emotions or bias
- Consistent methodology
- Repeatable results

### 5. **Complete Trade Setups**
- Entry price
- Stop loss (risk management)
- Target price (profit taking)
- Risk/reward ratio

---

## Configuration Options

You can customize the selection process in `config/master_config.yaml`:

### Adjust Scan Tier
```yaml
scanning:
  strategy:
    tier: "daily"  # Change to: weekly, monthly, full
```

### Adjust Pre-Screening Filters
```yaml
scanning:
  intelligent_filters:
    min_price_drop_pct: 3.0     # Minimum drop to consider
    max_price_drop_pct: 10.0    # Maximum (avoid crashes)
    min_volume_ratio: 1.2       # Minimum volume spike
    min_price: 5.0              # Minimum stock price
    min_volume: 500000          # Minimum daily volume
```

### Adjust Scoring Weights
```yaml
scoring:
  weights:
    news_sentiment: 30   # Adjust based on your style
    technical: 40        # Increase for technical focus
    fundamentals: 20     # Increase for value focus
    insider_activity: 10 # Increase to follow smart money
```

### Adjust Confidence Threshold
```yaml
scoring:
  min_confidence: 70  # Only show HIGH confidence
                      # Lower to 60 for more opportunities
```

---

## Summary

The master scanner uses a **3-phase intelligent process**:

1. **Fetch** entire US market from Finnhub (~10,000 symbols)
2. **Pre-screen** for promising candidates using 5 rules (~50-100 symbols)
3. **Deep analyze** with 4-signal scoring + 5 strategies (Top 5 opportunities)

**Result**: You get the **top 5 best opportunities** from the **entire market** with **complete trade setups** and **high confidence**.

**You don't pick symbols. The AI picks for you.** 🎯
