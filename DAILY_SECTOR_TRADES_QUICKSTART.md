# 🎯 Daily Sector Trades - Quick Start

## ⚡ **5-Minute Setup**

### **Step 1: Ensure Data is Ready**

```bash
# If not already done, fetch metadata and historical data
python scripts/fetch_symbol_metadata.py --sp500
python scripts/fetch_initial_sector_data.py --period 2y
```

### **Step 2: Run the Scanner**

```bash
# After market close (4:30 PM or later)
python scripts/daily_sector_trades.py
```

### **Step 3: Check Telegram**

You'll receive an alert with:
- Top 1-2 trades per sector
- Complete trade setups (Entry/Stop/Target)
- Confidence ratings (⭐⭐⭐ = HIGH)

---

## 📊 **What You Get**

```
🎯 DAILY SECTOR TRADES
November 18, 2024

10 trades across 5 sectors
━━━━━━━━━━━━━━━━━━━━

🏢 Technology

1. NVDA - NVIDIA Corporation ⭐⭐⭐
   Score: 88/100 | STRONG BUY
   Price: $485.00
   
   Trade Setup:
   Entry: $485.00
   Stop: $475.00
   Target: $505.00
   R:R = 1:2.0

[... more sectors ...]
```

---

## 🎓 **Scoring System (Simple)**

**Total Score = 4 Components:**

1. **📰 News (30%)** - Recent price drops, news sentiment
2. **📊 Technical (40%)** - RSI, MACD, Bollinger Bands, Volume
3. **💼 Fundamentals (20%)** - P/E, profit margins, analyst ratings
4. **🏢 Insider (10%)** - Corporate insider buying/selling

**Interpretation:**
- 80-100 = ⭐⭐⭐ **STRONG BUY** (high priority)
- 60-79 = ⭐⭐ **BUY** (good opportunity)
- 40-59 = ⭐ **WATCH** (monitor)
- < 40 = Not shown

---

## 💡 **How to Use**

### **Daily Routine:**

```
4:30 PM - Market closes
5:00 PM - Run scanner
5:01 PM - Check Telegram alert
5:15 PM - Review top trades (focus on ⭐⭐⭐)
5:30 PM - Select 3-5 trades across sectors
Next Day - Execute trades at market open
```

### **Pick Your Trades:**

```
Strategy: Pick 3-5 HIGH confidence trades
Diversification: 1 per sector maximum

Example Picks:
✅ NVDA (Technology) - 88/100
✅ JNJ (Healthcare) - 78/100
✅ JPM (Financial Services) - 80/100

Result: 3 high-quality, diversified trades
```

---

## 🚀 **Common Commands**

```bash
# Standard scan (2 per sector)
python scripts/daily_sector_trades.py

# More selective (1 per sector)
python scripts/daily_sector_trades.py --max-per-sector 1

# High quality only (score >= 70)
python scripts/daily_sector_trades.py --min-score 70

# Specific sectors
python scripts/daily_sector_trades.py --sectors Technology Healthcare
```

---

## 📱 **Complete Daily Workflow**

```bash
# Morning (7, 8, 9 AM) - Pre-market gaps
python scripts/send_premarket_alerts.py

# After close (4:30 PM) - Update data
python src/fetch_daily_prices.py

# Evening (5 PM) - Find tomorrow's trades
python scripts/daily_sector_trades.py

# Review all 3 alerts, pick best trades!
```

---

## 💡 **Pro Tips**

### **Tip 1: Focus on HIGH Confidence**

Only trade ⭐⭐⭐ (score 80+) when starting out.
Win rate is higher, risk is lower.

### **Tip 2: Diversify Across Sectors**

Don't pick 3 trades from Technology.
Pick 1 from Tech, 1 from Healthcare, 1 from Financials.

### **Tip 3: Always Set Stop Losses**

The system provides stop prices.
Set them IMMEDIATELY after entering.

### **Tip 4: Paper Trade First**

Track 2 weeks of picks in TradingView paper account.
Calculate your win rate before using real money.

### **Tip 5: Track by Sector**

Keep notes on which sectors work best for you.
Focus on your winners.

---

## 🎯 **Example Trade**

**Scanner picks: NVDA - 88/100 ⭐⭐⭐**

```
Entry: $485.00
Stop: $475.00 (risk: $10/share = 2.1%)
Target: $505.00 (reward: $20/share = 4.1%)
Risk/Reward: 1:2

Position Size: $1,000 / $485 = 2 shares
Max Loss: $10 × 2 = $20 (2% of $1,000)
Potential Profit: $20 × 2 = $40 (4%)

Action:
- Buy 2 shares at $485
- Set stop at $475
- Set target at $505
- Wait 1-2 weeks
```

---

## ❓ **FAQ**

**Q: When should I run this?**
A: After market close (4:30 PM ET or later)

**Q: How many trades should I pick?**
A: Start with 3-5, focus on HIGH confidence (⭐⭐⭐)

**Q: How long to hold?**
A: Until target hit or stop triggered (usually 1-2 weeks)

**Q: What if I miss a day?**
A: No problem! Run it the next evening. Markets are open Mon-Fri.

**Q: Can I scan just one sector?**
A: Yes! `python scripts/daily_sector_trades.py --sectors Technology`

---

## 📚 **More Information**

- [DAILY_SECTOR_TRADES_GUIDE.md](DAILY_SECTOR_TRADES_GUIDE.md) - Complete guide
- [SECTOR_SCANNING_QUICKSTART.md](SECTOR_SCANNING_QUICKSTART.md) - Setup guide
- [README.md](README.md) - Main documentation

---

## 🎉 **Summary**

✅ Run after market close
✅ Get top 1-2 trades per sector
✅ Focus on HIGH confidence (⭐⭐⭐)
✅ Diversify across sectors
✅ Set stop losses immediately
✅ Paper trade first!

**You're ready! Run it tonight and see your first picks! 🚀**

