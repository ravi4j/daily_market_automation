# Complete Automation Flow 🔄

Visual guide showing how everything works together automatically.

---

## 📊 Daily Automation Timeline

```
┌─────────────────────────────────────────────────────────────────────┐
│                    EVERY WEEKDAY (Mon-Fri)                          │
└─────────────────────────────────────────────────────────────────────┘

5:30 PM CT  ─┐
             │
             ▼
     ┌───────────────────┐
     │  WORKFLOW 1:      │
     │  Fetch Prices     │
     │  (daily-fetch.yml)│
     └─────────┬─────────┘
               │
               │ 1. Fetches new market data
               │ 2. Updates CSV files
               │ 3. Commits to repo
               │
               ▼
         [CSV files updated]
               │
               │ Triggers next workflow
               ▼
     ┌───────────────────┐
     │  WORKFLOW 2:      │
     │  Generate Charts  │
     │  & Signals        │
     │  (daily-charts.yml)│
     └─────────┬─────────┘
               │
               ├─► 1. Generate breakout charts (visualize_breakouts.py)
               │
               ├─► 2. Export trading signals (export_signals.py)
               │      ├─ data/trading_signals.json
               │      └─ data/trading_signals.csv
               │
               ├─► 3. Commit charts & signals to repo
               │
               ├─► 4. 📱 Send Telegram notification
               │      └─ Uses GitHub Secrets (secure!)
               │
               └─► 5. Create workflow summary
                      └─ Table with all signals

                              ▼

                     📱 YOUR PHONE!

         ┌─────────────────────────────────┐
         │  Telegram Message                │
         │                                  │
         │  📊 Trading Signals Report       │
         │  🕐 Generated: 5:30 PM          │
         │                                  │
         │  🟢 BUY: AAPL @ $225.50         │
         │  ⭐ Score: 6/6                  │
         │  🔴 SELL: TQQQ @ $110.03        │
         │  ⭐ Score: 5/6                  │
         └─────────────────────────────────┘
```

---

## 🔐 Security Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                     CREDENTIAL FLOW                               │
└──────────────────────────────────────────────────────────────────┘

LOCAL MACHINE:
┌─────────────────────┐
│  ~/.zshrc           │
│                     │
│  export             │
│  TELEGRAM_BOT_TOKEN │  ◄─── Set once, stays on your machine
│  TELEGRAM_CHAT_ID   │
└─────────────────────┘
         │
         │ Used for local testing
         ▼
┌─────────────────────┐
│  send_telegram_     │
│  signals.py         │
│  (reads env vars)   │
└─────────────────────┘


GITHUB ACTIONS:
┌─────────────────────┐
│  GitHub Secrets     │
│  (encrypted)        │
│                     │
│  TELEGRAM_BOT_TOKEN │  ◄─── Set once in repo settings
│  TELEGRAM_CHAT_ID   │       (Settings → Secrets → Actions)
└──────────┬──────────┘
           │
           │ Injected as env vars (secure)
           ▼
┌─────────────────────┐
│  Workflow           │
│  (daily-charts.yml) │
│                     │
│  env:               │
│    TELEGRAM_BOT:    │
│    ${{ secrets }}   │  ◄─── Never visible in logs (masked)
└──────────┬──────────┘
           │
           │ Passed to script
           ▼
┌─────────────────────┐
│  send_telegram_     │
│  signals.py         │
│  (reads env vars)   │
└──────────┬──────────┘
           │
           │ Sends via Telegram API
           ▼
     📱 YOUR PHONE
```

---

## 📂 File Updates Flow

```
┌──────────────────────────────────────────────────────────────────┐
│              WHAT GETS UPDATED AUTOMATICALLY                      │
└──────────────────────────────────────────────────────────────────┘

BEFORE WORKFLOWS:
data/
├── AAPL.csv          (yesterday's data)
├── TQQQ.csv          (yesterday's data)
├── SP500.csv         (yesterday's data)
└── UBER.csv          (yesterday's data)

           ▼ Workflow 1 runs ▼

AFTER FETCH:
data/
├── AAPL.csv          ✅ Updated with today's data
├── TQQQ.csv          ✅ Updated with today's data
├── SP500.csv         ✅ Updated with today's data
└── UBER.csv          ✅ Updated with today's data

           ▼ Workflow 2 runs ▼

AFTER CHARTS & SIGNALS:
data/
├── AAPL.csv
├── TQQQ.csv
├── SP500.csv
├── UBER.csv
├── trading_signals.json  ✅ NEW/Updated with today's signals
└── trading_signals.csv   ✅ NEW/Updated with today's signals

charts/
├── AAPL_breakout.png     ✅ Regenerated
├── TQQQ_breakout.png     ✅ Regenerated
├── SP500_breakout.png    ✅ Regenerated
└── UBER_breakout.png     ✅ Regenerated

           ▼ Committed to GitHub ▼

YOU CAN VIEW:
✅ On GitHub: Browse data/ and charts/ folders
✅ Via Raw URL: https://raw.githubusercontent.com/.../trading_signals.json
✅ In Telegram: Automatic notification sent
✅ In Actions: Workflow summary with table
```

---

## 🎯 Multiple Access Methods

```
┌──────────────────────────────────────────────────────────────────┐
│              HOW TO ACCESS YOUR SIGNALS                           │
└──────────────────────────────────────────────────────────────────┘

DAILY SIGNALS (data/trading_signals.json)
                    │
                    │ Committed to GitHub daily
                    ▼
        ┌───────────────────────┐
        │  GitHub Repository    │
        │  (Public or Private)  │
        └─────────┬─────────────┘
                  │
        ┌─────────┼─────────────────────┐
        │         │                     │
        ▼         ▼                     ▼
   ┌────────┐ ┌─────────┐      ┌──────────────┐
   │ Direct │ │ Telegram│      │ Google Sheets│
   │ GitHub │ │ Bot     │      │ IMPORTDATA() │
   │ Browse │ │ (Push)  │      │ (Pull)       │
   └────────┘ └─────────┘      └──────────────┘
        │         │                     │
        ▼         ▼                     ▼
   View on   Get on phone    Live spreadsheet
   GitHub     instantly       auto-updates


   ┌───────────┐      ┌──────────┐      ┌─────────┐
   │ Python    │      │ curl/wget│      │ Mobile  │
   │ Script    │      │ Command  │      │ Browser │
   │ (Pull)    │      │ (Pull)   │      │ (Pull)  │
   └─────┬─────┘      └────┬─────┘      └────┬────┘
         │                 │                  │
         ▼                 ▼                  ▼
   Automated       Quick CLI check    Bookmark URL
   checking         anytime            on phone


ALL OPTIONS USE THE SAME DATA SOURCE (NO DUPLICATION!)
```

---

## 🔄 Local vs GitHub Actions

```
┌──────────────────────────────────────────────────────────────────┐
│                 TWO WAYS TO RUN                                   │
└──────────────────────────────────────────────────────────────────┘

LOCAL DEVELOPMENT:
┌─────────────────────────────────────┐
│  Your Computer                      │
│                                     │
│  1. source .venv/bin/activate       │
│  2. python src/fetch_daily_prices.py│
│  3. python src/export_signals.py    │
│  4. python scripts/send_telegram_   │
│     signals.py                      │
│                                     │
│  Uses: ~/.zshrc env vars            │
│  When: Manual testing/development   │
└─────────────────────────────────────┘

GITHUB ACTIONS (AUTOMATED):
┌─────────────────────────────────────┐
│  GitHub Servers (Ubuntu)            │
│                                     │
│  1. Runs on schedule (5:30 PM)      │
│  2. fetch_daily_prices.py           │
│  3. export_signals.py               │
│  4. send_telegram_signals.py        │
│                                     │
│  Uses: GitHub Secrets               │
│  When: Automatic daily              │
└─────────────────────────────────────┘

BOTH PRODUCE THE SAME OUTPUT!
```

---

## 📱 Telegram Notification Trigger Points

```
┌──────────────────────────────────────────────────────────────────┐
│           WHEN YOU RECEIVE TELEGRAM MESSAGES                      │
└──────────────────────────────────────────────────────────────────┘

AUTOMATED (GitHub Actions):
┌────────────────────────────┐
│  Every Weekday @ ~5:35 PM  │
│  (After charts workflow)   │
└────────────────────────────┘
           │
           ├─► If signals exist → Sends detailed message
           └─► If no signals → Sends "Hold positions" message


MANUAL TRIGGER:
┌────────────────────────────┐
│  GitHub Actions UI         │
│  "Run workflow" button     │
└────────────────────────────┘
           │
           └─► Runs immediately → Sends Telegram


LOCAL TESTING:
┌────────────────────────────┐
│  python scripts/send_       │
│  telegram_signals.py        │
└────────────────────────────┘
           │
           └─► Runs immediately → Sends Telegram


ALL METHODS SEND TO THE SAME TELEGRAM CHAT!
```

---

## 🎯 Complete Setup Checklist

```
LOCAL SETUP:
☐ Clone repo
☐ Create virtual environment (.venv)
☐ Install dependencies (requirements-base.txt)
☐ Set local env vars (TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)
☐ Test: python scripts/send_telegram_signals.py

GITHUB SETUP:
☐ Create Telegram bot (@BotFather)
☐ Get chat ID (@userinfobot)
☐ Add GitHub Secrets (Settings → Secrets → Actions)
   ☐ TELEGRAM_BOT_TOKEN
   ☐ TELEGRAM_CHAT_ID
☐ Push updated workflows to GitHub
☐ Test: Actions → Run workflow manually
☐ Verify: Check Telegram for message

AUTOMATION ACTIVE:
✅ Daily fetch @ 5:30 PM CT
✅ Charts & signals generated
✅ Telegram notification sent
✅ All files committed to repo
```

---

## 🚀 Quick Links

- **Setup Telegram:** `TELEGRAM_QUICKSTART.md`
- **GitHub Secrets:** `docs/github-secrets-setup.md`
- **Full Telegram Docs:** `docs/telegram-setup.md`
- **Workflow Files:** `.github/workflows/`

---

**Everything runs automatically - you just receive the signals!** 📱
