# 🤖 Master Scanner Complete Guide

## 🎯 What Is This?

**ONE unified system** that does EVERYTHING automatically:
- Scans entire US market (stocks + ETFs)
- Finds best opportunities using AI + multiple signals
- Checks pre-market gaps
- Runs 5 proven trading strategies
- Monitors your portfolio
- Sends ONE consolidated Telegram alert

**YOU DON'T TELL IT WHAT TO SCAN - IT TELLS YOU WHAT TO BUY!**

---

## ⚡ Quick Start

### Daily Scan (After Market Close)
```bash
# macOS/Linux
./scripts/run_master_scan.sh

# Windows
.\scripts\run_master_scan.bat
```

### Pre-Market Scan (Before Market Open)
```bash
# macOS/Linux
./scripts/run_premarket_scan.sh --mode premarket

# Windows
python scripts\master_daily_scan.py --mode premarket
```

---

## 🧠 How It Works

### Phase 1: Fetch Market Universe
- Connects to Finnhub API
- Fetches ALL US stocks + ETFs (~10,000 symbols)
- Caches for fast access
- Filters by quality (volume, price, exchanges)

### Phase 2: Intelligent Pre-Screening (FAST)
Quickly filters entire market for promising candidates:
- ✅ Price drops 3-10% (opportunity zone)
- ✅ Volume spikes 1.2x-2x (interest)
- ✅ Price > $5 (no penny stocks)
- ✅ Volume > 500K (liquid)
- ✅ Not crashing (< 20% drop)

**Result**: Narrows 10,000 symbols → 50-100 candidates in ~5 minutes

### Phase 3: Deep Multi-Signal Analysis
Analyzes candidates with composite scoring (0-100):

#### 🤖 News Sentiment (30%)
- FinBERT AI analyzes news articles
- Identifies buying opportunities from dips
- Avoids serious issues (bankruptcy, fraud)

#### 📊 Technical Analysis (40%)
- RSI (oversold = opportunity)
- MACD (momentum confirmation)
- Trend analysis (uptrend vs downtrend)
- Volume patterns
- Support/resistance levels

#### 💼 Fundamentals (20%)
- P/E ratio (valuation)
- Profit margins (profitability)
- Revenue growth (momentum)
- Analyst ratings (consensus)
- Market cap (company size)

#### 👔 Insider Activity (10%)
- Tracks insider buying/selling
- Follows "smart money"
- Adjusts score based on sentiment

#### 🎯 Trading Strategies (BONUS +10 points)
**5 Proven Strategies** (all integrated):

1. **ABC Patterns** - Wave-based Fibonacci entries
2. **RSI + MACD** - Oversold + momentum
3. **Momentum Breakout** - Volume + price acceleration
4. **Mean Reversion** - Bollinger Band bounces
5. **Trend Following** - SMA crossovers

**Adds +10 points if strategies confirm the opportunity!**

### Phase 4: Generate Alert
- Ranks all opportunities by composite score
- Selects top 5 with HIGH confidence (70+)
- Formats complete trade setups
- Sends ONE consolidated Telegram message

---

## 📱 What You Get

### Daily Alert (After Market Close)
```
🔍 DAILY MARKET SCAN - 2024-11-20 16:30 ET
════════════════════════════════════════

📊 MARKET STATUS
S&P 500: +0.8% | VIX: 18.5 (Normal) | Risk: MODERATE

🚀 TOP 5 OPPORTUNITIES (from 1,247 symbols scanned)

1. NVDA - STRONG BUY (Score: 89/100)
   Entry: $485 | Target: $525 | Stop: $470 | R/R: 2.7
   🎯 Strategies: ABC Pattern, RSI+MACD
   Why: Strong earnings beat, RSI oversold, insider buying
   📈 Tech: 88 | 📰 News: 92 | 💼 Fund: 85 | 👔 Insider: 90

2. UNH - BUY (Score: 82/100)
   Entry: $512 | Target: $548 | Stop: $498 | R/R: 2.5
   🎯 Strategies: Mean Reversion
   Why: -5% news dip, solid fundamentals
   📈 Tech: 78 | 📰 News: 85 | 💼 Fund: 82 | 👔 Insider: 80

... (3 more)

⚖️ YOUR PORTFOLIO
✅ TQQQ: On target
⚠️ AAPL: 15% overweight - Consider profits

🛡️ RISK ASSESSMENT
Portfolio: 85% (Target: 80%)
Recommendation: Add TLT (bonds) for protection
```

### Pre-Market Alert (Before Market Open)
```
🌅 PRE-MARKET ALERT - 2024-11-21 08:00 ET
════════════════════════════════════════

⚖️ YOUR POSITIONS
🔴 ETN: $340.33 (-3.08%)
   Prev Close: $342.76
   ⚠️ GAP DOWN - Monitor closely

🚀 GAP OPPORTUNITIES (Top 3)

1. TSLA - BUY (Gap: -4.5% | Score: 85/100)
   Entry: $245 | Target: $265 | Stop: $237
   Why: Oversold gap down + solid fundamentals

... (2 more)

⏰ Market opens at 9:30 AM ET
```

---

## 🔧 Configuration

Edit `config/master_config.yaml`:

### Customize Scanning
```yaml
scanning:
  strategy:
    tier: "daily"  # daily, weekly, monthly, full

  intelligent_filters:
    min_price_drop_pct: 3.0      # Look for 3%+ drops
    min_volume_ratio: 1.2         # 20%+ volume spike
    min_price: 5.0                # No penny stocks
```

### Customize Scoring Weights
```yaml
scoring:
  weights:
    news_sentiment: 30   # 30%
    technical: 40        # 40%
    fundamentals: 20     # 20%
    insider_activity: 10 # 10%

  max_opportunities: 5   # Top 5
  min_confidence: 70     # Only HIGH
```

### Enable/Disable Features
```yaml
finbert:
  enabled: true  # AI sentiment

insider:
  enabled: true  # Insider tracking

strategies:
  enabled: true
  active_strategies:
    - abc_patterns
    - rsi_macd
    - momentum_breakout
    - mean_reversion
    - trend_following
```

---

## 🚀 Adding New Strategies (EASY!)

The system is designed to be extensible. Here's how to add a new strategy:

### Step 1: Create Strategy Class
```python
# src/your_new_strategy.py
class YourNewStrategy:
    def generate_signals(self, df):
        # Your strategy logic here
        return signals
```

### Step 2: Initialize in Master Scanner
```python
# scripts/master_daily_scan.py
# In _initialize_components():
self.your_strategy = YourNewStrategy()
```

### Step 3: Add to Strategy Checker
```python
# In _check_strategies():
if self.your_strategy:
    signal = self.your_strategy.generate_signals(df)
    if signal:
        signals.append({
            'strategy': 'Your Strategy',
            'signal': signal.signal,
            'confidence': signal.confidence,
            'trade_setup': {...}
        })
```

### Step 4: Update Config
```yaml
# config/master_config.yaml
strategies:
  active_strategies:
    - abc_patterns
    - rsi_macd
    - your_new_strategy  # Add here
```

That's it! The system will automatically:
- Run your strategy on all candidates
- Integrate signals into composite score
- Show in Telegram alerts
- Include in trade recommendations

---

## 📊 Scan Modes

### 1. Daily Scan (Default)
**When**: After market close (4:30 PM ET)
**What**: Comprehensive analysis of entire market
```bash
./scripts/run_master_scan.sh
```

### 2. Pre-Market Scan
**When**: Before market open (4:00 AM - 9:30 AM ET)
**What**: Gap detection and opportunity analysis
```bash
python scripts/master_daily_scan.py --mode premarket
```

### 3. Intraday Scan (Coming Soon)
**When**: During market hours
**What**: Quick momentum and breakout checks
```bash
python scripts/master_daily_scan.py --mode intraday
```

---

## 🎯 What's Integrated

### ✅ Core Features
- [x] Finnhub API (full market universe)
- [x] FinBERT AI (sentiment analysis)
- [x] Insider tracking (smart money)
- [x] 50+ technical indicators
- [x] Fundamental analysis
- [x] Pre-market gap detection
- [x] Portfolio monitoring
- [x] Telegram alerts

### ✅ Trading Strategies
- [x] ABC Patterns (Fibonacci waves)
- [x] RSI + MACD Confluence
- [x] Momentum Breakout
- [x] Bollinger Band Mean Reversion
- [x] Trend Following
- [ ] Your custom strategies (easily add more!)

### ✅ Intelligent Features
- [x] Auto symbol selection
- [x] Multi-signal composite scoring
- [x] Strategy confirmation boost
- [x] Risk/reward calculation
- [x] Complete trade setups
- [x] Confidence scoring

---

## 🔄 Daily Workflow

### Automated (GitHub Actions)
1. **8:00 AM ET** - Pre-market scan
2. **4:30 PM ET** - Daily scan
3. **6:00 PM Mon** - Weekly comprehensive

### Manual (Local)
```bash
# Morning routine
./scripts/run_premarket_scan.sh

# After market close
./scripts/run_master_scan.sh

# Weekly deep dive
python scripts/master_daily_scan.py --mode daily
```

---

## 💡 Pro Tips

### 1. Start Conservative
- Keep `min_confidence: 70` (HIGH only)
- Review alerts before trading
- Paper trade first

### 2. Customize for Your Style
- Aggressive? Increase technical weight
- Value investor? Increase fundamental weight
- News trader? Increase sentiment weight

### 3. Monitor Multiple Timeframes
- Pre-market: Gaps and opportunities
- Daily: Comprehensive analysis
- Weekly: Big picture trends

### 4. Use Strategy Confirmation
- Multiple strategies = higher confidence
- Single strategy = proceed with caution
- No strategies = rely on fundamentals

### 5. Track Performance
- Results saved to `signals/master_scan_results.json`
- Review what works
- Adjust weights accordingly

---

## 📝 Files Overview

### Core Files
```
scripts/
  ├── master_daily_scan.py      # Main scanner (ALL features)
  ├── run_master_scan.sh         # Daily scan (macOS/Linux)
  ├── run_master_scan.bat        # Daily scan (Windows)
  └── run_premarket_scan.sh      # Pre-market scan

config/
  └── master_config.yaml         # ONE unified config

src/
  ├── finnhub_data.py            # Finnhub API
  ├── finbert_sentiment.py       # AI sentiment
  ├── news_monitor.py            # News analysis
  ├── insider_tracker.py         # Insider tracking
  ├── indicators.py              # Technical indicators
  ├── strategy_runner.py         # Strategy engine
  ├── abc_strategy.py            # ABC patterns
  ├── premarket_monitor.py       # Gap detection
  └── premarket_opportunity_scanner.py
```

### Everything Else is Optional
- `docs/` - Detailed documentation
- `examples/` - Learning examples
- `charts/` - Generated charts
- `signals/` - Scan results

---

## ⚠️ Important Notes

### What This System DOES
✅ Scans entire market automatically
✅ Finds best opportunities with AI
✅ Runs multiple proven strategies
✅ Provides complete trade setups
✅ Monitors risk and portfolio
✅ Sends consolidated alerts

### What This System DOES NOT
❌ Execute trades (you review first)
❌ Guarantee profits (no system can)
❌ Replace your judgment
❌ Work without internet/APIs

### Risk Disclaimer
- Not financial advice
- Past performance ≠ future results
- Always do your own research
- Start with paper trading
- Risk only what you can afford to lose

---

## 🆘 Troubleshooting

### "Finnhub API key not found"
```bash
# Add to .env file
FINNHUB_API_KEY=your_key_here
```
Get free key: https://finnhub.io

### "FinBERT failed"
- System falls back to keyword sentiment
- Or install: `pip install -r requirements-finbert.txt`

### "No symbols found"
- Check internet connection
- Verify Finnhub API key
- System uses cached symbols if API fails

### "Scan too slow"
- Reduce `max_symbols_per_run` in config
- Use tier: "daily" instead of "full"
- Run during off-hours

---

## 🎓 Learn More

- **[README.md](README.md)** - Quick start
- **[config/master_config.yaml](config/master_config.yaml)** - All settings
- **[docs/](docs/)** - Technical documentation

---

**Made with ❤️ for intelligent, data-driven trading**

*"Stop guessing. Start scanning."*
