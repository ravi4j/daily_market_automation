# Telegram Integration Guide 📱

Get your trading signals delivered directly to Telegram - **NO SERVER NEEDED**!

## 🚀 Quick Setup (5 Minutes)

### Step 1: Create Your Telegram Bot

1. Open Telegram and search for **@BotFather**
2. Send `/newbot` command
3. Follow the prompts:
   - Choose a name (e.g., "Market Signals Bot")
   - Choose a username (e.g., "my_signals_bot")
4. **Copy the bot token** (looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### Step 2: Get Your Chat ID

**Option A: Using @userinfobot**
1. Search for **@userinfobot** on Telegram
2. Start a chat with it
3. It will send you your **Chat ID** (a number like: `123456789`)

**Option B: Using your bot**
1. Search for your bot username on Telegram
2. Start a chat with it (send `/start`)
3. Run this command:
   ```bash
   curl "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates"
   ```
4. Look for `"chat":{"id":123456789}` in the response

### Step 3: Set Up Environment Variables

**macOS/Linux:**
```bash
# Add to your ~/.zshrc or ~/.bashrc
export TELEGRAM_BOT_TOKEN="123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
export TELEGRAM_CHAT_ID="123456789"
export GITHUB_REPO="your-username/daily_market_automation"

# Reload shell
source ~/.zshrc  # or source ~/.bashrc
```

**Windows (PowerShell):**
```powershell
$env:TELEGRAM_BOT_TOKEN="123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
$env:TELEGRAM_CHAT_ID="123456789"
$env:GITHUB_REPO="your-username/daily_market_automation"
```

### Step 4: Install Requests (if not already installed)

```bash
pip install requests
```

### Step 5: Test It!

```bash
# Send signals to Telegram
python scripts/send_telegram_signals.py
```

You should receive a message in Telegram with your trading signals! 🎉

---

## 📋 Usage Examples

### Basic Usage
```bash
# Send all signals
python scripts/send_telegram_signals.py

# Or with explicit credentials (if env vars not set)
python scripts/send_telegram_signals.py --token YOUR_TOKEN --chat YOUR_CHAT_ID --repo username/repo
```

### Advanced Filtering
```bash
# Only send high-confidence signals (score >= 5)
python scripts/send_telegram_signals.py --min-score 5

# Only send from a specific repo/branch
python scripts/send_telegram_signals.py --repo username/repo --branch develop
```

---

## 🤖 Automate Daily Telegram Notifications

### Option 1: Local Cron Job (Mac/Linux)

```bash
# Edit crontab
crontab -e

# Add this line (sends signals at 6 PM daily)
0 18 * * 1-5 cd /path/to/daily_market_automation && source .venv/bin/activate && python scripts/send_telegram_signals.py
```

### Option 2: GitHub Actions (Best for public repos!)

Add to `.github/workflows/daily-charts.yml` after the signal export step:

```yaml
- name: Send signals to Telegram
  if: always()
  env:
    TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
    TELEGRAM_CHAT_ID: ${{ secrets.TELEGRAM_CHAT_ID }}
    GITHUB_REPO: ${{ github.repository }}
  run: |
    pip install requests
    python scripts/send_telegram_signals.py
```

**Set GitHub Secrets:**
1. Go to repo Settings → Secrets and variables → Actions
2. Add secrets:
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHAT_ID`

### Option 3: Windows Task Scheduler

1. Open Task Scheduler
2. Create Basic Task → Name it "Telegram Signals"
3. Trigger: Daily at 6:00 PM
4. Action: Start a Program
   - Program: `C:\Python\python.exe`
   - Arguments: `scripts\send_telegram_signals.py`
   - Start in: `C:\path\to\daily_market_automation`

---

## 📱 Message Format

Your Telegram messages will look like this:

```
📊 Trading Signals Report
🕐 Generated: 2025-11-10 05:30 PM

📈 Summary:
• Symbols Analyzed: 4
• Confirmed Breakouts: 2
  🟢 BUY: 1
  🔴 SELL: 1
  ⚪ WATCH: 0

🎯 Actionable Signals:

🟢 BUY: AAPL
💵 Price: $225.50
⭐ Score: 6/6
📊 Volume: 1.45x avg
📈 Trend: UPTREND
🎯 Type: RESISTANCE_BREAK_CONFIRMED
📉 Support: $210.25
📈 Resistance: $225.00

🔴 SELL: TQQQ
💵 Price: $110.03
⭐ Score: 5/6
📊 Volume: 1.15x avg
📈 Trend: UPTREND
🎯 Type: BEARISH_TRENDLINE_BREAKOUT_CONFIRMED
📉 Support: $97.07
📈 Resistance: $121.37

────────────────────
🔗 View details: JSON
```

---

## 🎯 Pro Tips

### 1. **Create Multiple Bots for Different Strategies**
```bash
# Conservative signals (score >= 5)
python scripts/send_telegram_signals.py --token BOT1_TOKEN --chat CHAT_ID --min-score 5

# All signals
python scripts/send_telegram_signals.py --token BOT2_TOKEN --chat CHAT_ID
```

### 2. **Send to Telegram Channel**
- Create a public/private channel
- Add your bot as administrator
- Use channel username as chat ID: `@your_channel`

### 3. **Group Notifications**
- Create a Telegram group
- Add your bot to the group
- Get group chat ID (will be negative, like `-123456789`)
- Use group ID as `TELEGRAM_CHAT_ID`

### 4. **Morning Reminder**
Set up a second cron job to remind you to check signals:
```bash
# 8 AM reminder to check signals
0 8 * * 1-5 python scripts/send_telegram_signals.py
```

---

## 🔒 Security Best Practices

✅ **DO:**
- Use environment variables for credentials
- Use GitHub Secrets for GitHub Actions
- Keep bot token private (never commit to repo)
- Use private Telegram groups for sensitive signals

❌ **DON'T:**
- Hardcode tokens in scripts
- Share bot tokens publicly
- Commit `.env` files with credentials
- Use bots for automated trading without proper safeguards

---

## 🛠️ Troubleshooting

### "Failed to send Telegram message"
- Check bot token is correct
- Verify chat ID is correct
- Make sure you've started a chat with the bot (send `/start`)

### "Failed to fetch signals"
- Check GitHub repo name is correct (format: `username/repo`)
- Verify repo is public or you have access
- Check internet connection
- Verify `data/trading_signals.json` exists in repo

### Bot not responding
- Make sure bot is not blocked
- Verify bot token is active (@BotFather)
- Check bot has permission to send messages

### No signals received
- Run script manually to see error messages
- Check if signals exist: `curl https://raw.githubusercontent.com/USER/REPO/main/data/trading_signals.json`
- Verify environment variables are set: `echo $TELEGRAM_BOT_TOKEN`

---

## 🌟 Alternative: IFTTT Integration (No Coding!)

1. Create IFTTT account (free)
2. Create applet:
   - **IF**: RSS Feed → New feed item
   - **Feed URL**: `https://github.com/USER/REPO/commits/main.atom`
   - **THEN**: Telegram → Send message
3. Applet triggers on new commits (including signal updates)

---

## 📚 Additional Resources

- [Telegram Bot API Documentation](https://core.telegram.org/bots/api)
- [BotFather Commands](https://core.telegram.org/bots#6-botfather)
- [Python Telegram Bot Library](https://github.com/python-telegram-bot/python-telegram-bot) (for advanced features)

---

**Need help?** Open an issue in the repo with your question! 🚀
