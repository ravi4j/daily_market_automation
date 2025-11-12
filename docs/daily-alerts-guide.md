# 🚨 Daily Trading Alerts Guide

Complete guide to automated daily trading alerts with buy/sell signals.

## Table of Contents
- [Quick Start](#quick-start)
- [How It Works](#how-it-works)
- [Available Strategies](#available-strategies)
- [Setup Automation](#setup-automation)
- [Customization](#customization)

---

## Quick Start

### Run Locally (Manual)

```bash
# 1. Run strategy analysis
python src/strategy_runner.py

# 2. View alerts
cat signals/daily_alerts.json

# 3. Send via Telegram (optional)
export TELEGRAM_BOT_TOKEN="your_token"
export TELEGRAM_CHAT_ID="your_chat_id"
python scripts/send_daily_alerts.py
```

### Setup Daily Automation

1. **Configure GitHub Secrets** (one-time setup):
   - Go to: Repository → Settings → Secrets → Actions
   - Add `TELEGRAM_BOT_TOKEN`
   - Add `TELEGRAM_CHAT_ID`
   - See [Telegram Setup Guide](telegram-setup.md)

2. **Enable Workflow**:
   - Workflow runs automatically every weekday at 4:30 PM EST
   - Or trigger manually: Actions → Daily Trading Alerts → Run workflow

3. **Done!** You'll receive alerts via Telegram daily

---

## How It Works

### 1. Data Collection (4:30 PM EST)
```
Market closes → Fetch latest prices → Update CSV files
```

### 2. Strategy Analysis
```
For each symbol:
  ├── Load price data + indicators
  ├── Run Strategy 1: RSI + MACD Confluence
  ├── Run Strategy 2: Trend Following  
  ├── Run Strategy 3: BB Mean Reversion
  ├── Run Strategy 4: Momentum Breakout
  └── Generate alerts (BUY/SELL/HOLD)
```

### 3. Alert Generation
```
Alerts include:
├── Symbol & Price
├── Signal (BUY/SELL)
├── Strategy name
├── Confidence (HIGH/MEDIUM/LOW)
├── Reason (why the signal was triggered)
└── Technical data (RSI, MACD, ADX, etc.)
```

### 4. Notification (Telegram)
```
Send to your phone:
├── Summary (total alerts, BUY/SELL count)
├── HIGH confidence alerts first
└── Individual alert details
```

---

## Available Strategies

### Strategy 1: RSI + MACD Confluence

**What it does:** Finds oversold/overbought conditions confirmed by MACD

**BUY Signal:**
- RSI < 35 (oversold)
- MACD crosses above signal line
- ADX > 20 (trending)

**SELL Signal:**
- RSI > 65 (overbought)
- MACD crosses below signal line

**Best for:** Mean reversion trades, catching reversals

**Example:**
```
🟢 BUY ALERT - AAPL

Symbol: AAPL
Price: $150.25
Strategy: RSI+MACD Confluence
Confidence: HIGH ⭐⭐⭐

Reason:
• RSI is oversold at 28.50 (< 35)
• MACD just crossed above signal line
• ADX shows strong trend at 26.30

Technical Data:
• RSI: 28.50
• MACD: -1.25
• Signal: -1.50
• ADX: 26.30
```

---

### Strategy 2: Trend Following

**What it does:** Identifies strong trends and trend reversals

**BUY Signal:**
- Price > SMA20 > SMA50 > SMA200 (uptrend)
- RSI between 40-70 (healthy momentum)
- ADX > 25 (strong trend)

**SELL Signal:**
- Price falls below SMA20 (trend broken)
- OR RSI < 35 (momentum lost)

**Best for:** Riding strong trends, avoiding choppy markets

**Example:**
```
🟢 BUY ALERT - TQQQ

Symbol: TQQQ
Price: $65.80
Strategy: Trend Following
Confidence: HIGH ⭐⭐⭐

Reason:
• Strong uptrend: Price > SMA20 > SMA50 > SMA200
• Price is 3.50% above SMA20
• RSI healthy at 58.20 (not overbought)
• ADX confirms strong trend at 32.10

Technical Data:
• Price: 65.80
• SMA20: 63.50
• SMA50: 60.25
• SMA200: 55.10
• RSI: 58.20
• ADX: 32.10
```

---

### Strategy 3: Bollinger Band Mean Reversion

**What it does:** Finds oversold/overbought extremes for reversals

**BUY Signal:**
- Price at/below lower Bollinger Band
- RSI < 40
- Volume spike (optional)

**SELL Signal:**
- Price at/above upper Bollinger Band
- RSI > 60

**Best for:** Range-bound markets, quick reversions

**Example:**
```
🟢 BUY ALERT - UBER

Symbol: UBER
Price: $48.20
Strategy: BB Mean Reversion
Confidence: MEDIUM ⭐⭐

Reason:
• Price at lower Bollinger Band (-0.50% from band)
• RSI oversold at 35.20
• Volume 1.80x average (potential reversal)
• Mean reversion opportunity to $51.50

Technical Data:
• Price: 48.20
• Lower_Band: 48.45
• Middle_Band: 51.50
• Upper_Band: 54.55
• RSI: 35.20
• Volume_Ratio: 1.80
```

---

### Strategy 4: Momentum Breakout

**What it does:** Catches breakouts above resistance or below support

**BUY Signal:**
- Price breaks above 20-day high
- Volume > 1.5x average
- ADX > 25 (trending)

**SELL Signal:**
- Price breaks below 20-day low
- OR RSI < 30

**Best for:** Capturing momentum moves, new highs/lows

**Example:**
```
🟢 BUY ALERT - AAPL

Symbol: AAPL
Price: $152.50
Strategy: Momentum Breakout
Confidence: HIGH ⭐⭐⭐

Reason:
• Breakout: Price surpassed 20-day high ($150.20)
• Breakout size: 1.53%
• Volume spike: 2.30x average (strong confirmation)
• ADX at 28.50 confirms strong trend
• Potential continuation to new highs

Technical Data:
• Price: 152.50
• 20D_High: 150.20
• Breakout_%: 1.53
• Volume_Ratio: 2.30
• ADX: 28.50
• RSI: 62.10
```

---

## Setup Automation

### Method 1: GitHub Actions (Recommended)

**Advantages:**
- ✅ Fully automated
- ✅ Runs daily after market close
- ✅ No server needed
- ✅ Free for public repos

**Setup:**

1. **Get Telegram Credentials** ([Full Guide](telegram-setup.md)):
   ```bash
   # Create bot with @BotFather
   # Get your chat ID from @userinfobot
   ```

2. **Add GitHub Secrets**:
   - Repository → Settings → Secrets → Actions
   - New secret: `TELEGRAM_BOT_TOKEN` = your bot token
   - New secret: `TELEGRAM_CHAT_ID` = your chat ID

3. **Enable Workflow**:
   - File: `.github/workflows/daily-alerts.yml`
   - Already configured to run at 4:30 PM EST weekdays
   - Or manually: Actions → Daily Trading Alerts → Run workflow

4. **Done!** Alerts will be sent automatically

**Schedule:**
```yaml
# Runs Monday-Friday at 4:30 PM EST (after market close)
schedule:
  - cron: '30 21 * * 1-5'  # 9:30 PM UTC = 4:30 PM EST
```

---

### Method 2: Local Cron Job

**Advantages:**
- ✅ Full control
- ✅ Can customize timing
- ✅ Runs on your machine

**Setup (Mac/Linux):**

1. **Create wrapper script** (`run_daily_alerts.sh`):
   ```bash
   #!/bin/bash
   cd /path/to/daily_market_automation
   source .venv/bin/activate
   
   # Set credentials
   export TELEGRAM_BOT_TOKEN="your_token"
   export TELEGRAM_CHAT_ID="your_chat_id"
   
   # Fetch latest data
   python src/fetch_daily_prices.py
   
   # Run strategies and send alerts
   python scripts/send_daily_alerts.py --min-confidence MEDIUM
   ```

2. **Make executable**:
   ```bash
   chmod +x run_daily_alerts.sh
   ```

3. **Add to crontab**:
   ```bash
   crontab -e
   
   # Add this line (runs Mon-Fri at 4:30 PM)
   30 16 * * 1-5 /path/to/run_daily_alerts.sh >> /path/to/alerts.log 2>&1
   ```

4. **Test**:
   ```bash
   ./run_daily_alerts.sh
   ```

---

## Customization

### Change Confidence Level

```bash
# Only HIGH confidence alerts
python scripts/send_daily_alerts.py --min-confidence HIGH

# All alerts (including LOW confidence)
python scripts/send_daily_alerts.py --min-confidence LOW
```

### Run Specific Strategies

```bash
# Only trend following
python scripts/send_daily_alerts.py --strategies trend_following

# Multiple strategies
python scripts/send_daily_alerts.py --strategies rsi_macd trend_following
```

### Add Your Own Strategy

Edit `src/strategy_runner.py`:

```python
def strategy_my_custom(self, symbol: str, df: pd.DataFrame) -> Optional[TradingAlert]:
    """Your custom strategy"""
    
    # Add indicators
    indicators = TechnicalIndicators(df)
    indicators.add_rsi(14)
    indicators.add_ema(50)
    
    df = indicators.df
    latest = df.iloc[-1]
    
    # Your logic
    if latest['RSI_14'] < 30 and latest['Close'] > latest['EMA_50']:
        return TradingAlert(
            symbol=symbol,
            signal='BUY',
            strategy_name='My Custom Strategy',
            confidence='HIGH',
            price=latest['Close'],
            timestamp=datetime.now().isoformat(),
            reason="Your reason here",
            technical_data={'RSI': latest['RSI_14']}
        )
    
    return None
```

Then register it:

```python
# In run_daily_analysis method
available_strategies = {
    'rsi_macd': self.strategy_rsi_macd_confluence,
    'trend_following': self.strategy_trend_following,
    'mean_reversion': self.strategy_bollinger_mean_reversion,
    'momentum_breakout': self.strategy_momentum_breakout,
    'my_custom': self.strategy_my_custom  # Add your strategy
}
```

### Modify Alert Format

Edit `TradingAlert.to_telegram_message()` in `src/strategy_runner.py`:

```python
def to_telegram_message(self) -> str:
    """Customize your alert format"""
    msg = f"🚨 {self.signal} - {self.symbol} @ ${self.price:.2f}\n"
    msg += f"Strategy: {self.strategy_name}\n"
    # Add your custom formatting...
    return msg
```

---

## Example Telegram Messages

### Summary Message
```
🚨 DAILY TRADING ALERTS 🚨

Total Alerts: 5
  🟢 BUY: 3
  🔴 SELL: 2

High Confidence: ⭐⭐⭐ 2

Detailed alerts follow...
```

### Individual Alert
```
🟢 BUY ALERT 🟢

Symbol: AAPL
Price: $150.25
Strategy: RSI+MACD Confluence
Confidence: HIGH ⭐⭐⭐

Reason:
• RSI is oversold at 28.50 (< 35)
• MACD just crossed above signal line
• ADX shows strong trend at 26.30

Technical Data:
  • RSI: 28.50
  • MACD: -1.25
  • Signal: -1.50
  • ADX: 26.30
  • Volume: 85432100

Time: 2025-11-11T16:30:00
```

### No Alerts Message
```
✅ Daily Market Analysis Complete

No trading alerts today.
All positions hold steady.

Analyzed: TQQQ, AAPL, UBER, SP500
```

---

## Alerts JSON Format

Stored in `signals/daily_alerts.json`:

```json
{
  "generated_at": "2025-11-11T16:30:00",
  "total_alerts": 2,
  "buy_signals": 1,
  "sell_signals": 1,
  "alerts": [
    {
      "symbol": "AAPL",
      "signal": "BUY",
      "strategy_name": "RSI+MACD Confluence",
      "confidence": "HIGH",
      "price": 150.25,
      "timestamp": "2025-11-11T16:30:00",
      "reason": "• RSI is oversold at 28.50...",
      "technical_data": {
        "RSI": 28.50,
        "MACD": -1.25,
        "Signal": -1.50,
        "ADX": 26.30
      }
    }
  ]
}
```

---

## FAQ

**Q: When do alerts run?**
A: By default, 4:30 PM EST on weekdays (after market close).

**Q: Can I change the timing?**
A: Yes, edit the `cron` schedule in `.github/workflows/daily-alerts.yml`

**Q: Do I need Telegram?**
A: No, alerts are saved to `signals/daily_alerts.json` even without Telegram.

**Q: Can I get alerts via email?**
A: Yes, modify `scripts/send_daily_alerts.py` to use email instead of Telegram.

**Q: How do I test without waiting for 4:30 PM?**
A: Run manually: `python src/strategy_runner.py`

**Q: Can I add more symbols?**
A: Yes, just add CSV files to `data/` folder. Auto-discovered!

**Q: Are these financial advice?**
A: NO! These are algorithmic signals for educational purposes only.

---

## Risk Disclaimer

⚠️ **IMPORTANT:**

- Alerts are algorithmic signals, NOT financial advice
- Past performance ≠ future results
- Always do your own research
- Never risk more than you can afford to lose
- Test strategies before using real money
- Consider consulting a financial advisor

---

## Quick Commands

```bash
# Run analysis manually
python src/strategy_runner.py

# Send alerts to Telegram
python scripts/send_daily_alerts.py

# View generated alerts
cat signals/daily_alerts.json | python -m json.tool

# Test a specific strategy
python src/strategy_runner.py --strategies trend_following

# HIGH confidence only
python scripts/send_daily_alerts.py --min-confidence HIGH
```

---

## Next Steps

1. ✅ Test locally: `python src/strategy_runner.py`
2. ✅ Setup Telegram bot (5 minutes)
3. ✅ Add GitHub Secrets
4. ✅ Enable workflow
5. ✅ Receive daily alerts! 🎉

**Happy Trading! 📈**

