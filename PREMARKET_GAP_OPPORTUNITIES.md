# 🌅 Pre-Market Gap Monitor - NOW WITH OPPORTUNITY DETECTION! 🎯

## 🚀 **DUAL FUNCTIONALITY - Complete Morning Trading System**

Your Pre-Market Gap Monitor now does **BOTH**:

### 1. 🛡️ **PROTECT** Your Existing Positions
- Monitor YOUR positions for gap risk
- Alert if price gaps near your stop loss
- Risk assessment (CRITICAL/HIGH/MEDIUM/LOW)
- Actionable recommendations

### 2. 🎯 **FIND** New Buy Opportunities  
- Scan S&P 500 for gap opportunities
- Identify oversold gap downs (buy the dip)
- Detect breakout gap ups (momentum plays)
- Score opportunities (0-100)
- Complete trade setups (entry/stop/target)

---

## 📱 **Sample Combined Alert**

```
🌅 PRE-MARKET ALERT
07:00 AM ET

📊 MARKET FUTURES
🔴 S&P 500: -0.85%
🔴 Nasdaq: -1.12%
🔴 Market likely opens red
━━━━━━━━━━━━━━━━━━━━

📈 YOUR POSITIONS

⚠️ ETN
🔴 Pre-Market: $340.33 (-0.71%)
Previous Close: $342.76
Your Entry: $341.49
Your Stop: $340.00
Distance: 0.10% from stop

💡 VERY CLOSE TO STOP! Be ready to exit at open.
━━━━━━━━━━━━━━━━━━━━

🟢 GAP OPPORTUNITIES
New buying opportunities detected

📉 1. AAPL ⭐⭐⭐
Gap Down (Oversold)
Gap: -4.35% ($230.00 → $220.00)
Score: 85/100

Trade Setup:
• Entry: $220.00
• Stop: $215.00
• Target: $230.00 (gap fill)
• Risk/Reward: 1:2.0

Why:
• Ideal gap down (4.4%)
• Strong profit margins
• Reasonable valuation
━━━━━━━━━━━━━━━━━━━━

📈 2. NVDA ⭐⭐⭐
Gap Up (Breakout)
Gap: +5.15% ($485.00 → $510.00)
Score: 88/100

Trade Setup:
• Entry: $510.00
• Stop: $495.00 (below gap)
• Target: $550.00
• Risk/Reward: 1:2.7

Why:
• Strong gap up (5.2%)
• Strong revenue growth
• Strong volume conviction
━━━━━━━━━━━━━━━━━━━━

⚠️ ACTION REQUIRED
• Be at computer at 9:25 AM
• Consider exiting ETN
• Consider buying AAPL or NVDA
• Market opens in 150 minutes
```

---

## 🎯 **Two Types of Gap Opportunities**

### **Type 1: Gap DOWN (Oversold) 📉**

**When it happens:**
- Stock gaps down 2-10% on temporary bad news
- Fundamentals still strong
- Likely to bounce back (gap fill)

**Example:**
```
AAPL
Previous Close: $230.00
Pre-Market: $220.00 (-4.35%)
Reason: Supply chain concerns (temporary)

✅ BUY at $220
❌ STOP at $215 (-2.3% risk)
🎯 TARGET at $230 (gap fill = +4.5% profit)

Risk/Reward: 1:2 (risk $5 to make $10)
```

**Why it works:**
- Market overreacts to temporary news
- Strong companies bounce back
- Gap fill is common (70% probability)
- Good entry discount

---

### **Type 2: Gap UP (Breakout) 📈**

**When it happens:**
- Stock gaps up 3-8% on earnings/news
- Strong momentum
- Gap doesn't fill (continuation)

**Example:**
```
NVDA
Previous Close: $485.00
Pre-Market: $510.00 (+5.15%)
Reason: Earnings beat + guidance raise

✅ BUY at $510 (or $505 if dips)
❌ STOP at $495 (below gap)
🎯 TARGET at $550 (+8% profit)

Risk/Reward: 1:2.7 (risk $15 to make $40)
```

**Why it works:**
- Breakaway gaps don't fill (80% continue)
- Strong momentum follows earnings
- New higher range established
- Institutional buying

---

## 🔍 **Scoring System (0-100)**

### **What Gets Points:**

**Gap Downs (Oversold):**
- ✅ Ideal gap size 2-4% (+25 pts)
- ✅ Strong profit margins (+15 pts)
- ✅ Reasonable P/E ratio (+15 pts)
- ✅ Revenue growth (+10 pts)
- ✅ Analyst ratings (buy/strong buy) (+15 pts)
- ✅ Well above 52W low (+10 pts)
- ✅ Good pre-market volume (+10 pts)

**Gap Ups (Breakout):**
- ✅ Strong gap 3-5% (+25 pts)
- ✅ Strong fundamentals (+15 pts)
- ✅ Revenue growth (+15 pts)
- ✅ Room to run (below 52W high) (+15 pts)
- ✅ High volume conviction (+15 pts)
- ✅ Analyst support (+15 pts)

### **Score Interpretation:**

| Score | Confidence | Action |
|-------|------------|--------|
| 80-100 | ⭐⭐⭐ HIGH | Strong buy |
| 60-79 | ⭐⭐ MEDIUM | Consider buying |
| 40-59 | ⭐ LOW | Watch only |
| < 40 | - | Skip |

---

## ⚙️ **Configuration**

Edit `config/premarket_config.yaml`:

```yaml
# Your positions (protection)
positions:
  ETN:
    shares: 20
    avg_entry: 341.49
    stop_loss: 340.00

# Gap Opportunity Scanner (NEW!)
opportunity_scanner:
  enabled: true              # Turn on/off
  min_gap_pct: 2.0          # Minimum 2% gap
  max_opportunities: 5      # Show top 5
  min_score: 50             # Only show score >= 50
  
  # Scan S&P 500 or custom list
  symbols_to_scan: []       # Empty = use S&P 500
  
  # Or specify your own:
  # symbols_to_scan: ['AAPL', 'MSFT', 'NVDA', 'GOOGL']
  
  scan_gap_downs: true      # Find oversold
  scan_gap_ups: true        # Find breakouts

# Telegram settings
telegram:
  include_opportunities: true   # Show opportunities
  include_market_sentiment: true
  include_vix: true
```

---

## 🎓 **How to Use This System**

### **Morning Routine (7:00 AM Alert)**

```yaml
STEP 1: Check Your Positions
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Look at "YOUR POSITIONS" section:
• Any CRITICAL/HIGH alerts? → Plan to exit at open
• Any LOW alerts? → Monitor normally

STEP 2: Check Market Sentiment
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Look at "MARKET FUTURES":
• Green (bullish)? → Good for buying opportunities
• Red (bearish)? → Be cautious, but dips = opportunities

STEP 3: Review Gap Opportunities
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Look at "GAP OPPORTUNITIES":
• Score 80+? → Strong candidate
• Score 60-79? → Consider if fits your strategy
• Score < 60? → Skip

STEP 4: Make Your Plan
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Write down:
• Exit: Which positions to sell?
• Enter: Which opportunities to buy?
• Stop losses: Where for each?

STEP 5: Execute at 9:30 AM
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
At market open:
• Exit positions near stops
• Buy opportunities with limit orders
• Set stop losses immediately
```

---

## 💡 **Pro Tips**

### **1. Don't Chase Everything**

```
❌ BAD: Buy every gap opportunity
✅ GOOD: Pick 1-2 best opportunities per day
   
Focus on:
• Highest scores (80+)
• HIGH confidence (⭐⭐⭐)
• Good risk/reward (1:2+)
• Fits your trading style
```

### **2. Use Position Sizing**

```
Total Capital: $10,000
Max Risk Per Trade: 2% = $200

Example:
Entry: $220
Stop: $215
Risk per share: $5

Position size: $200 / $5 = 40 shares
Total cost: $220 × 40 = $8,800

If stopped: Lose $200 (2%)
If target hit: Make $400+ (4%+)
```

### **3. Combine with Your Analysis**

```
System says: AAPL gap down -4%, score 85
↓
You check:
✅ Your technical analysis agrees?
✅ Fits your trading plan?
✅ Have capital available?
✅ Can monitor the position?
↓
If YES to all → EXECUTE
If NO to any → SKIP
```

### **4. Paper Trade First!**

```
Week 1-2: Paper trade ALL opportunities
• Add them to TradingView paper account
• Track results in spreadsheet
• Learn what works for YOU

After 10+ paper trades:
• Calculate win rate
• Verify profitable
• Then use real money (small size)
```

---

## 🎯 **Real-World Example**

**Your Morning on Nov 18, 2025:**

```
7:00 AM Alert Arrives:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📈 YOUR POSITIONS:
⚠️ ETN: Pre-market $340.33 (near stop $340)
→ Decision: Exit at open to protect capital

🟢 GAP OPPORTUNITIES:
1. AAPL: Gap down -4.3% to $220, Score 85
   Entry $220, Stop $215, Target $230
   → Decision: BUY 40 shares at open

2. NVDA: Gap up +5.2% to $510, Score 88
   Entry $510, Stop $495, Target $550
   → Decision: BUY 5 shares at open

9:30 AM Execution:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Sell 20 ETN @ $340.50 (stop triggered)
  Loss: -$20 (-0.2%)

• Buy 40 AAPL @ $220.50
  Stop set @ $215

• Buy 5 NVDA @ $511.00
  Stop set @ $495

Two Weeks Later:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• AAPL @ $232 (gap filled!)
  Profit: +$11.50 × 40 = +$460 (+5.2%)

• NVDA @ $545 (continued up)
  Profit: +$34 × 5 = +$170 (+6.7%)

Total:
  ETN loss: -$20
  AAPL profit: +$460
  NVDA profit: +$170
  Net: +$610 (+6.1% on capital)

System worked! ✅
```

---

## 🚀 **Getting Started**

### **1. Enable Feature**

```bash
# Edit config
vim config/premarket_config.yaml

# Set these:
opportunity_scanner:
  enabled: true
  min_gap_pct: 2.0
  max_opportunities: 5

telegram:
  include_opportunities: true
```

### **2. Test It**

```bash
# Run manually
python scripts/send_premarket_alerts.py

# Should see:
# "🔍 Scanning for gap opportunities..."
# "✅ Found N gap opportunities!"
```

### **3. Set Up Automation**

```bash
# Runs automatically at 7, 8, 9 AM ET
# via GitHub Actions or local cron/Task Scheduler
# (Already configured!)
```

### **4. Start Paper Trading**

```
Day 1: Receive alert with opportunities
Day 1: Paper trade top 2 opportunities
Day 2: Track results
...
Week 2: Review paper trades
Week 3: Start with real money (small size)
```

---

## 📚 **Related Guides**

- [PREMARKET_GAP_MONITOR_QUICKSTART.md](PREMARKET_GAP_MONITOR_QUICKSTART.md) - Basic setup
- [Gap Trading Strategies Guide](docs/GAP_TRADING_STRATEGIES.md) - Advanced techniques
- [Risk Management Guide](docs/RISK_MANAGEMENT.md) - Position sizing

---

## 🎉 **Summary**

**You now have a COMPLETE morning trading system!**

✅ **Protects** existing positions from gaps
✅ **Finds** new opportunities to buy
✅ **Scores** opportunities (0-100)
✅ **Provides** complete trade setups
✅ **Delivers** everything in ONE Telegram alert

**3 alerts per morning:**
- 7:00 AM - Early warning
- 8:00 AM - Mid-check
- 9:00 AM - Final call

**All automatic. All in one place. Ready to trade!** 🚀

---

**Questions? Issues?**

See [README.md](README.md) or open a GitHub issue!

**Happy Trading! Buy the dips, ride the breakouts!** 📈💰

