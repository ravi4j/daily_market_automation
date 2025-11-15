# 💼 Insider Tracking - Quick Start

Get started with insider trading tracking in 5 minutes!

---

## Step 1: Get Free API Key (2 min)

1. Go to https://finnhub.io/register
2. Sign up (free)
3. Copy your API key

---

## Step 2: Set Environment Variable (1 min)

**Option A: Terminal (temporary)**
```bash
export FINNHUB_API_KEY='your_api_key_here'
```

**Option B: Permanent (recommended)**
```bash
# Add to your shell profile
echo 'export FINNHUB_API_KEY="your_api_key_here"' >> ~/.zshrc
source ~/.zshrc
```

**Option C: `.env` file**
```bash
# Create .env in project root
echo 'FINNHUB_API_KEY=your_api_key_here' >> .env
```

---

## Step 3: Install Dependencies (1 min)

```bash
pip install finnhub-python
# or
pip install -r requirements-base.txt
```

---

## Step 4: Test It (1 min)

```bash
# Run test suite
python scripts/test_insider_tracking.py

# Or test specific stocks
python src/insider_tracker.py AAPL NVDA MSFT
```

Expected output:
```
✅ Connected to Finnhub API
📊 Analyzing insider activity for 3 symbol(s)...

Symbol: AAPL
Sentiment: BUY
Score Adjustment: +8
Buys: 5, Sells: 2
Net Value: $2,500,000.00
...
```

---

## Step 5: Use It! (varies)

### Daily Portfolio Scan
```bash
python scripts/send_news_opportunities.py
```

### S&P 500 Scanner (Pre-filtered, Fast)
```bash
python scripts/scan_sp500_news.py
```

### Full S&P 500 Scan (Slower, Comprehensive)
```bash
python scripts/scan_sp500_news.py --full-scan
```

### Test Mode (10 stocks only)
```bash
python scripts/scan_sp500_news.py --top 10
```

---

## What You'll See

### Example Alert

```
📰 S&P 500 News Scan
2024-11-15 18:30

Found: 12 opportunities

1. NVDA 🟢
NVIDIA Corporation
Score: 87/100 (+15 insider 🟢)
• Price: $485.50 (-5.2%)
• Insider: 🟢🟢 STRONG_BUY (4B/1S)
```

### Score Adjustments

| Insider Signal | Score Change | Example |
|---------------|--------------|---------|
| 🟢🟢 STRONG_BUY | +15 | 70 → 85 |
| 🟢 BUY | +8 | 70 → 78 |
| ⚪ NEUTRAL | 0 | 70 → 70 |
| 🔴 SELL | -8 | 70 → 62 |
| 🔴🔴 STRONG_SELL | -15 | 70 → 55 |

---

## Command Flags

```bash
# Pre-filtered scan (default, fast)
python scripts/scan_sp500_news.py

# Full scan (all stocks, slower)
python scripts/scan_sp500_news.py --full-scan

# Custom drop threshold
python scripts/scan_sp500_news.py --min-drop 3.0

# Skip insider data (faster)
python scripts/scan_sp500_news.py --no-insider

# Test mode
python scripts/scan_sp500_news.py --top 10
```

---

## GitHub Actions Setup

### Add Secret

1. Go to your repo on GitHub
2. Settings → Secrets and variables → Actions
3. New repository secret:
   - Name: `FINNHUB_API_KEY`
   - Value: Your API key
4. Save

That's it! Workflows will automatically use insider data.

---

## Troubleshooting

### "API key not found"
```bash
# Make sure it's set
echo $FINNHUB_API_KEY

# If empty, set it:
export FINNHUB_API_KEY='your_key_here'
```

### "No module named 'finnhub'"
```bash
pip install finnhub-python
```

### "Rate limit reached"
This is normal! The system will wait automatically.

For testing, use: `--top 10`

---

## Next Steps

✅ Read full guide: `INSIDER_TRACKING_GUIDE.md`  
✅ Configure settings: `config/insider_config.yaml`  
✅ Test suite: `python scripts/test_insider_tracking.py`  
✅ Run daily: `python scripts/send_news_opportunities.py`

---

**That's it! Happy tracking! 🚀**

