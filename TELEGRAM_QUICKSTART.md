# 📱 Telegram Quick Start (5 Minutes)

Get trading signals on your phone automatically!

## 🚀 Setup Steps

### 1️⃣ Create Telegram Bot (2 minutes)

Open Telegram app:

1. Search for **@BotFather**
2. Send: `/newbot`
3. Name: `My Signals Bot` (or anything you like)
4. Username: `my_signals_bot` (must end with 'bot')
5. **Copy the token** (looks like `123456:ABC-DEF...`)

### 2️⃣ Get Your Chat ID (1 minute)

1. Search for **@userinfobot**
2. Start chat - it will show your **Chat ID** (like `123456789`)

### 3️⃣ Configure Script (1 minute)

```bash
# Set your credentials (add to ~/.zshrc or ~/.bashrc)
export TELEGRAM_BOT_TOKEN="paste_your_bot_token_here"
export TELEGRAM_CHAT_ID="paste_your_chat_id_here"
export GITHUB_REPO="your-username/daily_market_automation"

# Reload shell
source ~/.zshrc
```

### 4️⃣ Install Dependencies

```bash
pip install requests  # If not already installed
```

### 5️⃣ Test It!

```bash
cd /path/to/daily_market_automation
python scripts/send_telegram_signals.py
```

**Check your Telegram** - you should see a message with trading signals! 🎉

---

## 🤖 Automate It (Optional)

### Option A: GitHub Actions (Recommended)

Add to `.github/workflows/daily-charts.yml` after line 62:

```yaml
      - name: Send Telegram notification
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
1. Go to repo **Settings → Secrets → Actions**
2. Add `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID`

Now you'll get signals automatically after each GitHub Actions run! ✅

### Option B: Cron (Mac/Linux)

```bash
crontab -e

# Add this line (sends at 6 PM daily, Mon-Fri)
0 18 * * 1-5 cd /path/to/daily_market_automation && source .venv/bin/activate && python scripts/send_telegram_signals.py
```

---

## 📋 Usage Examples

```bash
# Send all signals
python scripts/send_telegram_signals.py

# Only high-confidence signals (score >= 5)
python scripts/send_telegram_signals.py --min-score 5

# Specific repo
python scripts/send_telegram_signals.py --repo username/repo
```

---

## 📱 What You'll Receive

```
📊 Trading Signals Report
🕐 Generated: 2025-11-10 05:30 PM

📈 Summary:
• Symbols Analyzed: 4
• Confirmed Breakouts: 2
  🟢 BUY: 1
  🔴 SELL: 1

🎯 Actionable Signals:

🟢 BUY: AAPL
💵 Price: $225.50
⭐ Score: 6/6
📊 Volume: 1.45x avg
🎯 Type: RESISTANCE_BREAK_CONFIRMED
```

---

## 🎯 Pro Tips

**Send to Group:**
- Create Telegram group
- Add bot as member
- Get group ID (use @userinfobot in group)
- Set `TELEGRAM_CHAT_ID` to group ID

**Send to Channel:**
- Create channel
- Add bot as admin
- Use channel username: `@your_channel`

**Multiple Alerts:**
- Run script multiple times with different filters
- Create different bots for different strategies

---

## 🛠️ Troubleshooting

**Bot not sending?**
- Make sure you started chat with bot (send `/start`)
- Verify token and chat ID are correct
- Check environment variables: `echo $TELEGRAM_BOT_TOKEN`

**No signals?**
- Check repo name is correct
- Verify signals exist: https://raw.githubusercontent.com/USER/REPO/main/data/trading_signals.json

---

**Full docs:** `docs/telegram-setup.md`

**Need help?** Open an issue! 🚀
