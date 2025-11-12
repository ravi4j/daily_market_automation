# 🚨 Daily Trading Alerts - Quick Start

Get automated BUY/SELL alerts on your phone after market close!

## 📱 5-Minute Setup

### Step 1: Test Locally (1 min)

```bash
# Run strategy analysis
python src/strategy_runner.py

# View results
cat signals/daily_alerts.json | python -m json.tool
```

You should see alerts like:
```json
{
  "symbol": "AAPL",
  "signal": "BUY",
  "confidence": "HIGH",
  "price": 269.46,
  "technical_data": {
    "RSI": 64.97,
    "ADX": 30.47
  }
}
```

✅ If it works, continue to Step 2!

---

### Step 2: Setup Telegram Bot (2 min)

1. **Open Telegram** and search for `@BotFather`

2. **Create bot:**
   ```
   /newbot
   YourBotName
   yourbot_bot
   ```

3. **Copy token:** `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`

4. **Get chat ID:**
   - Search for `@userinfobot` in Telegram
   - Send any message
   - Copy your ID: `1234567890`

---

### Step 3: Test Telegram (1 min)

```bash
# Set credentials
export TELEGRAM_BOT_TOKEN="123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
export TELEGRAM_CHAT_ID="1234567890"

# Send test alert
python scripts/send_daily_alerts.py
```

✅ Check your phone - you should receive messages!

---

### Step 4: Automate with GitHub (1 min)

1. **Go to:** Your Repo → Settings → Secrets → Actions

2. **Add secrets:**
   - Name: `TELEGRAM_BOT_TOKEN`, Value: (your token)
   - Name: `TELEGRAM_CHAT_ID`, Value: (your chat ID)

3. **Done!** Workflow runs automatically at 4:30 PM EST weekdays

---

## 🎯 What You Get

### Daily at 4:30 PM EST:

**1. Summary Message:**
```
🚨 DAILY TRADING ALERTS 🚨

Total Alerts: 3
  🟢 BUY: 2
  🔴 SELL: 1

High Confidence: ⭐⭐⭐ 1

Detailed alerts follow...
```

**2. Individual Alerts:**
```
🟢 BUY ALERT 🟢

Symbol: AAPL
Price: $269.46
Strategy: Trend Following
Confidence: HIGH ⭐⭐⭐

Reason:
• Strong uptrend: Price > SMA20 > SMA50 > SMA200
• Price is 2.28% above SMA20
• RSI healthy at 64.97 (not overbought)
• ADX confirms strong trend at 30.47

Technical Data:
  • Price: 269.46
  • SMA20: 263.45
  • RSI: 64.97
  • ADX: 30.47
```

---

## 🎓 4 Strategies Included

1. **RSI + MACD Confluence**
   - Finds oversold/overbought with momentum confirmation
   - Best for: Catching reversals

2. **Trend Following**
   - Identifies strong trends using SMA alignment
   - Best for: Riding momentum

3. **BB Mean Reversion**
   - Catches price extremes at Bollinger Bands
   - Best for: Range-bound markets

4. **Momentum Breakout**
   - Detects breakouts above 20-day highs
   - Best for: Capturing new trends

All strategies run automatically every day!

---

## ⚙️ Customization

### Change Confidence Level

```bash
# Only HIGH confidence alerts
python scripts/send_daily_alerts.py --min-confidence HIGH

# All alerts (including LOW)
python scripts/send_daily_alerts.py --min-confidence LOW
```

### Run Specific Strategies

```bash
# Only trend following
python scripts/send_daily_alerts.py --strategies trend_following

# Multiple strategies
python scripts/send_daily_alerts.py --strategies rsi_macd momentum_breakout
```

### Change Schedule

Edit `.github/workflows/daily-alerts.yml`:

```yaml
schedule:
  # Current: 4:30 PM EST (Mon-Fri)
  - cron: '30 21 * * 1-5'

  # Example: 5:00 PM EST (Mon-Fri)
  - cron: '0 22 * * 1-5'
```

---

## 📊 Sample Results

Based on current data:

| Symbol | Signal | Strategy | Confidence | Price |
|--------|--------|----------|------------|-------|
| 🟢 AAPL | BUY | Trend Following | MEDIUM | $269.46 |
| 🔴 TQQQ | SELL | Trend Following | MEDIUM | $110.03 |
| 🔴 UBER | SELL | Trend Following | MEDIUM | $92.39 |

---

## 🔧 Troubleshooting

### Not receiving messages?

```bash
# Test Telegram connection
curl -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMessage" \
  -d "chat_id=$TELEGRAM_CHAT_ID" \
  -d "text=Test message"
```

### No alerts generated?

```bash
# Check if data is up to date
python src/fetch_daily_prices.py

# Run with verbose output
python src/strategy_runner.py
```

### GitHub Actions not running?

- Check: Actions tab → Daily Trading Alerts
- Verify: Secrets are added (Settings → Secrets)
- Check: Workflow is enabled (green checkmark)

---

## 📚 Full Documentation

- **Complete Guide:** [docs/daily-alerts-guide.md](docs/daily-alerts-guide.md)
- **Telegram Setup:** [docs/telegram-setup.md](docs/telegram-setup.md)
- **GitHub Secrets:** [docs/github-secrets-setup.md](docs/github-secrets-setup.md)

---

## ⚠️ Disclaimer

These are algorithmic signals for **educational purposes only**, not financial advice.

- Always do your own research
- Never risk more than you can afford to lose
- Past performance ≠ future results
- Consider consulting a financial advisor

---

## ✅ Quick Commands Cheat Sheet

```bash
# Run analysis locally
python src/strategy_runner.py

# Send to Telegram
python scripts/send_daily_alerts.py

# View alerts
cat signals/daily_alerts.json

# HIGH confidence only
python scripts/send_daily_alerts.py --min-confidence HIGH

# Test Telegram
echo "Test" | curl -X POST \
  "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMessage" \
  -d "chat_id=$TELEGRAM_CHAT_ID" \
  -d "text=Test from terminal"
```

---

**🎉 You're all set! You'll now receive daily trading alerts automatically!**
