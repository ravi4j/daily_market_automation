# 📰 Yahoo Finance News Scanner Guide

Monitor news and identify buying opportunities from price dips automatically.

## Overview

The News Scanner monitors Yahoo Finance news articles for your tracked symbols and identifies potential buying opportunities when:
- Stocks experience significant price drops (5%+ in 5 days)
- News indicates temporary concerns (not fundamental issues)
- Fundamentals remain strong (good P/E, margins, growth)

## Features

✅ **Automatic Scanning** - Runs twice daily (morning & after market close)
✅ **Uses Your Config** - Scans symbols from `config/symbols.yaml`
✅ **Smart Filtering** - Avoids red flags (bankruptcy, fraud, scandals)
✅ **Opportunity Scoring** - Ranks opportunities 0-100
✅ **Telegram Alerts** - Sends top opportunities to Telegram
✅ **Fundamental Analysis** - Checks P/E, margins, growth, analyst ratings

---

## How It Works

### 1. News Fetching
- Fetches last 10 news articles for each symbol via `yfinance`
- Analyzes titles for sentiment keywords
- Detects percentage drops mentioned in headlines

### 2. Sentiment Analysis
**Opportunity Keywords** (indicate dips):
- falls, drops, plunges, tumbles, declines
- selloff, misses, disappoints, downgrade
- slump, slide, correction, pullback

**Red Flag Keywords** (avoid):
- bankruptcy, fraud, scandal, investigation
- lawsuit, delisting, SEC investigation

### 3. Fundamental Check
For each symbol with a 5-day drop:
- Current price & market cap
- P/E ratio, PEG ratio
- Profit margins & revenue growth
- Distance from 52-week high
- Analyst recommendations

### 4. Opportunity Scoring (0-100)

**High Score (+points):**
- 5-15% price drop (ideal dip) → +20 pts
- 10-30% from 52W high (good entry) → +15 pts
- P/E ratio 10-25 (reasonable valuation) → +10 pts
- Revenue growth >10% → +10 pts
- Profit margins >15% → +10 pts
- Analyst rating: Buy/Strong Buy → +10 pts
- Negative news sentiment (fear = opportunity) → +10 pts

**Low Score (-points):**
- Drop >25% (falling knife) → -10 pts
- Red flag keywords in news → -30 pts
- Poor analyst ratings → -5 pts

**Score Interpretation:**
- **80-100**: 🟢 STRONG BUY - Excellent opportunity
- **65-79**: 🟢 BUY - Good entry point
- **50-64**: 🟡 WATCH - Monitor for better entry
- **<50**: 🔴 AVOID - Risk too high

---

## Usage

### Automated (Recommended)

News scanner runs automatically via GitHub Actions:
- **9:00 AM EST** - Morning scan
- **4:30 PM EST** - After market close

Results are saved to `signals/news_opportunities.json` and sent to Telegram.

### Manual Trigger

**Via GitHub Actions:**
1. Go to: https://github.com/YOUR_USERNAME/daily_market_automation/actions
2. Click "Daily News Scanner"
3. Click "Run workflow"

**Via Command Line:**
```bash
# Activate virtual environment first
source venv/bin/activate  # or: . venv/bin/activate

# Run the scanner
python scripts/send_news_opportunities.py
```

### Test the Module

```bash
# Activate venv
source venv/bin/activate

# Test just the news monitor (no Telegram)
python src/news_monitor.py

# Full test with Telegram alerts
export TELEGRAM_BOT_TOKEN="your_token"
export TELEGRAM_CHAT_ID="your_chat_id"
python scripts/send_news_opportunities.py
```

---

## Configuration

### Symbols to Scan

The scanner uses symbols from `config/symbols.yaml`:

```yaml
symbols:
  AAPL: AAPL
  TQQQ: TQQQ
  UBER: UBER
  NVDA: NVDA
  # Add more symbols here
```

**To add symbols:**
1. Edit `config/symbols.yaml`
2. Add new lines in the format: `SYMBOL: SYMBOL`
3. Save the file
4. Next scan will include new symbols

### Sensitivity Settings

You can adjust the minimum drop threshold in the code:

**File:** `scripts/send_news_opportunities.py`
```python
# Default: 3% minimum drop
opportunities = monitor.identify_opportunities(symbols_to_scan, min_drop=3.0)

# More sensitive (catch smaller dips)
opportunities = monitor.identify_opportunities(symbols_to_scan, min_drop=2.0)

# Less sensitive (only large drops)
opportunities = monitor.identify_opportunities(symbols_to_scan, min_drop=5.0)
```

---

## Telegram Alert Format

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
• Analyst: Hold

📰 Uber slides on analyst downgrade...

━━━━━━━━━━━━━━━━━━━━

💡 Next Steps:
• Review fundamentals
• Run on-demand analysis
• Set price alerts
• Consider position sizing

⚠️ Not financial advice. DYOR.
```

---

## Output Files

### signals/news_opportunities.json

Contains full scan results:
```json
{
  "scan_date": "2025-11-15T16:30:00",
  "symbols_scanned": 4,
  "scanned_symbols": ["AAPL", "TQQQ", "UBER", "NVDA"],
  "opportunities_found": 2,
  "opportunities": [
    {
      "symbol": "NVDA",
      "fundamentals": {
        "current_price": 485.20,
        "5d_change": -8.5,
        "distance_from_52w_high": 12.3,
        "pe_ratio": 42.5,
        "recommendation": "buy"
      },
      "news": [...],
      "opportunity_score": 85,
      "recommendation": "🟢 STRONG BUY - Excellent opportunity"
    }
  ]
}
```

---

## Integration with Existing System

### Combine with Daily Alerts

You can integrate news scanning with your existing strategy alerts:

1. **Run both workflows** (they're independent)
2. **Compare signals** - If a symbol appears in both news opportunities AND strategy alerts, it's a strong signal
3. **Use on-demand analysis** - For high-score news opportunities, trigger detailed technical analysis

### Workflow Integration

```
Daily Flow:
1. 6:35 PM - Fetch latest prices (daily-fetch.yml)
2. 6:40 PM - Generate charts (daily-charts.yml)
3. 9:30 PM - Run strategies (daily-alerts.yml)
4. 9:30 PM - Scan news (daily-news-scan.yml) ← NEW

All results converge in Telegram
```

---

## Best Practices

### ✅ Do:
- **DYOR** - Always verify opportunities manually
- **Check multiple sources** - Don't rely on one signal
- **Use stop losses** - Protect against further drops
- **Position sizing** - Don't go all-in
- **Diversify** - Spread across multiple opportunities
- **Monitor news** - Stay updated on developments

### ❌ Don't:
- **Catch falling knives** - Avoid stocks with red flags
- **Ignore fundamentals** - Score alone isn't enough
- **Buy on emotion** - Stick to your strategy
- **Over-leverage** - Use appropriate position sizes
- **Ignore risk** - Some dips are justified

---

## Real-World Example

**Scenario: CoreWeave Drops 15%**

1. **News Scanner Detects:**
   - 15% drop in 5 days
   - News: "CoreWeave slides on competitive concerns"
   - No red flags (no bankruptcy/fraud mentions)

2. **Fundamental Analysis:**
   - P/E: 22 (reasonable)
   - Revenue growth: 25% (strong)
   - Profit margins: 18% (healthy)
   - Analyst rating: Buy
   - Distance from 52W high: 20%

3. **Opportunity Score: 82/100**
   - Recommendation: 🟢 STRONG BUY

4. **Your Action:**
   - Review company fundamentals
   - Run on-demand technical analysis
   - Check support levels
   - Set entry price & stop loss
   - Size position appropriately
   - Execute trade if aligned with strategy

---

## Troubleshooting

### No opportunities found
- **Cause**: All symbols are stable or rising
- **Solution**: This is normal! Not every scan finds opportunities

### Too many opportunities
- **Cause**: Market-wide selloff
- **Solution**: Increase `min_drop` threshold or check if it's a broader market issue

### News not fetching
- **Cause**: yfinance API rate limits or symbol has no news
- **Solution**: Wait a few minutes and retry, or check if symbol is valid

### Scores seem off
- **Cause**: Scoring algorithm needs tuning for your strategy
- **Solution**: Adjust scoring weights in `src/news_monitor.py` → `_calculate_opportunity_score()`

---

## Advanced Customization

### Custom Keywords

Edit `src/news_monitor.py`:

```python
class NewsMonitor:
    def __init__(self):
        # Add your custom opportunity keywords
        self.opportunity_keywords = [
            'falls', 'drops', 'your_keyword_here'
        ]
        
        # Add your custom red flags
        self.avoid_keywords = [
            'bankruptcy', 'fraud', 'your_redflag_here'
        ]
```

### Custom Scoring

Modify `_calculate_opportunity_score()` in `src/news_monitor.py`:

```python
def _calculate_opportunity_score(self, fundamentals: Dict, news: List[Dict]) -> int:
    score = 50
    
    # Add your custom scoring logic
    if fundamentals.get('your_metric') > threshold:
        score += 20
    
    return score
```

---

## FAQ

**Q: Does this guarantee profits?**
A: No. This is a tool to identify opportunities. Markets are unpredictable.

**Q: How often should I check?**
A: Let automation handle it. Check Telegram alerts when they arrive.

**Q: Can I use this for day trading?**
A: It's designed for swing trades (multi-day holds), not day trading.

**Q: What if I miss an alert?**
A: Check `signals/news_opportunities.json` for the latest scan results.

**Q: Can I add more symbols?**
A: Yes! Just edit `config/symbols.yaml` and they'll be included in next scan.

**Q: Why use 5-day drops instead of 1-day?**
A: 5 days smooths out noise and catches meaningful corrections, not just daily volatility.

---

## Related Documentation

- [Daily Alerts Guide](./daily-alerts-guide.md)
- [On-Demand Analysis](./ON_DEMAND_ANALYSIS.md)
- [Strategy Testing Guide](./STRATEGY_TESTING_GUIDE.md)
- [Telegram Setup](./telegram-setup.md)

---

## Support

- **Issues**: https://github.com/ravi4j/daily_market_automation/issues
- **Discussions**: https://github.com/ravi4j/daily_market_automation/discussions

---

**⚠️ Disclaimer**: This tool is for educational purposes only. Not financial advice. Always do your own research and consult with a financial advisor before making investment decisions.

