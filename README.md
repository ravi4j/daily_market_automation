# 🤖 Intelligent Daily Market Scanner

**AI-Powered Trading System** that scans the **ENTIRE US market** daily and tells you exactly what to buy.

## 🎯 What Makes This Different?

**YOU DON'T TELL IT WHAT TO SCAN - IT TELLS YOU WHAT TO BUY!**

- 🧠 **Intelligent**: Scans 1000s of stocks/ETFs automatically
- 🎯 **Smart Filtering**: Finds opportunities based on price drops, volume spikes, technical signals
- 📊 **Multi-Signal Scoring**: News (FinBERT AI) + Technicals + Fundamentals + Insider Activity
- 📱 **One Daily Alert**: Top 5 best opportunities with complete trade setups
- ⚡ **Fast**: 2-phase scanning (quick pre-screen → deep analysis)

## ⚡ Quick Start (5 Minutes)

### macOS / Linux

```bash
# 1. Clone and setup
git clone https://github.com/ravi4j/daily_market_automation.git
cd daily_market_automation
./scripts/setup_local.sh

# 2. Configure credentials (get keys from finnhub.io and Telegram)
nano .env

# Add:
# FINNHUB_API_KEY=your_key_here
# TELEGRAM_BOT_TOKEN=your_token_here
# TELEGRAM_CHAT_ID=your_chat_id_here

# 3. Run master scanner
./scripts/run_master_scan.sh
```

### Windows 11

```powershell
# 1. Clone and setup
git clone https://github.com/ravi4j/daily_market_automation.git
cd daily_market_automation
.\scripts\setup_local.bat

# 2. Configure credentials
notepad .env

# Add:
# FINNHUB_API_KEY=your_key_here
# TELEGRAM_BOT_TOKEN=your_token_here
# TELEGRAM_CHAT_ID=your_chat_id_here

# 3. Run master scanner
.\scripts\run_master_scan.bat
```

## 📊 What You Get Daily

**ONE Telegram message with:**

```
🔍 DAILY MARKET SCAN - 2024-11-20 16:30 ET
═══════════════════════════════════════

📊 MARKET STATUS
S&P 500: +0.8% | VIX: 18.5 (Normal) | Risk: MODERATE

🚀 TOP 5 OPPORTUNITIES (from 1,247 symbols scanned)

1. NVDA - STRONG BUY (Score: 89/100)
   Entry: $485 | Target: $525 | Stop: $470 | R/R: 2.7
   Why: Strong earnings beat + RSI oversold + insider buying
   📈 Tech: 88 | 📰 News: 92 | 💼 Fund: 85 | 👔 Insider: 90

2. UNH - BUY (Score: 82/100)
   Entry: $512 | Target: $548 | Stop: $498 | R/R: 2.5
   Why: -5% news dip + solid fundamentals + sector rotation
   📈 Tech: 78 | 📰 News: 85 | 💼 Fund: 82 | 👔 Insider: 80

... (3 more)

⚖️ YOUR PORTFOLIO (optional - monitors your positions)
✅ TQQQ: On target
⚠️ AAPL: 15% overweight - Consider taking profits

🛡️ RISK ASSESSMENT
Portfolio Exposure: 85% (Target: 80%)
Recommendation: Add defensive position (TLT or GLD)
```

## 🧠 How It Works (Intelligent Scanning)

### Phase 1: Quick Pre-Screen (FAST - scans 1000s)
```
Automatically filters ENTIRE market for:
✓ Price drops (3-10%) = potential opportunities
✓ Volume spikes = something happening
✓ Healthy technicals = not catching falling knives
✓ Quality filters = liquid, tradeable stocks
```

### Phase 2: Deep Analysis (SMART - top 50-100)
```
Multi-signal composite scoring (0-100):
• News Sentiment (30%) - FinBERT AI analysis
• Technical Analysis (40%) - RSI, MACD, trends
• Fundamentals (20%) - P/E, margins, growth
• Insider Activity (10%) - Smart money tracking
```

### Output
```
Top 5 opportunities with:
- Complete trade setup (entry, stop, target)
- Risk/reward ratios
- Confidence scores
- Specific reasons WHY to buy
```

## 🎯 Core Features

### ✨ Intelligent Market Scanning
- **Auto Symbol Selection**: Scans entire US market (stocks + ETFs)
- **Smart Pre-Screening**: Filters for price drops, volume spikes, technical signals
- **No Manual Lists**: System finds opportunities automatically
- **Tiered Scanning**: Daily (~600 symbols), Weekly (~2000), Monthly (full 10,000)

### 🤖 FinBERT AI Sentiment
- **ML-Powered**: Financial-specific BERT model for news analysis
- **GPU Support**: Auto-detects GPU for faster processing
- **Free & Open Source**: No API costs

### 👔 Insider Tracking
- **Follow Smart Money**: Track insider buying/selling
- **Finnhub Integration**: Real-time insider transactions
- **Score Adjustment**: Boosts score for insider buying, reduces for selling

### 📊 Technical Analysis
- **50+ Indicators**: RSI, MACD, Bollinger Bands, ADX, ATR, etc.
- **Pattern Detection**: ABC patterns, breakouts, reversals
- **Trend Analysis**: Identify uptrends, downtrends, consolidations

### 💼 Fundamental Analysis
- **Company Health**: P/E ratio, profit margins, revenue growth
- **Analyst Ratings**: Consensus recommendations
- **Quality Filters**: Avoid penny stocks, low volume, OTC

### 📱 Smart Alerts
- **One Consolidated Message**: No spam, just actionable insights
- **Telegram Integration**: Alerts sent after market close
- **Complete Trade Setups**: Entry, stop loss, target, risk/reward

## 🚀 Advanced Usage

### Configuration (`config/master_config.yaml`)

```yaml
# Scanning strategy
scanning:
  strategy:
    tier: "daily"  # Options: daily, weekly, monthly, full

  intelligent_filters:
    min_price_drop_pct: 3.0      # Look for 3%+ drops
    min_volume_ratio: 1.2         # 20%+ volume spike
    min_price: 5.0                # Skip penny stocks

# Scoring weights (customize to your style)
scoring:
  weights:
    news_sentiment: 30   # 30%
    technical: 40        # 40%
    fundamentals: 20     # 20%
    insider_activity: 10 # 10%

  max_opportunities: 5   # Show top 5
  min_confidence: 70     # Only HIGH confidence

# Portfolio (optional - monitors YOUR existing positions)
portfolio:
  positions: {}  # Leave empty for pure opportunity scanning
  
  # Example: Add your actual positions to monitor
  # positions:
  #   TQQQ: 100    # 100 shares
  #   AAPL: 50     # 50 shares
```

### Run Locally

```bash
# macOS/Linux - Daily scan
./scripts/run_master_scan.sh

# Windows - Daily scan
.\scripts\run_master_scan.bat
```

### GitHub Actions (Automatic)

The system runs automatically via GitHub Actions:
- **Daily**: 4:30 PM ET (after market close)
- **Weekly**: Monday 6 PM ET (comprehensive scan)
- **Pre-market**: 8 AM ET (gap monitoring)

## 📦 Requirements

- **Python**: 3.12+
- **API Keys** (free):
  - Finnhub (60 calls/min free tier)
  - Telegram Bot
- **Optional**:
  - NVIDIA GPU (for faster FinBERT)
  - No GPU? CPU works fine (just slower)

## 🔧 Installation

### Automatic Setup (Recommended)

```bash
# macOS/Linux
./scripts/setup_local.sh

# Windows
.\scripts\setup_local.bat
```

### Manual Setup

```bash
# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate     # Windows

# 2. Install dependencies
pip install -r requirements-base.txt
pip install -r requirements-fetch.txt
pip install -r requirements-indicators.txt
pip install -r requirements-finbert.txt  # For FinBERT

# 3. Configure environment
cp .env.example .env
nano .env  # Add your API keys

# 4. Run
python scripts/master_daily_scan.py
```

## 📚 Documentation

- **[Master Config Guide](config/master_config.yaml)** - All configuration options
- **[Technical Docs](docs/)** - Architecture, workflows, indicators
- **[Changelog](CHANGELOG.md)** - Version history

## 🎯 What This System Does

### ✅ DOES (Automatic)
- Scans entire US market daily
- Finds best opportunities automatically
- Multi-signal analysis (News + Technical + Fundamental + Insider)
- Sends ONE consolidated alert with top 5 trades
- Complete trade setups (entry, stop, target)
- Risk management recommendations

### ❌ DOES NOT
- Execute trades (you review and decide)
- Require you to pick symbols manually
- Send multiple alerts (just one clean message)
- Cost money for API usage (free tier sufficient)

## 🤝 Contributing

This is a personal trading system, but feel free to:
- Fork and customize for your needs
- Report bugs via Issues
- Suggest improvements

## ⚖️ Disclaimer

**This is for educational and informational purposes only.**

- Not financial advice
- Past performance ≠ future results
- Always do your own research
- Trade at your own risk
- Start with paper trading

## 📝 License

MIT License - See [LICENSE](LICENSE) file

## 🙋 Questions?

Open an issue on GitHub or check the [docs](docs/) folder.

---

**Made with ❤️ for intelligent, data-driven trading**

*"You don't tell it what to scan. It tells you what to buy."*
