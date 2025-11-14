# 🔍 On-Demand Symbol Analysis

Analyze any stock symbol instantly and get comprehensive technical analysis delivered to Telegram!

## 🎯 What It Does

When you trigger an on-demand analysis, the system:
1. ✅ Fetches latest price data for the symbol
2. ✅ Calculates 50+ technical indicators
3. ✅ Runs 8+ trading strategies
4. ✅ Generates BUY/SELL/HOLD recommendation
5. ✅ Sends detailed report to Telegram
6. ✅ (Optional) Adds symbol to daily tracking

## 🚀 How to Use

### Step 1: Go to GitHub Actions

Visit your workflow page:
```
https://github.com/YOUR_USERNAME/daily_market_automation/actions/workflows/on-demand-analysis.yml
```

Or navigate through GitHub:
1. Go to your repository
2. Click **"Actions"** tab
3. Click **"On-Demand Symbol Analysis"** in the left sidebar

### Step 2: Trigger Analysis

1. Click **"Run workflow"** button (top right)
2. Enter the symbol (e.g., `NVDA`, `TSLA`, `MSFT`)
3. (Optional) Check **"Add to daily tracking"** if you want it tracked daily
4. Click **"Run workflow"**

### Step 3: Wait for Results

- ⏱️ Takes 1-2 minutes to complete
- 📱 Results sent to Telegram automatically
- 📊 Full report available as workflow artifact

## 📱 Example Telegram Output

```
🔍 On-Demand Analysis: NVDA

NVIDIA Corporation
💰 Current Price: $485.32

📊 Price Changes:
  🟢 1 Day    : +2.45%
  🟢 5 Days   : +5.67%
  🟢 1 Month  : +12.34%

📈 Technical Indicators:
  • RSI: 58.2
  • MACD: 2.145 / Signal: 1.892
  • ADX: 32.5 (Strong trend)
  • SMA 20: $478.50
  • SMA 50: $465.20
  • SMA 200: $420.15
  • BB Range: $470.25 - $490.80
  • Volume: 45,234,567 (1.8x avg)

🎯 Signals Detected:
  📊 3 BUY signals, 0 SELL signals

  🟢 Strong Uptrend ⭐⭐⭐
     Price > SMA20 > SMA50 > SMA200 (ADX: 32.5)
  🟢 MACD Bullish ⭐⭐⭐
     MACD above signal line and positive
  🟢 Volume Surge ⭐⭐
     High volume with price increase

💡 Recommendation: 🟢 BUY ⭐⭐⭐
Confidence: HIGH

📅 Analysis based on 252 days
Period: 2024-11-14 to 2025-11-14
```

## 🎨 Supported Symbols

You can analyze:
- ✅ **Stocks**: AAPL, MSFT, GOOGL, TSLA, etc.
- ✅ **ETFs**: SPY, QQQ, TQQQ, VOO, etc.
- ✅ **Indices**: ^GSPC (S&P 500), ^DJI (Dow), ^IXIC (NASDAQ)
- ✅ **Any ticker on Yahoo Finance**

## 📊 What Gets Analyzed

### Technical Indicators Calculated
- **Momentum**: RSI, MACD, Stochastic
- **Trend**: SMA (20/50/200), EMA (12/26), ADX
- **Volatility**: Bollinger Bands, ATR
- **Volume**: Volume SMA, relative volume

### Strategies Applied
1. **RSI Oversold/Overbought** - Entry/exit based on RSI levels
2. **MACD Bullish/Bearish** - MACD crossovers and divergences
3. **Trend Following** - Moving average alignment
4. **Bollinger Band Bounce** - Mean reversion plays
5. **Volume Analysis** - Volume confirmation
6. **Multi-indicator Confirmation** - Combined signals

### Recommendation Logic
- **BUY**: 2+ buy signals from different strategies
- **SELL**: 2+ sell signals from different strategies  
- **HOLD**: Mixed signals or insufficient confidence
- **Confidence**: Based on signal strength and agreement

## ⚙️ Advanced Usage

### Add to Daily Tracking Automatically

When you check **"Add to daily tracking"**, the system will:
1. Add the symbol to `config/symbols.yaml`
2. Include it in daily analysis from tomorrow onwards
3. Send daily alerts for this symbol

### View Full Analysis Report

After the workflow completes:
1. Click on the workflow run
2. Scroll to **"Artifacts"**
3. Download `analysis-SYMBOL` 
4. Open the JSON file for detailed data

### Run from Command Line (Advanced)

If you have GitHub CLI installed:

```bash
# Install GitHub CLI
brew install gh  # macOS
# or download from: https://cli.github.com/

# Authenticate
gh auth login

# Trigger analysis
gh workflow run on-demand-analysis.yml \
  -f symbol=NVDA \
  -f add_to_tracking=false

# With auto-add to tracking
gh workflow run on-demand-analysis.yml \
  -f symbol=TSLA \
  -f add_to_tracking=true
```

## 🎯 Use Cases

### Research New Stocks
```
1. Hear about a hot stock (e.g., PLTR)
2. Trigger on-demand analysis
3. Get instant technical analysis
4. Decide if you want to track it daily
```

### Quick Position Check
```
1. Want to check a stock you don't track
2. Run analysis without adding to config
3. Get BUY/SELL/HOLD recommendation
4. Make informed decision
```

### Build Your Watchlist
```
1. Analyze multiple interesting symbols
2. Check "Add to tracking" for winners
3. Automatically get daily alerts
4. Build personalized portfolio tracking
```

## 🔧 Setup Requirements

### Required (for Telegram alerts)
- GitHub Secrets configured:
  - `TELEGRAM_BOT_TOKEN`
  - `TELEGRAM_CHAT_ID`
- See [Telegram Setup Guide](telegram-setup.md)

### Optional
- GitHub CLI for command-line triggering
- Nothing else needed! Runs in GitHub Actions

## 💡 Pro Tips

1. **Test before tracking** - Analyze a symbol first, then add to daily tracking if you like it
2. **Compare multiple symbols** - Run analysis on 3-4 similar stocks to compare
3. **Check after market close** - Most accurate analysis after 4:00 PM EST
4. **Review workflow logs** - Click on the run to see detailed execution
5. **Download artifacts** - JSON files have even more detailed data

## 🚨 Troubleshooting

### "Symbol not found"
- Check spelling (use ticker symbols, not company names)
- Try Yahoo Finance first to verify the symbol
- Indices need `^` prefix (e.g., `^GSPC`)

### "Telegram not configured"
- Analysis still works and saves to artifacts
- Just won't send to Telegram
- See [Telegram Setup Guide](telegram-setup.md)

### "Analysis failed"
- Check workflow logs for details
- Symbol may not have enough historical data
- Try a different period or symbol

## 📚 Related Documentation

- [Telegram Setup Guide](telegram-setup.md) - Configure Telegram bot
- [Daily Alerts Guide](daily-alerts-guide.md) - Automated daily tracking
- [Strategy Testing](STRATEGY_TESTING_GUIDE.md) - Backtest strategies
- [Config Guide](../config/README.md) - Managing your portfolio

## 🎉 Example Workflow

**Monday Morning**: Hear about a hot stock on social media
```
Symbol: NVDA
Action: Run on-demand analysis
Result: Get technical analysis in 2 minutes
```

**Result is BUY ⭐⭐⭐**: Looks good!
```
Action: Re-run with "Add to tracking" checked
Result: Now tracked daily, get alerts automatically
```

**Daily**: NVDA reaches new levels
```
Action: Nothing! System automatically analyzes
Result: Telegram alert if BUY/SELL signal triggered
```

---

**Ready to analyze your first symbol?** [Go to Actions →](../../actions/workflows/on-demand-analysis.yml)

