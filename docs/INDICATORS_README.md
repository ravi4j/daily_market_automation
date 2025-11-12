# 📊 Technical Indicators - Quick Start

Add 50+ professional technical indicators to your trading system in minutes!

## 🚀 One-Line Setup

```bash
pip install --index-url https://pypi.org/simple/ pandas-ta
```

## 💡 5-Minute Example

```python
from src.indicators import TechnicalIndicators
import pandas as pd

# 1. Load your data
df = pd.read_csv('data/AAPL.csv', index_col='Date', parse_dates=True)

# 2. Add indicators
indicators = TechnicalIndicators(df)
indicators.add_rsi(14)           # Relative Strength Index
indicators.add_macd()            # MACD
indicators.add_bbands()          # Bollinger Bands
indicators.add_sma(20)           # 20-day Moving Average
indicators.add_adx()             # Trend Strength

# 3. Get signals
latest = indicators.df.iloc[-1]
print(f"RSI: {latest['RSI_14']:.2f}")
print(f"Price vs SMA20: {'Above' if latest['Close'] > latest['SMA_20'] else 'Below'}")
```

## 📚 What's Available?

### Popular Indicators by Category

**Momentum** (13 indicators)
- RSI, MACD, Stochastic, Williams %R, CCI, ROC, CMO, Ultimate Oscillator

**Trend** (13 indicators)
- SMA, EMA, HMA, DEMA, TEMA, ADX, Aroon, Parabolic SAR, SuperTrend, Ichimoku

**Volatility** (6 indicators)
- Bollinger Bands, Keltner Channels, Donchian Channels, ATR

**Volume** (14 indicators)
- OBV, AD, CMF, MFI, VWAP, Klinger Volume, Elder's Force Index

**Statistics** (5 indicators)
- Z-Score, Entropy, Standard Deviation, Variance, MAD

**Total: 51 Indicators!**

## 🎯 Real Trading Examples

### Example 1: Golden Cross Detection
```python
indicators = TechnicalIndicators(df)
indicators.add_sma(50)
indicators.add_sma(200)

latest = indicators.df.iloc[-1]
if latest['SMA_50'] > latest['SMA_200']:
    print("🟢 GOLDEN CROSS - Bullish!")
```

### Example 2: RSI Overbought/Oversold
```python
indicators.add_rsi(14)
rsi = indicators.df.iloc[-1]['RSI_14']

if rsi > 70:
    print("⚠️  OVERBOUGHT - Consider selling")
elif rsi < 30:
    print("💰 OVERSOLD - Buying opportunity")
```

### Example 3: MACD Signal
```python
indicators.add_macd()
latest = indicators.df.iloc[-1]

if latest['MACD_12_26_9'] > latest['MACDs_12_26_9']:
    print("🟢 BULLISH - MACD crossed above signal")
else:
    print("🔴 BEARISH - MACD crossed below signal")
```

### Example 4: Bollinger Band Squeeze
```python
indicators.add_bbands()
df = indicators.df

# Find BB columns
bb_upper = [col for col in df.columns if 'BBU' in col][0]
bb_lower = [col for col in df.columns if 'BBL' in col][0]
bb_middle = [col for col in df.columns if 'BBM' in col][0]

# Calculate width
width = (df[bb_upper] - df[bb_lower]) / df[bb_middle]

if width.iloc[-1] < width.mean() * 0.7:
    print("🔥 SQUEEZE DETECTED - Breakout imminent!")
```

## 📖 Full Documentation

- **Complete Guide**: See [docs/indicators-guide.md](indicators-guide.md)
- **API Reference**: See [src/indicators.py](../src/indicators.py)
- **Examples**: Run `python examples/demo_indicators_simple.py`

## 🔗 Integration

### Use with Breakout Detection

```python
from src.indicators import TechnicalIndicators
from src.detect_breakouts import analyze_symbol

# Add indicators to your analysis
def analyze_with_indicators(symbol):
    df = load_data(symbol)

    # Add indicators
    indicators = TechnicalIndicators(df)
    indicators.add_rsi(14)
    indicators.add_macd()
    indicators.add_adx()

    df = indicators.df
    latest = df.iloc[-1]

    # Your existing breakout logic
    breakouts = analyze_symbol(symbol)

    # Add indicator confirmation
    if latest['RSI_14'] < 70 and latest['ADX_14'] > 25:
        breakouts['confirmed'] = True

    return breakouts
```

## 🎓 Learning Resources

- **Investopedia**: https://www.investopedia.com/technical-analysis-4689657
- **pandas-ta GitHub**: https://github.com/twopirllc/pandas-ta
- **TradingView Education**: https://www.tradingview.com/education/

## 💡 Pro Tips

1. **Start Simple**: Use RSI, MACD, and moving averages first
2. **Combine Categories**: Trend + Momentum + Volume = stronger signals
3. **Don't Overfit**: More indicators ≠ better results
4. **Backtest**: Always test your strategy on historical data
5. **Confirm Price Action**: Use indicators to confirm, not predict

## 🚦 Quick Commands

```bash
# Run demo
python examples/demo_indicators_simple.py

# List all available indicators
python src/indicators.py

# Install with all dependencies
pip install -r requirements-indicators.txt
```

## 📊 Sample Output

```
📊 Technical Indicators Demo
================================================================================

✅ Loaded 3774 days of TQQQ data
   From: 2010-11-09 to 2025-11-10

📈 Latest Values (2025-11-10):
--------------------------------------------------------------------------------
Close:    $110.03
SMA 20:   $110.08
SMA 50:   $103.94
RSI:      51.60
MACD:     2.02
ATR:      $5.05

🎯 Trading Signals:
--------------------------------------------------------------------------------
✅ Price above SMA50 - BULLISH
✅ RSI Neutral (30-70)
🔴 MACD Bearish (below signal)
```

## ⚡ Performance

- **Fast**: Indicators calculate in milliseconds
- **Memory Efficient**: Only adds columns you need
- **Production Ready**: Handles missing data gracefully
- **Type Safe**: Full pandas DataFrame integration

---

**Ready to level up your trading system? Start with `python examples/demo_indicators_simple.py`!** 🚀
