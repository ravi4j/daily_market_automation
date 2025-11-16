# 🤖 Auto-Add to Portfolio - Quick Start

Automatically analyze high-score opportunities and optionally add them to your portfolio.

---

## 🎯 What It Does

When the news scanner or S&P 500 scanner finds high-score opportunities (80+), this feature:

1. ✅ **Automatically runs technical analysis** on each symbol
2. ✅ **Generates complete charts** (breakouts, indicators, ABC patterns)
3. ✅ **Sends detailed Telegram reports** with all 5 strategies
4. ✅ **Optionally adds to portfolio** if confidence is HIGH
5. ✅ **Prevents duplicate work** with 24-hour cooldown

---

## 🚀 Quick Start

### 1. Configure Settings

Edit `config/auto_analysis.yaml`:

```yaml
auto_analysis:
  enabled: true              # Turn on/off
  min_score: 80             # Only analyze 80+ scores
  max_per_scan: 5           # Limit to top 5
  auto_add_to_portfolio: false  # Set true to auto-add
  min_confidence_for_add: HIGH  # Only add HIGH confidence
  send_telegram_report: true    # Send detailed reports
  cooldown_hours: 24        # Don't re-analyze for 24h
```

### 2. Run It

```bash
# Run manually
python scripts/auto_add_portfolio.py

# OR add to daily workflow (see below)
```

### 3. Check Results

```bash
# View analysis results
ls signals/auto_analysis/

# Example: NVDA_20251116_163245.json
cat signals/auto_analysis/NVDA_*.json

# Check if added to portfolio
cat config/symbols.yaml
```

---

## 📊 Example Output

```
================================================================================
🤖 AUTO-ADD TO PORTFOLIO
Automatically analyze high-score opportunities
================================================================================

📋 Loading configuration...
✅ Config loaded:
   - Min score: 80
   - Max per scan: 5
   - Auto-add to portfolio: false
   - Cooldown: 24 hours

📰 Loading opportunities...
✅ Found 15 total opportunities

🔍 Filtering opportunities...
📊 Found 8 opportunities with score >= 80
   8 are not in cooldown period
   Top 5 selected for analysis (max: 5)

✅ 5 symbols selected for analysis:
   1. NVDA   - Score: 92.5/100 (sp500_scan)
   2. AMD    - Score: 88.3/100 (sp500_scan)
   3. AAPL   - Score: 85.7/100 (portfolio_news)
   4. MSFT   - Score: 82.1/100 (sp500_scan)
   5. GOOGL  - Score: 81.4/100 (sp500_scan)

================================================================================
🚀 Starting automated analysis...
================================================================================

================================================================================
📊 Analyzing NVDA (Score: 92.5/100, Source: sp500_scan)
================================================================================

1️⃣  Running technical analysis...
   Fetching data for NVDA...
   Calculating indicators...
   Running strategies...
   ✅ 5 strategies analyzed

✅ Analysis saved: NVDA_20251116_163245.json

2️⃣  Sending Telegram report...
✅ Telegram report sent

✅ NVDA analysis complete!

⏳ Waiting 5 seconds before next analysis...

[... continues for AMD, AAPL, MSFT, GOOGL ...]

================================================================================
📊 AUTO-ANALYSIS COMPLETE
================================================================================
✅ Analyzed: 5/5 symbols

📁 Results saved to: signals/auto_analysis/
📱 Telegram reports sent

================================================================================
```

---

## 📱 Telegram Report Example

You'll receive a detailed report for each symbol:

```
🔍 SYMBOL ANALYSIS: NVDA

📊 OPPORTUNITY SCORE: 92.5/100
   Source: S&P 500 Scan
   Sentiment: Negative (buying opportunity)
   Insider: STRONG BUY (+15)

💰 CURRENT PRICE: $485.20
📉 Price Drop: -5.2% (from $512.50)

━━━━━━━━━━━━━━━━━━━━

📊 TECHNICAL ANALYSIS SIGNALS:

1. RSI + MACD Confluence: BUY ⭐⭐⭐ HIGH
   - RSI: 35.2 (oversold)
   - MACD: Bullish crossover
   - Entry: $485 - $490
   - Target: $525 (+8.2%)
   - Stop Loss: $470 (-3.1%)

2. Trend Following: HOLD ⭐ LOW
   - Trend: Downtrend (caution)
   - Wait for trend reversal

3. ABC Pattern: BUY ⭐⭐ MEDIUM
   - Pattern: Bullish ABC forming
   - Entry Zone: $480 - $495
   - Targets: $525, $540, $560
   - Stop: $465

━━━━━━━━━━━━━━━━━━━━

📈 COMBINED RECOMMENDATION:
✅ STRONG BUY
   - 2/5 strategies recommend BUY
   - High opportunity score (92.5)
   - Strong insider buying
   - Oversold technicals

⚠️ Risk/Reward: 1:2.6 (Good)

📁 Charts: charts/indicators/NVDA_indicators.png
```

---

## ⚙️ Configuration Options

### Basic Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `enabled` | `true` | Enable/disable feature |
| `min_score` | `80` | Minimum score to trigger (0-100) |
| `max_per_scan` | `5` | Max symbols to analyze per run |
| `cooldown_hours` | `24` | Hours before re-analyzing same symbol |

### Analysis Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `strategies` | `[rsi_macd, trend_following, abc_patterns]` | Which strategies to run |
| `send_telegram_report` | `true` | Send detailed reports to Telegram |

### Auto-Add Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `auto_add_to_portfolio` | `false` | **Auto-add to config/symbols.yaml** |
| `min_confidence_for_add` | `HIGH` | Minimum confidence to auto-add |

### Advanced Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `priority_sectors` | `[]` | Prioritize these sectors when max reached |

---

## 🔄 Add to Daily Workflow

### Option A: Run After News Scanner

This is automatically integrated in the daily workflow scripts!

**Already included in:**
- ✅ `scripts/run_daily_workflow.sh` (macOS/Linux)
- ✅ `scripts/run_daily_workflow.bat` (Windows)
- ✅ `.github/workflows/daily-news-scan.yml` (GitHub Actions)

### Option B: Manual Schedule

**cron (macOS/Linux):**
```bash
# Run at 5:00 PM EST (after news scanner)
0 17 * * 1-5 cd /path/to/project && venv/bin/python scripts/auto_add_portfolio.py
```

**Task Scheduler (Windows):**
```powershell
# Create task
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday,Tuesday,Wednesday,Thursday,Friday -At 5:00PM
$action = New-ScheduledTaskAction -Execute "python" -Argument "scripts\auto_add_portfolio.py" -WorkingDirectory "C:\path\to\project"
Register-ScheduledTask -TaskName "Auto Portfolio Analysis" -Trigger $trigger -Action $action
```

---

## 📈 Use Cases

### 1. Conservative (Manual Review)

```yaml
auto_add_to_portfolio: false  # Keep false
min_score: 85                 # Higher threshold
max_per_scan: 3               # Fewer symbols
```

**Result**: Get detailed analysis, but you decide what to add.

---

### 2. Aggressive (Auto-Add)

```yaml
auto_add_to_portfolio: true   # Enable auto-add
min_score: 75                 # Lower threshold
max_per_scan: 10              # More symbols
min_confidence_for_add: MEDIUM  # Less strict
```

**Result**: Automatically adds good opportunities to portfolio.

---

### 3. Sector Focus

```yaml
min_score: 80
priority_sectors:
  - Information Technology
  - Healthcare
```

**Result**: Prioritizes tech and healthcare stocks when multiple opportunities.

---

## 🎯 Real-World Example

**Scenario**: S&P 500 scan finds 12 stocks with 70+ scores

1. **Filter**: Only 8 have 80+ scores
2. **Cooldown**: 3 were analyzed yesterday, skip them
3. **Limit**: 5 remaining, but max is 5, so analyze all
4. **Prioritize**: 2 are in priority sectors, analyze them first
5. **Analyze**: Run technical analysis on all 5
6. **Report**: Send 5 detailed Telegram reports
7. **Auto-Add**: If enabled and HIGH confidence, add to portfolio
8. **Cache**: Mark all 5 in cooldown for 24 hours

**Time**: ~2-3 minutes total (5 symbols × 30 seconds each)

---

## 📊 Output Files

### Analysis Results

```
signals/auto_analysis/
├── NVDA_20251116_163245.json
├── AMD_20251116_163310.json
├── AAPL_20251116_163335.json
├── MSFT_20251116_163400.json
└── GOOGL_20251116_163425.json
```

**Each file contains:**
- Original opportunity score
- News sentiment
- Insider activity
- All technical indicators
- Strategy signals (BUY/SELL/HOLD)
- Confidence levels
- Entry/exit levels
- Risk/reward ratios

### Cooldown Cache

```
data/cache/auto_analysis_cache.json
```

**Format:**
```json
{
  "NVDA": {
    "last_analyzed": "2025-11-16T16:32:45",
    "score": 92.5,
    "source": "sp500_scan"
  },
  "AMD": {
    "last_analyzed": "2025-11-16T16:33:10",
    "score": 88.3,
    "source": "sp500_scan"
  }
}
```

---

## 🛠️ Troubleshooting

### Issue: No symbols analyzed

**Check:**
1. Are there opportunities? `cat signals/news_opportunities.json`
2. Are scores high enough? Lower `min_score` in config
3. Are symbols in cooldown? Check `data/cache/auto_analysis_cache.json`

---

### Issue: Too many analyses

**Solution:** Adjust limits
```yaml
max_per_scan: 3  # Reduce from 5
min_score: 85    # Increase from 80
```

---

### Issue: Not adding to portfolio

**Check:**
1. Is `auto_add_to_portfolio: true`?
2. Are signals HIGH confidence? Lower `min_confidence_for_add`
3. Check logs for errors

---

## 📚 Related Features

- **News Scanner**: [`NEWS_SCANNER_QUICKSTART.md`](NEWS_SCANNER_QUICKSTART.md)
- **S&P 500 Scanner**: [`SP500_SCANNER_GUIDE.md`](SP500_SCANNER_GUIDE.md)
- **On-Demand Analysis**: [`docs/ON_DEMAND_ANALYSIS.md`](docs/ON_DEMAND_ANALYSIS.md)
- **Insider Trading**: [`INSIDER_QUICKSTART.md`](INSIDER_QUICKSTART.md)

---

## 🎉 Benefits

✅ **Save Time**: No manual analysis of 80+ scored stocks
✅ **Never Miss**: Automatically analyze all high-score opportunities
✅ **Complete Picture**: Combines news + technicals + insider data
✅ **Smart Cooldown**: Doesn't re-analyze same symbols daily
✅ **Configurable**: Adjust thresholds to your risk tolerance
✅ **Integrated**: Works seamlessly with existing workflows

---

**Ready to automate your portfolio!** 🚀

Questions? Check [`WORKFLOW_MAINTENANCE.md`](WORKFLOW_MAINTENANCE.md) or [`README.md`](README.md)

