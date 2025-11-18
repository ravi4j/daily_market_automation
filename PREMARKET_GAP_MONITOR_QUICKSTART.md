# 🌅 Pre-Market Gap Monitor - Quick Start Guide

Get morning alerts for:
- 🛡️ **Gap RISKS** on your positions (protection)
- 🎯 **Gap OPPORTUNITIES** to buy (new trades)

---

## 🎯 What Is This?

The Pre-Market Gap Monitor is a **DUAL-PURPOSE** system that:

### 🛡️ **PROTECTS Your Positions:**
- 📉 **Gap Downs** - Price opening lower (potential stop loss triggers)
- 📈 **Gap Ups** - Price opening higher (profit-taking opportunities)
- ⚠️ **Risk Levels** - How close you are to your stop loss

### 🎯 **FINDS New Opportunities:**
- 📉 **Gap Down Buys** - Oversold stocks ready to bounce (70% gap fill rate)
- 📈 **Gap Up Buys** - Breakout stocks with momentum (80% continuation rate)
- 🔢 **Opportunity Scoring** - 0-100 score for each opportunity
- 💰 **Trade Setups** - Entry/Stop/Target for each

### 📊 **Market Context:**
- S&P 500, Nasdaq, Dow futures sentiment
- VIX volatility index

**Runs 3 times each morning:**
- 🌅 **7:00 AM ET** - Early warning (2.5 hours before open)
- 🕗 **8:00 AM ET** - Mid-check (1.5 hours before open)
- 🕘 **9:00 AM ET** - Final warning (30 min before open)

---

## ⚡ Quick Setup (5 Minutes)

### Step 1: Add Your Positions

Edit `config/premarket_config.yaml` and add your active trades:

```yaml
positions:
  AAPL:
    shares: 10
    avg_entry: 230.00
    stop_loss: 225.00
    target1: 240.00
    target2: 250.00
    notes: "Swing trade from Nov 18"
  
  MSFT:
    shares: 5
    avg_entry: 420.00
    stop_loss: 410.00
    target1: 440.00
```

**⚠️ IMPORTANT**: 
- Update this file **every time** you enter or exit a trade
- Remove positions when you close them
- Accurate data = better alerts!

**✨ NEW: Enable Gap Opportunities**

To also scan for NEW buying opportunities (recommended!), add to your config:

```yaml
# Gap Opportunity Scanner (NEW!)
opportunity_scanner:
  enabled: true              # Turn on opportunity detection
  min_gap_pct: 2.0          # Minimum 2% gap to consider
  max_opportunities: 5      # Show top 5 opportunities
  min_score: 50             # Only show score >= 50
  symbols_to_scan: []       # Empty = scan S&P 500
  
telegram:
  include_opportunities: true   # Show in alerts
```

**How it works:**
- Scans S&P 500 stocks for gaps >= 2%
- Finds **Gap Downs** (oversold, ready to bounce)
- Finds **Gap Ups** (breakouts with momentum)
- Scores each 0-100 based on fundamentals
- Shows top 5 with trade setups (entry/stop/target)

**Result:** Your alert will have 2 sections:
1. 📈 YOUR POSITIONS (protection)
2. 🟢 GAP OPPORTUNITIES (new trades)

---

### Step 2: Test It Locally

```bash
# macOS/Linux
python scripts/send_premarket_alerts.py

# Windows
python scripts\send_premarket_alerts.py
```

**Expected Output:**
```
============================================================================
PRE-MARKET GAP MONITOR
============================================================================

📋 Loading configuration...
📊 Monitoring 2 position(s): AAPL, MSFT

🔍 Checking pre-market prices...
   Fetching AAPL...
   ✅ AAPL: +0.45% - LOW
   Fetching MSFT...
   ✅ MSFT: -0.32% - LOW

📊 Checking market futures...
   Fetching S&P 500...
   ✅ S&P 500: +0.25%
   ...

🔍 Scanning for gap opportunities...
   Loaded 503 symbols from S&P 500 list
   Found: NVDA gap +5.15%
   Found: AAPL gap -4.35%
   ✅ Found 2 gap opportunities!

📱 Sending to Telegram...
✅ Alert sent successfully!
```

---

### Step 3: Set Up Automation

Choose your platform:

#### 🍎 macOS/Linux (Cron)

```bash
# Edit crontab
crontab -e

# Add these lines (adjust PROJECT path):
PROJECT=/path/to/daily_market_automation

# Pre-market alerts (7 AM, 8 AM, 9 AM ET)
0 12 * * 1-5 cd $PROJECT && venv/bin/python scripts/send_premarket_alerts.py >> logs/premarket.log 2>&1
0 13 * * 1-5 cd $PROJECT && venv/bin/python scripts/send_premarket_alerts.py >> logs/premarket.log 2>&1
0 14 * * 1-5 cd $PROJECT && venv/bin/python scripts/send_premarket_alerts.py >> logs/premarket.log 2>&1
```

**Note**: Times are in UTC. Adjust for your timezone:
- EST (winter): 7 AM = 12 PM UTC
- EDT (summer): 7 AM = 11 AM UTC

#### 🪟 Windows (Task Scheduler)

```powershell
# Run setup script (auto-creates all tasks)
.\scripts\setup_scheduled_tasks.ps1

# Or create manually:
# Open Task Scheduler → Create Basic Task
# Name: "Pre-Market Alert 7 AM"
# Trigger: Daily at 7:00 AM, Mon-Fri
# Action: scripts\run_premarket_workflow.bat
```

#### ☁️ GitHub Actions (Cloud)

Already set up! Just push your `premarket_config.yaml`:

```bash
git add config/premarket_config.yaml
git commit -m "Update positions for pre-market monitoring"
git push
```

Workflow runs automatically at 7, 8, 9 AM ET every weekday.

---

## 📱 Sample Telegram Alert

```
🌅 PRE-MARKET ALERT
07:00 AM ET

📊 MARKET FUTURES
🟢 S&P 500: +0.35%
🟢 Nasdaq: +0.52%
🟢 Dow Jones: +0.28%

🟢 BULLISH (+0.38%)
Market likely opens green
━━━━━━━━━━━━━━━━━━━━

🌡️ VIX: 14.2 (NORMAL)
Normal market conditions
━━━━━━━━━━━━━━━━━━━━

📈 YOUR POSITIONS

✅ AAPL
🟢 Pre-Market: $231.05 (+0.46%)
Previous Close: $230.00
Your Entry: $230.00
Your Stop: $225.00

Distance: 2.68% from stop

💡 Small gap up. Hold and let it run. Monitor for continuation.
━━━━━━━━━━━━━━━━━━━━

⚠️ MSFT
🔴 Pre-Market: $411.50 (-2.02%)
Previous Close: $420.00
Your Entry: $420.00
Your Stop: $410.00

Distance: 0.37% from stop

💡 VERY CLOSE TO STOP! Be at your computer at 9:25 AM. Prepare to sell at market open.
━━━━━━━━━━━━━━━━━━━━

⚠️ ACTION REQUIRED
• Be at computer/phone at 9:25 AM ET
• Prepare to exit positions if needed
• Market opens in 150 minutes
```

---

## 🎯 Understanding Gap Types

### Common Gap (< 2%)
- **What**: Small overnight move
- **Usually**: Fills during the day
- **Action**: Monitor normally

### Breakaway Gap (> 5%)
- **What**: Major news-driven move
- **Usually**: Doesn't fill (continues trend)
- **Action**: Take immediate action (exit or take profit)

### Gap Up vs Gap Down

#### Gap Up 📈
- **Good for**: Long positions
- **Action**: Consider taking partial profits
- **Risk**: Might reverse (gap fill)

#### Gap Down 📉
- **Bad for**: Long positions
- **Action**: Prepare to exit if near stop
- **Risk**: Could continue lower

---

## 🚨 Risk Levels Explained

### CRITICAL 🚨
- **Position is below your stop loss**
- **Action**: Exit immediately at market open
- **Why**: Your stop should have triggered

### HIGH ⚠️
- **Position within 1% of stop loss**
- **Action**: Be ready to exit at 9:30 AM
- **Why**: One more dip triggers your stop

### MEDIUM 🟡
- **Significant gap (2-5%) but not near stop**
- **Action**: Monitor closely
- **Why**: Volatility is elevated

### LOW ✅
- **Small gap (< 1%) or far from stop**
- **Action**: Normal monitoring
- **Why**: No immediate concern

---

## 🛠️ Configuration Options

Edit `config/premarket_config.yaml`:

```yaml
# Alert thresholds
alerts:
  gap_threshold: 0.5          # Alert if gap > 0.5%
  stop_proximity_threshold: 1.0  # Alert if within 1% of stop
  critical_gap_threshold: 2.0    # Critical if gap > 2%

# Include/exclude features
telegram:
  include_market_sentiment: true   # Show S&P 500, Nasdaq, Dow
  include_vix: true                # Show volatility index
  include_sector_data: false       # Show sector rotation (advanced)
  include_recommendations: true    # Show action suggestions

# Alert filtering
telegram:
  alert_levels: ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']
  # Remove 'LOW' to only get important alerts
```

---

## 📊 Extended Hours Trading (Advanced)

### What Are Extended Hours?

- **Pre-Market**: 4:00 AM - 9:30 AM ET
- **Regular**: 9:30 AM - 4:00 PM ET
- **After-Hours**: 4:00 PM - 8:00 PM ET

### Can I Trade Pre-Market?

**Depends on your broker:**
- ✅ Interactive Brokers: Yes (4 AM - 8 PM)
- ✅ TD Ameritrade: Yes (7 AM - 8 PM)
- ✅ Fidelity: Yes (7 AM - 8 PM)
- ✅ Charles Schwab: Yes (7 AM - 8 PM)
- ⚠️ Robinhood: Limited (9 AM - 9:30 AM only)

### Should I Exit in Pre-Market?

**Pros:**
- ✅ Avoid bigger loss if gap continues
- ✅ Get out before everyone else
- ✅ Beat the crowd at 9:30 AM

**Cons:**
- ❌ Lower liquidity (wider spreads)
- ❌ Worse fill price
- ❌ Might reverse at open (gap fill)

**My Recommendation:**
- **If gap is CRITICAL (below stop)**: Exit in pre-market
- **If gap is HIGH (near stop)**: Wait until 9:30 AM open (more liquidity)
- **If gap is MEDIUM/LOW**: Let your regular stop work

---

## 🔧 Troubleshooting

### Not Getting Alerts?

**Check:**
```bash
# 1. Are positions configured?
grep "^  [A-Z]" config/premarket_config.yaml

# 2. Is send_alerts enabled?
grep "send_alerts: true" config/premarket_config.yaml

# 3. Are env vars set?
echo $TELEGRAM_BOT_TOKEN
echo $TELEGRAM_CHAT_ID

# 4. Test manually
python scripts/send_premarket_alerts.py
```

### Alerts for Old Positions?

**Update your config:**
```yaml
# Remove or comment out closed positions
positions:
  # ETN:  # <-- Add # to comment out
  #   shares: 20
  #   ...
  
  AAPL:  # Keep active positions
    shares: 10
    ...
```

### Wrong Gap Data?

**Possible causes:**
- Market hasn't opened yet (data not available)
- Symbol is wrong (check ticker)
- Stock doesn't trade pre-market (illiquid)
- Yahoo Finance API issue (try again)

---

## 💡 Pro Tips

### 1. Morning Routine

```yaml
6:45 AM: Wake up, check phone 📱
7:00 AM: Get first alert (early warning)
7:05 AM: Review positions, plan action
8:00 AM: Get second alert (confirmation)
9:00 AM: Get final alert (last warning)
9:25 AM: Be at computer if action needed
9:30 AM: Market opens - execute plan!
```

### 2. Keep Config Updated

```bash
# After EVERY trade
vim config/premarket_config.yaml  # Add new position
git add config/premarket_config.yaml
git commit -m "Add TSLA position for gap monitoring"
git push  # If using GitHub Actions
```

### 3. Use Paper Trading First

Add your **paper trading positions** to learn:
- How gaps work
- What alerts look like
- When to take action
- Build confidence!

### 4. Set Phone Alerts

Make Telegram notifications louder:
- iPhone: Settings → Notifications → Telegram → Sounds (Loud)
- Android: Long-press notification → Importance → Urgent

### 5. Weekend Preparation

Sunday night:
```bash
# Review your positions
cat config/premarket_config.yaml

# Update any changes
vim config/premarket_config.yaml

# Test the system
python scripts/send_premarket_alerts.py
```

---

## 📚 Related Guides

- [Trading Stop Loss Guide](docs/STOP_LOSS_GUIDE.md) - Understanding stops
- [Gap Trading Strategies](docs/GAP_TRADING_GUIDE.md) - How to trade gaps
- [Risk Management](docs/RISK_MANAGEMENT.md) - Position sizing
- [News Scanner Guide](NEWS_SCANNER_GUIDE.md) - Finding opportunities

---

## 🆘 Common Questions

**Q: Do I need to be awake at 7 AM?**
A: No! Alerts are sent to Telegram. Check when you wake up. Most important is the 9 AM alert (30 min before open).

**Q: What if I miss the alerts?**
A: Your regular stop loss still protects you! Pre-market alerts are *extra* protection for early warning.

**Q: Can I disable certain alerts?**
A: Yes! Edit `config/premarket_config.yaml`:
```yaml
telegram:
  alert_levels: ['CRITICAL', 'HIGH']  # Only urgent alerts
```

**Q: Does this work for day trading?**
A: Not ideal. This is for **swing traders** holding overnight. Day traders close positions before 4 PM (no overnight risk).

**Q: What about crypto/forex?**
A: No. This is for US stocks only (9:30 AM - 4 PM ET market hours). Crypto trades 24/7 (no gaps).

---

## ✅ Success Story

**Your ETN Trade Example:**

```
Day 1 (Nov 17):
• Bought ETN at $341.49
• Set stop at $340.00
• Went to bed ✅

Day 2 (Nov 18) Morning:
• 7:00 AM Alert: "ETN pre-market $340.33, NEAR STOP!"
• You: "Oh no! Let me watch this..."
• 9:30 AM: Opens at $340.33
• Stop triggers at $340.00
• Loss: Only -$29.70 (-0.3%) ✅

WITHOUT Pre-Market Alert:
• You wake up at 10 AM
• ETN already at $335 (kept falling)
• Stop triggered at $340
• But you didn't know until later
• Same result, but more stress!

WITH Pre-Market Alert:
• You knew at 7 AM what was coming
• You were prepared mentally
• You could have exited pre-market at $340.50 (saved $10!)
• Less stress, more control ✅
```

**Lesson**: Pre-market alerts don't prevent losses, but they give you **control** and **peace of mind**!

---

## 🚀 Next Steps

1. **Add your positions** to `config/premarket_config.yaml`
2. **Test locally**: `python scripts/send_premarket_alerts.py`
3. **Set up automation** (cron / Task Scheduler / GitHub Actions)
4. **Receive morning alerts** at 7, 8, 9 AM ET
5. **Trade with confidence** knowing you're protected!

---

**Questions? Issues? Improvements?**

Open an issue on GitHub or check the main [README.md](README.md) for more help!

**Happy Trading! May your gaps be small and your profits be large!** 🎯📈

