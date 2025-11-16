# 📊 Historical News Correlation - Quick Start

Track which types of news lead to price rebounds vs further declines.

---

## What It Does

Analyzes historical patterns like:
- "Earnings miss → 75% rebound in 5 days"
- "Guidance downgrade → 40% further decline"
- "Lawsuit news → 60% neutral (no clear pattern)"

Uses this data to **predict rebound probability** for current opportunities!

---

## Quick Start

### 1. Test the Tracker

```bash
# View current database stats
python src/news_correlation.py
```

### 2. Update Correlations (Run Weekly)

```bash
# Fetches price data and calculates correlations
python scripts/update_news_correlations.py
```

### 3. Auto-Track New Opportunities

The system automatically tracks opportunities when you run:
```bash
python scripts/send_news_opportunities.py
python scripts/scan_sp500_news.py
```

---

## How It Works

### 1. **Event Recording**
When a buying opportunity is detected:
- Symbol, date, headline recorded
- Sentiment & category classified
- Initial drop percentage saved

### 2. **Price Tracking**
System tracks price movements:
- 1 day after event
- 3 days after event
- 5 days after event  
- 10 days after event

Outcome classified as:
- **Rebound**: +2% or more
- **Decline**: -2% or worse
- **Neutral**: Between -2% and +2%

### 3. **Correlation Calculation**
Statistics calculated by category/sentiment:
- Success rate (% that rebound)
- Average rebound percentage
- Sample size
- Confidence level (HIGH/MEDIUM/LOW)

### 4. **Prediction**
For new opportunities, system predicts:
- HIGH_REBOUND (70%+ success rate)
- MODERATE_REBOUND (55-70%)
- NEUTRAL (45-55%)
- MODERATE_DECLINE (30-45%)
- HIGH_DECLINE (<30%)

---

## Example Output

```
📈 Historical Correlations:

1. earnings / negative
   ✅ 75.0% rebound rate
   📊 Avg gain: +4.2%
   📝 Sample: 24 events (HIGH confidence)

2. guidance / negative
   ❌ 35.0% rebound rate
   📊 Avg change: -2.8%
   📝 Sample: 15 events (MEDIUM confidence)

3. analyst_downgrade / negative
   ✅ 62.5% rebound rate
   📊 Avg gain: +3.1%
   📝 Sample: 8 events (LOW confidence)
```

---

## News Categories

Auto-detected from headlines:
- `earnings` - Earnings reports
- `guidance` - Forward guidance
- `analyst_downgrade` - Analyst ratings
- `lawsuit` - Legal issues
- `regulatory` - Regulatory concerns
- `competitive` - Competition news
- `general` - Other news

---

## Database

**Location:** `data/metadata/news_correlation.db` (SQLite)

**Tables:**
- `news_events` - Historical events
- `price_movements` - Price tracking
- `correlations` - Calculated statistics

**Size:** Small (~1-5 MB for 1000s of events)

---

## Integration

### In Telegram Alerts

Opportunities now show correlation prediction:

```
1. NVDA 🟢
Score: 85/100
• Price: $485.50 (-5.2%)
• Correlation: HIGH_REBOUND (75% success rate)
  Based on 24 historical events: avg +4.2% rebound
```

### In JSON Output

```json
{
  "symbol": "NVDA",
  "correlation_prediction": {
    "prediction": "HIGH_REBOUND",
    "probability": 0.75,
    "confidence": "HIGH",
    "reason": "Based on 24 historical events: 75% rebound rate, avg +4.2% gain"
  }
}
```

---

## Maintenance

### Weekly Update (Recommended)

```bash
python scripts/update_news_correlations.py
```

Updates price movements and recalculates correlations.

### Add to GitHub Actions

```yaml
# .github/workflows/weekly-correlation-update.yml
name: Update News Correlations

on:
  schedule:
    - cron: '0 12 * * 0'  # Sundays at 12 PM

jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - name: Install dependencies
        run: pip install -r requirements-base.txt yfinance
      - name: Update correlations
        run: python scripts/update_news_correlations.py
      - name: Commit database
        run: |
          git add data/metadata/news_correlation.db
          git commit -m "Update news correlations"
          git push
```

---

## Benefits

✅ **Data-Driven** - Based on actual historical outcomes  
✅ **Confidence Levels** - Know when predictions are reliable  
✅ **Auto-Learning** - Improves as more data accumulates  
✅ **Category-Specific** - Different news types behave differently  
✅ **Transparent** - Shows reasoning for each prediction  

---

## FAQ

### Q: How much data is needed?
**A:** Minimum 3 events per category. 10+ for MEDIUM confidence, 20+ for HIGH confidence.

### Q: How accurate are predictions?
**A:** Accuracy improves with sample size. HIGH confidence predictions are based on 20+ similar historical events.

### Q: What if no correlation data exists?
**A:** System returns "UNKNOWN" and falls back to standard opportunity scoring.

### Q: Does it slow down scans?
**A:** No! Correlation lookup is instantaneous (SQLite index query).

---

**Status:** ✅ Core functionality complete, integration in progress!

Next: Full integration with news scanner + Telegram alerts

