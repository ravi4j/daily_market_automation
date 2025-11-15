# 💼 Insider Trading Tracker Guide

## Overview

The Insider Trading Tracker monitors corporate insider transactions (executives, directors, major shareholders buying/selling their company's stock) and uses this "smart money" data to enhance opportunity scoring.

**Why It Matters:** Insiders often have better information about their company's future prospects. Heavy insider buying can signal confidence, while heavy selling might indicate concerns.

---

## Features

✅ **Real-time Insider Data** - Powered by Finnhub API  
✅ **Sentiment Analysis** - Classifies as STRONG_BUY, BUY, NEUTRAL, SELL, STRONG_SELL  
✅ **Score Adjustment** - Boosts/penalizes opportunity scores (-15 to +15 points)  
✅ **Pre-filtering** - Scans only stocks with significant drops (5%+) for efficiency  
✅ **Rate Limiting** - Stays under API limits (50 calls/min, buffer for 60 limit)  
✅ **Caching** - 24h cache for fundamentals to reduce API calls  
✅ **Fallback Strategies** - Works without API key (degrades gracefully)

---

## Quick Start

### 1. Get Finnhub API Key (FREE)

```bash
# Register for free at https://finnhub.io/register
# Free tier: 60 API calls/minute, 30 calls/second
```

### 2. Set Environment Variable

```bash
export FINNHUB_API_KEY='your_api_key_here'
```

Or add to `.env` file:
```
FINNHUB_API_KEY=your_api_key_here
```

### 3. Test It

```bash
# Run test suite
python scripts/test_insider_tracking.py

# Test on specific symbols
python src/insider_tracker.py AAPL NVDA MSFT
```

### 4. Use It

```bash
# Daily portfolio scan (with insider data)
python scripts/send_news_opportunities.py

# S&P 500 scan (pre-filtered, fast)
python scripts/scan_sp500_news.py

# Full S&P 500 scan (slower, no pre-filter)
python scripts/scan_sp500_news.py --full-scan

# Without insider tracking (faster)
python scripts/scan_sp500_news.py --no-insider
```

---

## How It Works

### 1. **Insider Data Collection**

Fetches insider transactions for the last 30 days:
- Name of insider
- Transaction type (buy/sell)
- Number of shares
- Share price
- Total value

### 2. **Sentiment Calculation**

Analyzes buying vs selling activity:

| Sentiment | Criteria | Score Adjustment |
|-----------|----------|------------------|
| **STRONG_BUY** 🟢🟢 | 75%+ buying by value, 70%+ by count | +15 |
| **BUY** 🟢 | 60%+ buying by value, 55%+ by count | +8 |
| **NEUTRAL** ⚪ | Balanced activity | 0 |
| **SELL** 🔴 | 40% or less buying by value, 45% by count | -8 |
| **STRONG_SELL** 🔴🔴 | 25% or less buying by value, 30% by count | -15 |

### 3. **Score Boosting**

Original opportunity score (0-100) is adjusted:
- **Strong insider buying**: Score + 15 (e.g., 70 → 85)
- **Strong insider selling**: Score - 15 (e.g., 70 → 55)

### 4. **Pre-filtering (Smart Defaults)**

To stay under rate limits, the system:
1. **First pass**: Checks all stocks for 5%+ price drops (fast, uses yfinance)
2. **Second pass**: Only fetches insider data for dropped stocks (uses Finnhub)

Result: Instead of 500 API calls, only ~20-50 calls needed!

---

## Command-Line Flags

### `--full-scan`
Scan all stocks without pre-filtering (slower, more comprehensive):
```bash
python scripts/scan_sp500_news.py --full-scan
```

### `--min-drop`
Customize pre-filter threshold (default 5.0%):
```bash
python scripts/scan_sp500_news.py --min-drop 3.0
```

### `--no-insider`
Skip insider tracking for faster scans:
```bash
python scripts/scan_sp500_news.py --no-insider
```

### `--top`
Test mode - scan only first N symbols:
```bash
python scripts/scan_sp500_news.py --top 10
```

---

## Example Output

### Console Output
```
📊 Top 10 Opportunities:
  1. NVDA   - Score:  87/100 (+15 insider) (-5.2%) - NVIDIA Corporation
  2. AAPL   - Score:  82/100 (+8 insider) (-3.1%) - Apple Inc.
  3. TSLA   - Score:  65/100 (-8.2%) - Tesla Inc.
```

### Telegram Alert
```
📰 S&P 500 News Scan
2024-11-15 18:30

Scanned: 331 stocks
Found: 15 opportunities

📊 By Sector:
• Information Technology: 6
• Consumer Discretionary: 4
• Health Care: 3
• Financials: 2

━━━━━━━━━━━━━━━━━━━━

1. NVDA 🟢
NVIDIA Corporation
Score: 87/100 (+15 insider 🟢)
• Price: $485.50 (-5.2%)
• From 52W High: 12.3%
• P/E: 45.2
• Insider: 🟢🟢 STRONG_BUY (4B/1S)

📰 Nvidia shares drop on supply chain concerns...
```

---

## API Rate Limits

### Finnhub Free Tier
- **60 calls/minute**
- **30 calls/second**

### Our Strategy
- **Rate limiter**: 50 calls/min (buffer)
- **Pre-filter**: Only scan dropped stocks
- **Caching**: 24h cache for fundamentals

### Typical Usage
| Scenario | API Calls | Time | Under Limit? |
|----------|-----------|------|--------------|
| Daily portfolio (4 symbols) | 8 | ~10s | ✅ Yes |
| S&P 500 pre-filtered (50 drops) | 100 | ~2min | ✅ Yes |
| S&P 500 full scan (500 stocks) | 1000 | ~20min | ⚠️ Requires care |

**Note:** Full scans use 1000 calls over 20 minutes (50/min avg), staying under 60/min limit.

---

## Configuration

Edit `config/insider_config.yaml`:

```yaml
# Enable/disable insider tracking
enabled: true

# Lookback period for insider transactions
lookback_days: 30

# Score adjustments
score_adjustments:
  STRONG_BUY: 15
  BUY: 8
  NEUTRAL: 0
  SELL: -8
  STRONG_SELL: -15

# Pre-filter settings
pre_filter:
  min_drop_pct: 5.0
  drop_period_days: 5

# Rate limiting
rate_limit:
  calls_per_minute: 50
```

---

## GitHub Actions Setup

### 1. Add Secret

Go to your repo → Settings → Secrets → Actions:
- Name: `FINNHUB_API_KEY`
- Value: Your API key

### 2. Workflows Updated

Both workflows now include Finnhub support:
- ✅ `daily-news-scan.yml` - Daily portfolio scanner
- ✅ `weekly-sp500-scan.yml` - Weekly S&P 500 scanner

The workflows will:
- Use insider data if `FINNHUB_API_KEY` is set
- Degrade gracefully if not set (skip insider tracking)
- Stay under rate limits with pre-filtering

---

## Troubleshooting

### Error: "Finnhub API key not found"

**Solution:**
```bash
export FINNHUB_API_KEY='your_key_here'
```

Or add to your shell profile (`.bashrc`, `.zshrc`):
```bash
echo 'export FINNHUB_API_KEY="your_key_here"' >> ~/.zshrc
source ~/.zshrc
```

### Error: "No module named 'finnhub'"

**Solution:**
```bash
pip install finnhub-python
```

Or:
```bash
pip install -r requirements-base.txt
```

### Rate Limit Hit

If you see "Rate limit reached, waiting...":
- This is normal and automatic
- The system will wait and resume
- Reduce API calls with `--top 10` for testing

### No Insider Data Found

Possible reasons:
1. **Stock has no recent insider activity** (normal for many stocks)
2. **API key invalid** - Check your key
3. **Rate limit** - Wait a minute and retry

---

## Best Practices

### 1. **Daily Use**
```bash
# Portfolio scan (fast, 4 symbols, ~8 API calls)
python scripts/send_news_opportunities.py
```

### 2. **Weekly Deep Dive**
```bash
# S&P 500 scan (pre-filtered, ~50 stocks, ~100 API calls)
python scripts/scan_sp500_news.py
```

### 3. **Testing New Features**
```bash
# Test on 10 symbols first
python scripts/scan_sp500_news.py --top 10
```

### 4. **Without API Key**
System works without Finnhub API key:
- News scanning ✅
- Fundamentals ✅ (via yfinance)
- Insider tracking ❌ (skipped)

---

## Real-World Example

### Scenario: Market Dip Detection

1. **Market drops 5%**
2. **Pre-filter identifies 50 stocks with 5%+ drops**
3. **Fetch insider data for those 50** (100 API calls, ~2 min)
4. **Find 3 with strong insider buying**:
   - NVDA: Score 85 (+15 insider boost)
   - AAPL: Score 82 (+8 insider boost)
   - MSFT: Score 75 (no recent insider activity)
5. **Telegram alert sent with top picks**
6. **You review and decide to buy NVDA and AAPL**

### Result
You bought stocks with:
- ✅ Price dips (5%+ drops)
- ✅ Strong fundamentals (P/E, margins, growth)
- ✅ Insider confidence (heavy buying)

---

## FAQ

### Q: Is insider trading legal?
**A:** Yes, when properly reported. Corporate insiders must file Form 4 with the SEC within 2 business days. This data is public and legal to use.

### Q: How accurate is insider data?
**A:** Insiders don't always predict the future correctly, but studies show insider buying often correlates with positive returns. Use it as one signal among many.

### Q: Can I use a different API?
**A:** Yes! The code is modular. You can create a new class similar to `InsiderTracker` using any API (e.g., SEC Edgar, Insider Monkey, Whale Wisdom).

### Q: What if I hit rate limits?
**A:** The system has built-in rate limiting. If you still hit limits, use `--top 10` for testing or reduce `calls_per_minute` in config.

### Q: Does it work in GitHub Actions?
**A:** Yes! Just add `FINNHUB_API_KEY` to GitHub Secrets. Workflows are pre-configured.

---

## Next Steps

1. ✅ **Test locally**: `python scripts/test_insider_tracking.py`
2. ✅ **Run a scan**: `python scripts/scan_sp500_news.py --top 10`
3. ✅ **Check results**: `signals/sp500_opportunities.json`
4. ✅ **Add to GitHub**: Set `FINNHUB_API_KEY` in repo secrets
5. ✅ **Automate**: Workflows will run automatically

---

## Support

- **Finnhub Docs**: https://finnhub.io/docs/api
- **Free API Key**: https://finnhub.io/register
- **Test Script**: `python scripts/test_insider_tracking.py`
- **Configuration**: `config/insider_config.yaml`

---

**Happy tracking! 🚀**

