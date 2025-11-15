## 📊 S&P 500 News Scanner

Scan all 500 stocks in the S&P 500 for buying opportunities!

## Quick Start

### 1. Fetch S&P 500 List

```bash
# Activate venv
source .venv/bin/activate

# Fetch current S&P 500 constituents from Wikipedia
python scripts/fetch_sp500_list.py
```

This creates `data/sp500_symbols.json` with ~500 stock symbols.

### 2. Run S&P 500 Scan

```bash
# Scan all 500 stocks (takes ~5-10 minutes)
python scripts/scan_sp500_news.py

# Scan specific sector only
python scripts/scan_sp500_news.py --sector "Information Technology"

# Test with just 10 stocks
python scripts/scan_sp500_news.py --top 10
```

### 3. View Results

Results are saved to `signals/sp500_opportunities.json` and sent to Telegram.

---

## Features

✅ **All 500 Stocks** - Scans entire S&P 500 index  
✅ **Sector Filtering** - Focus on specific sectors  
✅ **Progress Bar** - See scan progress in real-time  
✅ **Auto-Updates List** - Fetches current S&P 500 constituents  
✅ **Weekly Automation** - GitHub Actions runs every Sunday  
✅ **Telegram Alerts** - Top 10 opportunities sent to your phone  

---

## Usage Options

### Scan All S&P 500

```bash
python scripts/scan_sp500_news.py
```

**Output:**
- Scans ~500 stocks
- Takes ~5-10 minutes
- Finds stocks with 5%+ drops
- Ranks by opportunity score

### Scan by Sector

```bash
# Tech stocks only
python scripts/scan_sp500_news.py --sector "Information Technology"

# Healthcare
python scripts/scan_sp500_news.py --sector "Health Care"

# Financials
python scripts/scan_sp500_news.py --sector "Financials"
```

**Available Sectors:**
- Information Technology
- Health Care
- Financials
- Consumer Discretionary
- Communication Services
- Industrials
- Consumer Staples
- Energy
- Utilities
- Real Estate
- Materials

### Test Mode

```bash
# Scan just 10 stocks (for testing)
python scripts/scan_sp500_news.py --top 10

# Scan top 50 stocks
python scripts/scan_sp500_news.py --top 50
```

---

## Automated Weekly Scans

### GitHub Actions

The workflow runs automatically every **Sunday at 6 PM EST**.

**Manual Trigger:**
1. Go to Actions → "Weekly S&P 500 Scan"
2. Click "Run workflow"
3. Choose sector (or All Sectors)
4. Optionally limit to top N stocks
5. Click "Run workflow"

**Results:**
- Saved to `signals/sp500_opportunities.json`
- Sent to Telegram (top 10)
- Available in workflow artifacts

---

## Example Output

### Terminal

```
📊 Loading S&P 500 constituent list...
✅ Fetched 503 S&P 500 symbols
📰 Scanning 503 stocks for opportunities...
⏱️  This will take approximately 4.2 minutes

🔍 Scanning symbols...
100%|██████████| 503/503 [04:15<00:00,  1.97stock/s]

✅ Scan complete! Found 23 opportunities
💾 Saved to signals/sp500_opportunities.json

📊 Top 10 Opportunities:
  1. NVDA   - Score:  92/100 (-8.5%) - NVIDIA Corporation
  2. META   - Score:  88/100 (-7.2%) - Meta Platforms, Inc.
  3. UBER   - Score:  85/100 (-6.8%) - Uber Technologies, Inc.
  4. AMD    - Score:  82/100 (-9.1%) - Advanced Micro Devices, Inc.
  5. COIN   - Score:  78/100 (-12.3%) - Coinbase Global, Inc.
  6. PLTR   - Score:  75/100 (-8.9%) - Palantir Technologies Inc.
  7. SNOW   - Score:  72/100 (-7.5%) - Snowflake Inc.
  8. NET    - Score:  70/100 (-6.2%) - Cloudflare, Inc.
  9. DDOG   - Score:  68/100 (-5.8%) - Datadog, Inc.
  10. ZS    - Score:  65/100 (-6.4%) - Zscaler, Inc.

📤 Sending to Telegram...
✅ Sent to Telegram

🎉 S&P 500 scan complete!
```

### Telegram Alert

```
📰 S&P 500 News Scan
2025-11-17 18:00

Scanned: 503 stocks
Found: 23 opportunities

━━━━━━━━━━━━━━━━━━━━

1. NVDA 🟢
NVIDIA Corporation
Score: 92/100
• Price: $485.20 (-8.5%)
• From 52W High: 12.3%
• P/E: 42.5
📰 NVIDIA falls on earnings concerns...

2. META 🟢
Meta Platforms, Inc.
Score: 88/100
• Price: $324.50 (-7.2%)
• From 52W High: 9.8%
• P/E: 24.1

...and 21 more opportunities

━━━━━━━━━━━━━━━━━━━━

💡 Next Steps:
• Review top picks
• Run technical analysis
• Check charts & support levels

⚠️ Not financial advice. DYOR.
```

---

## Performance

### Scan Speed

- **Sequential**: ~0.5-1 second per stock
- **Full S&P 500**: 5-10 minutes
- **Sector (50 stocks)**: 1-2 minutes
- **Test (10 stocks)**: 10-20 seconds

### Rate Limits

- yfinance has rate limits
- Sequential scanning avoids hitting limits
- If you get errors, wait a few minutes and retry

---

## Tips

### Finding the Best Opportunities

1. **Run weekly** - Sunday evening before market opens
2. **Filter by sector** - Focus on sectors you understand
3. **Check top 10** - Usually the best opportunities
4. **Verify fundamentals** - Always DYOR before buying
5. **Use technical analysis** - Run on-demand analysis on interesting picks

### Combining with Daily Portfolio Scan

1. **Daily**: Scan your portfolio symbols (5-10 stocks, fast)
2. **Weekly**: Scan S&P 500 (500 stocks, comprehensive)
3. **Strong signals**: Stocks appearing in both scans

### Sector Rotation Strategy

```bash
# Week 1: Tech
python scripts/scan_sp500_news.py --sector "Information Technology"

# Week 2: Healthcare
python scripts/scan_sp500_news.py --sector "Health Care"

# Week 3: Financials
python scripts/scan_sp500_news.py --sector "Financials"

# Week 4: All sectors
python scripts/scan_sp500_news.py
```

---

## Troubleshooting

### "S&P 500 list not found"

```bash
# Fetch the list first
python scripts/fetch_sp500_list.py
```

### "Rate limit exceeded"

- Wait 5-10 minutes
- Try with `--top 50` to test
- Run during off-peak hours

### "Module 'tqdm' not found"

```bash
pip install tqdm
```

### Scan taking too long

- This is normal for 500 stocks
- Use `--sector` to scan fewer stocks
- Use `--top 50` for quick testing

---

## Files

### Generated Files

- `data/sp500_symbols.json` - Current S&P 500 constituents
- `signals/sp500_opportunities.json` - Scan results

### Scripts

- `scripts/fetch_sp500_list.py` - Fetch S&P 500 list
- `scripts/scan_sp500_news.py` - Scan for opportunities
- `.github/workflows/weekly-sp500-scan.yml` - Automation

---

## Real-World Example

**Scenario: Market pullback, want to find bargains**

```bash
# 1. Update S&P 500 list (in case constituents changed)
python scripts/fetch_sp500_list.py

# 2. Scan for opportunities
python scripts/scan_sp500_news.py

# 3. Results: 23 opportunities found
#    - Top pick: NVDA (92/100)
#    - Strong fundamentals
#    - -8.5% dip
#    - No red flags

# 4. Run technical analysis
# Via GitHub Actions: On-Demand Analysis → NVDA

# 5. Review charts and make decision
```

---

## Advanced Options

### Custom Batch Size

```python
# In scan_sp500_news.py
python scripts/scan_sp500_news.py --batch-size 100
```

### Skip Telegram

```bash
python scripts/scan_sp500_news.py --no-telegram
```

### Combine with Backtesting

1. Find opportunity from S&P 500 scan
2. Fetch historical data
3. Run backtest
4. Review performance before buying

---

## FAQ

**Q: How often should I run this?**  
A: Weekly is ideal. GitHub Actions runs every Sunday automatically.

**Q: Can I scan NASDAQ-100 instead?**  
A: Yes, modify `fetch_sp500_list.py` to use a different Wikipedia URL.

**Q: Does this scan penny stocks?**  
A: No, only S&P 500 constituents (large-cap stocks).

**Q: Can I filter by market cap?**  
A: Not built-in, but you can modify the script to add this filter.

**Q: Why Sunday scans?**  
A: Gives you all day Monday to research opportunities before market opens.

---

## Integration

### With Daily Portfolio Scan

```yaml
Daily (Mon-Fri):
- 9:00 AM - Scan portfolio symbols
- 4:30 PM - Scan portfolio symbols

Weekly (Sunday):
- 6:00 PM - Scan S&P 500 (all 500 stocks)

Result: Best of both worlds
- Daily: Quick, focused
- Weekly: Comprehensive, discover new opportunities
```

---

## Dependencies

```bash
pip install -r requirements-base.txt
pip install -r requirements-fetch.txt
pip install tqdm lxml html5lib beautifulsoup4
```

---

## Next Steps

1. ✅ Fetch S&P 500 list
2. ✅ Run test scan (10 stocks)
3. ✅ Run sector scan
4. ✅ Run full S&P 500 scan
5. ✅ Review opportunities
6. ✅ Enable weekly automation

---

**⚠️ Disclaimer**: Not financial advice. Always do your own research and consult with a financial advisor before making investment decisions.

