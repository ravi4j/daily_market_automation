# 📰 News Scanner - Quick Start Guide

Automatically identify buying opportunities from market dips and negative news.

## What It Does

🔍 **Scans** your portfolio symbols for price drops  
📰 **Analyzes** Yahoo Finance news for sentiment  
📊 **Checks** fundamentals (P/E, margins, growth)  
🎯 **Scores** opportunities (0-100)  
📱 **Alerts** you via Telegram with top picks

---

## Quick Setup (2 minutes)

### 1. Files Already Created ✅

The following files have been added to your project:
- `src/news_monitor.py` - Core scanning engine
- `scripts/send_news_opportunities.py` - Alert script
- `.github/workflows/daily-news-scan.yml` - Automation

### 2. Configuration

**Symbols** - Uses your existing `config/symbols.yaml`:
```yaml
symbols:
  AAPL: AAPL
  TQQQ: TQQQ
  UBER: UBER
  NVDA: NVDA
```

**That's it!** The scanner will automatically monitor these symbols.

### 3. Telegram Setup (Optional)

Already configured in GitHub Secrets:
- `TELEGRAM_BOT_TOKEN` - Your bot token
- `TELEGRAM_CHAT_ID` - Your chat ID

If not set up, see [Telegram Setup Guide](docs/telegram-setup.md)

---

## How to Use

### Option 1: Fully Automated (Recommended)

**GitHub Actions runs automatically:**
- ⏰ **9:00 AM EST** - Morning scan
- ⏰ **4:30 PM EST** - After market close

You'll receive Telegram alerts with opportunities!

### Option 2: Manual Trigger

**Via GitHub Actions:**
1. Go to Actions → "Daily News Scanner"
2. Click "Run workflow"
3. Wait 1-2 minutes
4. Check Telegram or `signals/news_opportunities.json`

**Via Command Line:**
```bash
# Activate virtual environment
source venv/bin/activate

# Run scanner
python scripts/send_news_opportunities.py
```

---

## Understanding the Alerts

### Telegram Message Example

```
📰 Daily News Scan Report
2025-11-15 16:30

Scanned: 4 symbols
Found: 2 opportunities

━━━━━━━━━━━━━━━━━━━━

1. NVDA 🟢
NVIDIA Corporation
Score: 85/100
• Price: $485.20 (-8.5%)
• From 52W High: 12.3%
• P/E: 42.5
• Analyst: Buy

📰 NVIDIA shares fall after earnings guidance...

2. UBER 🟡
Uber Technologies Inc
Score: 62/100
• Price: $68.50 (-5.8%)
• From 52W High: 8.2%
• P/E: 28.1

━━━━━━━━━━━━━━━━━━━━

💡 Next Steps:
• Review fundamentals
• Run on-demand analysis
• Set price alerts
• Consider position sizing

⚠️ Not financial advice. DYOR.
```

### Score Interpretation

- **80-100** 🟢 STRONG BUY - Excellent opportunity
- **65-79** 🟢 BUY - Good entry point  
- **50-64** 🟡 WATCH - Monitor for better entry
- **<50** 🔴 AVOID - Risk too high

---

## What Makes a Good Opportunity?

✅ **Ideal Profile:**
- 5-15% price drop in 5 days
- 10-30% below 52-week high
- P/E ratio: 10-25
- Strong revenue growth (>10%)
- Healthy margins (>15%)
- Buy/Strong Buy analyst rating
- Negative news without red flags

❌ **Red Flags (Auto-Filtered):**
- Bankruptcy, fraud, scandals
- SEC investigations
- Lawsuits, delisting threats
- Accounting issues

---

## Real-World Example

**You mentioned CoreWeave dropped yesterday:**

1. **Scanner detects:**
   - 15% drop detected ✅
   - News: "CoreWeave falls on competitive concerns" ✅
   - No red flags (bankruptcy, fraud) ✅

2. **Analyzes fundamentals:**
   - P/E ratio: Reasonable ✅
   - Revenue growth: Strong ✅
   - Profit margins: Healthy ✅
   - Analyst rating: Buy ✅

3. **Generates score: 82/100**
   - Recommendation: 🟢 STRONG BUY

4. **Sends alert to Telegram:**
   ```
   1. COREWEAVE 🟢
   Score: 82/100
   • Price: $XX.XX (-15.0%)
   • From 52W High: 20%
   • P/E: 22
   📰 CoreWeave tumbles on competitive concerns...
   ```

5. **Your action:**
   - Review the opportunity ✅
   - Run on-demand analysis for technical signals
   - Check support levels on charts
   - Set entry price & stop loss
   - Execute if aligned with your strategy

---

## Next Steps After Alert

### 1. Verify Fundamentals
- Read full news articles
- Check company financials
- Review analyst reports

### 2. Run Technical Analysis
Use on-demand analysis:
```bash
# Via GitHub Actions
# Actions → On-Demand Analysis → Run with symbol
```

### 3. Check Charts
Look at:
- Support levels
- Volume patterns
- RSI/MACD signals

### 4. Set Trade Plan
- Entry price
- Stop loss
- Take profit targets
- Position size

---

## Customization

### Add More Symbols

Edit `config/symbols.yaml`:
```yaml
symbols:
  # Your existing symbols
  AAPL: AAPL
  TQQQ: TQQQ
  
  # Add new ones
  MSFT: MSFT
  GOOGL: GOOGL
  COREWEAVE: COREWEAVE  # If publicly traded
```

Next scan will include them automatically!

### Adjust Sensitivity

Edit `scripts/send_news_opportunities.py`, line ~47:
```python
# Current: 3% minimum drop
opportunities = monitor.identify_opportunities(symbols, min_drop=3.0)

# More sensitive (catch smaller dips)
opportunities = monitor.identify_opportunities(symbols, min_drop=2.0)

# Less sensitive (only large drops)
opportunities = monitor.identify_opportunities(symbols, min_drop=5.0)
```

---

## Integration with Your Workflow

### Combined Signal Strength

If a symbol appears in **both**:
1. News Scanner (buying opportunity)
2. Daily Strategy Alerts (technical BUY signal)

→ **This is a very strong signal!**

### Daily Flow

```
6:35 PM → Fetch latest prices
6:40 PM → Generate charts
9:30 PM → Run trading strategies
9:30 PM → Scan news for opportunities ← NEW
         ↓
    Telegram alerts
```

---

## Files Generated

### signals/news_opportunities.json

Full scan results saved here:
```json
{
  "scan_date": "2025-11-15T16:30:00",
  "symbols_scanned": 4,
  "opportunities_found": 2,
  "opportunities": [...]
}
```

Access anytime to review past scans.

---

## Testing

### Test Locally (Optional)

```bash
# Activate virtual environment
source venv/bin/activate

# Install dependencies if needed
pip install -r requirements-base.txt
pip install -r requirements-fetch.txt

# Run scanner
python scripts/send_news_opportunities.py
```

### Test via GitHub Actions

1. Push your code
2. Go to Actions → "Daily News Scanner"
3. Click "Run workflow" → "Run workflow"
4. Wait ~2 minutes
5. Check Telegram or workflow summary

---

## FAQ

**Q: Will I get alerts every day?**  
A: Only when opportunities are found (5%+ drops with good fundamentals).

**Q: What if no opportunities?**  
A: You'll get a message: "No significant buying opportunities found today."

**Q: Can I disable this?**  
A: Yes, go to `.github/workflows/daily-news-scan.yml` and delete the `schedule:` section.

**Q: How do I add CoreWeave?**  
A: Add to `config/symbols.yaml`. If not publicly traded yet, wait for IPO.

**Q: Does this guarantee profits?**  
A: No. This identifies opportunities. You must verify, analyze, and manage risk.

---

## Commit and Enable

### Commit the Changes

```bash
git add .
git commit -m "feat: Add Yahoo Finance news scanner for buying opportunities"
git push
```

### Verify Workflow

1. Go to: https://github.com/YOUR_USERNAME/daily_market_automation/actions
2. Check that "Daily News Scanner" appears in workflows
3. Manually trigger it to test
4. Check Telegram for alert

---

## Success! 🎉

You now have an automated system that:
- 🔍 Scans your portfolio for price drops
- 📰 Analyzes news sentiment
- 📊 Checks fundamentals
- 🎯 Scores opportunities
- 📱 Alerts you via Telegram

**Next scans:**
- Tomorrow at 9:00 AM EST
- Tomorrow at 4:30 PM EST

Sit back and let the system work for you!

---

## Need Help?

- 📖 [Full Guide](docs/NEWS_SCANNER_GUIDE.md)
- 📖 [Telegram Setup](docs/telegram-setup.md)
- 🐛 [Report Issues](https://github.com/ravi4j/daily_market_automation/issues)

---

**⚠️ Disclaimer**: Not financial advice. Always do your own research and consult with a financial advisor before making investment decisions.

