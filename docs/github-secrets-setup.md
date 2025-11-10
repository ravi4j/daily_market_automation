# Setting Up GitHub Secrets for Telegram Automation

This guide shows you how to securely configure GitHub Actions to send Telegram notifications automatically.

## 🔐 Why GitHub Secrets?

GitHub Secrets are **encrypted environment variables** that:
- ✅ Are stored securely by GitHub (encrypted at rest)
- ✅ Never appear in logs or workflow outputs
- ✅ Can't be accessed by forked repos
- ✅ Are perfect for API tokens and credentials

---

## 🚀 Setup Steps (5 Minutes)

### Step 1: Create Your Telegram Bot

If you haven't already:

1. Open Telegram → Search **@BotFather**
2. Send: `/newbot`
3. Follow prompts → **Copy your bot token**
   - Format: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`

### Step 2: Get Your Chat ID

1. Search **@userinfobot** on Telegram
2. Start chat → **Copy your Chat ID**
   - Format: `123456789`

### Step 3: Add Secrets to GitHub

#### Visual Steps:

1. **Go to your GitHub repository**
   - Navigate to: `https://github.com/YOUR_USERNAME/daily_market_automation`

2. **Click on Settings** (top menu)

3. **Click on "Secrets and variables"** (left sidebar)

4. **Click on "Actions"**

5. **Click "New repository secret"** button

6. **Add First Secret: TELEGRAM_BOT_TOKEN**
   - Name: `TELEGRAM_BOT_TOKEN`
   - Value: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz` (your actual token)
   - Click "Add secret"

7. **Add Second Secret: TELEGRAM_CHAT_ID**
   - Click "New repository secret" again
   - Name: `TELEGRAM_CHAT_ID`
   - Value: `123456789` (your actual chat ID)
   - Click "Add secret"

#### Command Line (Alternative):

If you have GitHub CLI installed:

```bash
# Set secrets via gh CLI
gh secret set TELEGRAM_BOT_TOKEN
# Paste your token when prompted

gh secret set TELEGRAM_CHAT_ID
# Paste your chat ID when prompted
```

---

## ✅ Verify Setup

After adding secrets, you should see:

```
Repository secrets:
- TELEGRAM_BOT_TOKEN
- TELEGRAM_CHAT_ID
```

**Note:** You can't view the values after adding them (security feature).

---

## 🤖 How GitHub Actions Uses These Secrets

In your workflow file (`.github/workflows/daily-charts.yml`):

```yaml
- name: Send Telegram notification
  env:
    TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
    TELEGRAM_CHAT_ID: ${{ secrets.TELEGRAM_CHAT_ID }}
    GITHUB_REPO: ${{ github.repository }}
  run: |
    python scripts/send_telegram_signals.py
```

**What happens:**
1. GitHub Actions reads encrypted secrets
2. Injects them as environment variables (only during workflow run)
3. Your script reads them via `os.getenv('TELEGRAM_BOT_TOKEN')`
4. Secrets are never logged or visible in outputs
5. After workflow completes, they're destroyed

---

## 🔄 Complete Automation Flow

Once secrets are configured, here's what happens automatically:

```
Every Weekday @ 5:30 PM CT:
├─ 1️⃣ daily-fetch.yml runs
│   └─ Fetches latest market data
│   └─ Commits CSVs to repo
│
└─ 2️⃣ daily-charts.yml triggers (after fetch succeeds)
    ├─ Generates breakout charts
    ├─ Exports trading signals (JSON/CSV)
    ├─ Commits charts & signals to repo
    └─ 📱 Sends Telegram notification ← NEW!
        └─ Uses GitHub Secrets (secure)
        └─ Sends formatted message to YOUR phone
        └─ Includes all confirmed breakouts
```

---

## 📱 What You'll Receive

After each successful workflow run:

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
📈 Trend: UPTREND
🎯 Type: RESISTANCE_BREAK_CONFIRMED
📉 Support: $210.25
📈 Resistance: $225.00

[... more signals ...]
```

---

## 🧪 Test Your Setup

### Option 1: Manual Trigger (Recommended)

1. Go to **Actions** tab on GitHub
2. Click **"Generate Daily Charts"** workflow
3. Click **"Run workflow"** dropdown
4. Click **"Run workflow"** button
5. Wait ~2 minutes
6. **Check your Telegram!** 📱

### Option 2: View Workflow Logs

After a run completes:

1. Go to **Actions** tab
2. Click on the latest workflow run
3. Click on **"generate-charts"** job
4. Expand **"Send Telegram notification"** step
5. You should see: `✅ Telegram notification sent!`

---

## 🔒 Security Features

### What's Protected:

✅ **Bot Token** - Encrypted by GitHub, never visible
✅ **Chat ID** - Encrypted by GitHub, never visible
✅ **Logs** - Secrets are masked (show as `***`)
✅ **Forked Repos** - Can't access your secrets
✅ **Pull Requests** - From forks can't access secrets

### Example Log Output:

```
📤 Sending signals to Telegram...
Using bot token: ***  ← Automatically masked!
Sending to chat: ***  ← Automatically masked!
✅ Signals sent successfully!
```

---

## 🛠️ Troubleshooting

### Secrets Not Working?

**Check 1: Secrets are correctly named**
```
✅ TELEGRAM_BOT_TOKEN (correct)
❌ TELEGRAM_TOKEN (wrong name)
❌ telegram_bot_token (wrong case - must be uppercase)
```

**Check 2: No extra spaces**
```
✅ 123456:ABC-DEF (correct)
❌ 123456:ABC-DEF  (trailing space)
❌  123456:ABC-DEF (leading space)
```

**Check 3: Workflow syntax**
```yaml
# ✅ Correct
${{ secrets.TELEGRAM_BOT_TOKEN }}

# ❌ Wrong
${{ secrets.telegram_bot_token }}  # Case sensitive!
${ secrets.TELEGRAM_BOT_TOKEN }    # Wrong syntax
```

### Workflow Runs but No Telegram Message?

1. **Check workflow logs:**
   - Look for "Send Telegram notification" step
   - Check for error messages

2. **Verify bot setup:**
   - Did you start a chat with your bot? (send `/start`)
   - Is the bot token still valid? (check @BotFather)
   - Is the chat ID correct?

3. **Test locally first:**
   ```bash
   export TELEGRAM_BOT_TOKEN="your_token"
   export TELEGRAM_CHAT_ID="your_id"
   python scripts/send_telegram_signals.py
   ```

### Still Not Working?

**Debug mode:** Add this to workflow to see more details:

```yaml
- name: Debug Telegram setup
  run: |
    echo "Checking secrets..."
    if [ -z "${{ secrets.TELEGRAM_BOT_TOKEN }}" ]; then
      echo "❌ TELEGRAM_BOT_TOKEN not set"
    else
      echo "✅ TELEGRAM_BOT_TOKEN is set"
    fi
    if [ -z "${{ secrets.TELEGRAM_CHAT_ID }}" ]; then
      echo "❌ TELEGRAM_CHAT_ID not set"
    else
      echo "✅ TELEGRAM_CHAT_ID is set"
    fi
```

---

## 🎯 Optional: Multiple Notification Targets

### Send to Multiple Chats:

Add more secrets:
```
TELEGRAM_CHAT_ID_1  (your personal chat)
TELEGRAM_CHAT_ID_2  (your trading group)
TELEGRAM_CHAT_ID_3  (your partner's chat)
```

Update workflow:
```yaml
- name: Send to multiple Telegrams
  run: |
    python scripts/send_telegram_signals.py --chat ${{ secrets.TELEGRAM_CHAT_ID_1 }}
    python scripts/send_telegram_signals.py --chat ${{ secrets.TELEGRAM_CHAT_ID_2 }}
    python scripts/send_telegram_signals.py --chat ${{ secrets.TELEGRAM_CHAT_ID_3 }}
```

### Send to Telegram Channel:

1. Create a channel
2. Add your bot as admin
3. Use channel username as chat ID: `@your_channel`
4. Add as secret: `TELEGRAM_CHANNEL_ID`

---

## 📚 Additional Resources

- [GitHub Encrypted Secrets Docs](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [BotFather Guide](https://core.telegram.org/bots#6-botfather)

---

## ✅ Quick Reference

| Secret Name | Example Value | How to Get |
|-------------|---------------|------------|
| `TELEGRAM_BOT_TOKEN` | `123456:ABC-DEF...` | @BotFather → `/newbot` |
| `TELEGRAM_CHAT_ID` | `123456789` | @userinfobot → Start chat |

**Location:** GitHub Repo → Settings → Secrets and variables → Actions

---

**Need help?** Open an issue with:
- Workflow logs (with secrets masked)
- Steps you've tried
- Error messages

🚀 **Happy Automating!**
