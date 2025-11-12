# Technical Indicators Guide

Comprehensive guide to using 50+ technical indicators with `pandas-ta` in your trading system.

## Table of Contents
- [Quick Start](#quick-start)
- [Available Indicators](#available-indicators)
- [Usage Examples](#usage-examples)
- [Integration with Signal Generation](#integration)

---

## Quick Start

### Installation

```bash
# Install indicators library
pip install --index-url https://pypi.org/simple/ pandas-ta

# Or use the requirements file
pip install -r requirements-indicators.txt
```

### Basic Usage

```python
from src.indicators import TechnicalIndicators

# Load your OHLCV data
df = pd.read_csv('data/AAPL.csv', index_col='Date', parse_dates=True)

# Create indicators instance
indicators = TechnicalIndicators(df)

# Add specific indicators
indicators.add_rsi(14)
indicators.add_macd()
indicators.add_bbands()

# Get DataFrame with indicators
df_with_indicators = indicators.df

# Access latest values
latest = df_with_indicators.iloc[-1]
print(f"RSI: {latest['RSI_14']:.2f}")
print(f"MACD: {latest['MACD_12_26_9']:.2f}")
```

---

## Available Indicators

### 📈 Momentum Indicators (13)
Perfect for identifying overbought/oversold conditions and trend strength.

| Indicator | Function | Key Parameters | Typical Values |
|-----------|----------|----------------|----------------|
| **RSI** | `add_rsi(length=14)` | length | >70 overbought, <30 oversold |
| **MACD** | `add_macd(fast=12, slow=26, signal=9)` | fast, slow, signal | Cross signals |
| **Stochastic** | `add_stochastic(k=14, d=3)` | k, d | >80 overbought, <20 oversold |
| **Stochastic RSI** | `add_stochrsi()` | length, rsi_length | >0.8 overbought, <0.2 oversold |
| **CCI** | `add_cci(length=20)` | length | >100 overbought, <-100 oversold |
| **Williams %R** | `add_willr(length=14)` | length | >-20 overbought, <-80 oversold |
| **ROC** | `add_roc(length=12)` | length | Rate of price change |
| **CMO** | `add_cmo(length=14)` | length | Chande Momentum |
| **Fisher Transform** | `add_fisher(length=9)` | length | Gaussian price distribution |
| **Awesome Oscillator** | `add_ao()` | - | SMA difference |
| **Know Sure Thing** | `add_kst()` | - | Multiple timeframes |
| **True Strength Index** | `add_tsi()` | fast, slow | Momentum strength |
| **Ultimate Oscillator** | `add_uo()` | - | Multi-timeframe momentum |

### 📊 Trend Indicators (13)
Identify and confirm trend direction.

| Indicator | Function | Key Parameters | Usage |
|-----------|----------|----------------|-------|
| **SMA** | `add_sma(length=20)` | length | Classic moving average |
| **EMA** | `add_ema(length=20)` | length | Exponential weighting |
| **WMA** | `add_wma(length=20)` | length | Linear weighting |
| **HMA** | `add_hma(length=20)` | length | Hull - reduced lag |
| **ALMA** | `add_alma(length=20)` | length | Arnaud Legoux |
| **DEMA** | `add_dema(length=20)` | length | Double exponential |
| **TEMA** | `add_tema(length=20)` | length | Triple exponential |
| **ADX** | `add_adx(length=14)` | length | Trend strength (>25 = strong) |
| **Aroon** | `add_aroon(length=25)` | length | Up/down trend signals |
| **Parabolic SAR** | `add_psar()` | - | Stop and reverse points |
| **SuperTrend** | `add_supertrend(length=7, multiplier=3.0)` | length, multiplier | Trend-following |
| **Vortex** | `add_vortex(length=14)` | length | Directional movement |
| **Ichimoku** | `add_ichimoku()` | - | Cloud support/resistance |

### 💨 Volatility Indicators (6)
Measure market volatility for risk management.

| Indicator | Function | Key Parameters | Usage |
|-----------|----------|----------------|-------|
| **Bollinger Bands** | `add_bbands(length=20, std=2.0)` | length, std | Price channels |
| **Keltner Channels** | `add_kc(length=20, scalar=2.0)` | length, scalar | ATR-based channels |
| **Donchian Channels** | `add_dc(length=20)` | length | High/low channels |
| **ATR** | `add_atr(length=14)` | length | Average true range |
| **NATR** | `add_natr(length=14)` | length | Normalized ATR |
| **Ulcer Index** | `add_ui(length=14)` | length | Downside volatility |

### 📦 Volume Indicators (14)
Confirm price movements with volume analysis.

| Indicator | Function | Key Parameters | Usage |
|-----------|----------|----------------|-------|
| **OBV** | `add_obv()` | - | On-balance volume |
| **AD** | `add_ad()` | - | Accumulation/Distribution |
| **Chaikin Oscillator** | `add_adosc(fast=3, slow=10)` | fast, slow | AD momentum |
| **CMF** | `add_cmf(length=20)` | length | Chaikin money flow |
| **EFI** | `add_efi(length=13)` | length | Elder's force index |
| **EOM** | `add_eom(length=14)` | length | Ease of movement |
| **KVO** | `add_kvo(fast=34, slow=55)` | fast, slow | Klinger volume |
| **MFI** | `add_mfi(length=14)` | length | Money flow index |
| **NVI** | `add_nvi()` | - | Negative volume index |
| **PVI** | `add_pvi()` | - | Positive volume index |
| **PVOL** | `add_pvol()` | - | Price volume |
| **PVT** | `add_pvt()` | - | Price volume trend |
| **VWAP** | `add_vwap()` | - | Volume-weighted avg price |
| **VWMA** | `add_vwma(length=20)` | length | Volume-weighted MA |

### 📊 Statistics (5)
Statistical measures for analysis.

| Indicator | Function | Key Parameters | Usage |
|-----------|----------|----------------|-------|
| **Z-Score** | `add_zscore(length=30)` | length | Standard deviations from mean |
| **Entropy** | `add_entropy(length=10)` | length | Measure of randomness |
| **MAD** | `add_mad(length=30)` | length | Mean absolute deviation |
| **Variance** | `add_variance(length=30)` | length | Statistical variance |
| **Std Dev** | `add_stdev(length=30)` | length | Standard deviation |

---

## Usage Examples

### Example 1: Common Indicators (Quick Setup)

```python
from src.indicators import calculate_indicators

# Load data
df = pd.read_csv('data/TQQQ.csv', index_col='Date', parse_dates=True)

# Add all common indicators at once
df_with_indicators = calculate_indicators(df, preset='common')

# Common indicators include:
# - SMAs (20, 50, 200)
# - EMAs (20, 50)
# - RSI, MACD, Stochastic
# - Bollinger Bands, ATR
# - OBV, CMF, MFI
# - ADX
```

### Example 2: Custom Indicator Selection

```python
from src.indicators import TechnicalIndicators

df = pd.read_csv('data/AAPL.csv', index_col='Date', parse_dates=True)
indicators = TechnicalIndicators(df)

# Add only what you need
indicators.add_rsi(14)
indicators.add_macd()
indicators.add_supertrend()
indicators.add_adx()

# Get result
df_indicators = indicators.df
```

### Example 3: Multiple Moving Averages

```python
indicators = TechnicalIndicators(df)

# Short-term
indicators.add_sma(10)
indicators.add_sma(20)

# Medium-term
indicators.add_sma(50)
indicators.add_sma(100)

# Long-term
indicators.add_sma(200)

# Golden Cross detection
latest = indicators.df.iloc[-1]
if latest['SMA_50'] > latest['SMA_200']:
    print("Golden Cross - Bullish!")
```

### Example 4: RSI Divergence Detection

```python
indicators = TechnicalIndicators(df)
indicators.add_rsi(14)

df = indicators.df.tail(50)

# Find bearish divergence
# Price makes higher high, RSI makes lower high
price_highs = df['Close'].rolling(window=5, center=True).max()
rsi_highs = df['RSI_14'].rolling(window=5, center=True).max()

# Compare recent highs
if price_highs.iloc[-1] > price_highs.iloc[-10] and \
   rsi_highs.iloc[-1] < rsi_highs.iloc[-10]:
    print("Bearish divergence detected!")
```

### Example 5: Bollinger Band Squeeze

```python
indicators = TechnicalIndicators(df)
indicators.add_bbands(length=20, std=2.0)

df = indicators.df
bb_upper = [col for col in df.columns if 'BBU' in col][0]
bb_lower = [col for col in df.columns if 'BBL' in col][0]
bb_middle = [col for col in df.columns if 'BBM' in col][0]

# Calculate bandwidth
df['BB_Width'] = (df[bb_upper] - df[bb_lower]) / df[bb_middle]

# Detect squeeze (low volatility = potential breakout)
current_width = df['BB_Width'].iloc[-1]
avg_width = df['BB_Width'].tail(50).mean()

if current_width < avg_width * 0.7:
    print("Squeeze detected - expect breakout!")
```

---

## Integration with Signal Generation

### Enhance Your Breakout Detection

Integrate indicators into `src/detect_breakouts.py`:

```python
from indicators import TechnicalIndicators

def analyze_symbol_with_indicators(symbol: str):
    """Enhanced analysis with technical indicators"""

    # Load data
    df = load_data(symbol)

    # Add indicators
    indicators = TechnicalIndicators(df)
    indicators.add_rsi(14)
    indicators.add_macd()
    indicators.add_adx()
    indicators.add_bbands()

    df = indicators.df
    latest = df.iloc[-1]

    # Existing breakout detection
    breakouts = detect_trendline_breakout(df)

    # Add indicator confirmation
    confirmation_score = 0

    # RSI confirmation
    if 30 < latest['RSI_14'] < 70:
        confirmation_score += 1

    # MACD confirmation
    if latest['MACD_12_26_9'] > latest['MACDs_12_26_9']:
        confirmation_score += 1

    # ADX trend strength
    if latest['ADX_14'] > 25:
        confirmation_score += 1

    # Volume confirmation (existing)
    # ... your existing code ...

    return {
        'breakouts': breakouts,
        'confirmation_score': confirmation_score,
        'indicators': {
            'rsi': latest['RSI_14'],
            'macd': latest['MACD_12_26_9'],
            'adx': latest['ADX_14']
        }
    }
```

### Signal Scoring System

```python
def calculate_signal_strength(df, latest):
    """Calculate overall signal strength using multiple indicators"""

    score = 0
    max_score = 10

    # Trend (3 points)
    if latest['Close'] > latest['SMA_50'] > latest['SMA_200']:
        score += 3
    elif latest['Close'] > latest['SMA_50']:
        score += 2
    elif latest['Close'] > latest['SMA_20']:
        score += 1

    # Momentum (3 points)
    if 40 < latest['RSI_14'] < 60:
        score += 1  # Neutral = sustainable
    if latest['MACD_12_26_9'] > latest['MACDs_12_26_9']:
        score += 1
    if latest['ADX_14'] > 25:
        score += 1

    # Volatility (2 points)
    atr_pct = (latest['ATR_14'] / latest['Close']) * 100
    if 1 < atr_pct < 5:  # Reasonable volatility
        score += 1

    # Bollinger position
    bb_upper = [col for col in df.columns if 'BBU' in col][0]
    bb_lower = [col for col in df.columns if 'BBL' in col][0]
    bb_pct = [col for col in df.columns if 'BBP' in col][0]

    if 0.2 < latest[bb_pct] < 0.8:  # Not at extremes
        score += 1

    # Volume (2 points)
    vol_ratio = latest['Volume'] / df['Volume'].tail(20).mean()
    if vol_ratio > 1.5:
        score += 2
    elif vol_ratio > 1.0:
        score += 1

    return score, max_score
```

---

## Best Practices

### 1. **Don't Overfit**
- Start with common indicators (RSI, MACD, MA)
- Add more only if they provide unique insights
- Too many indicators = analysis paralysis

### 2. **Combine Different Categories**
- Trend + Momentum + Volume = stronger signals
- Example: Price > SMA50 + RSI < 70 + Volume spike

### 3. **Adjust for Timeframe**
- Day trading: Shorter periods (RSI 9, SMA 10/20)
- Swing trading: Medium periods (RSI 14, SMA 20/50)
- Position trading: Longer periods (RSI 21, SMA 50/200)

### 4. **Backtest Your Strategy**
- Test indicators on historical data
- Measure win rate, profit factor, drawdown
- Adjust parameters based on results

### 5. **Use Indicators for Confirmation**
- Don't trade on indicators alone
- Use them to confirm price action
- Wait for multiple indicators to align

---

## Quick Reference

### Run Demo
```bash
python examples/demo_indicators_simple.py
```

### List All Indicators
```python
from src.indicators import get_available_indicators

indicators = get_available_indicators()
for category, indicator_list in indicators.items():
    print(f"{category}: {len(indicator_list)} indicators")
```

### Add All Indicators (Heavy)
```python
indicators = TechnicalIndicators(df)
df_all = indicators.add_all_indicators()
print(f"Total columns: {len(df_all.columns)}")
```

---

## Resources

- **pandas-ta Documentation**: https://github.com/twopirllc/pandas-ta
- **TradingView Indicators**: https://www.tradingview.com/scripts/
- **Investopedia**: https://www.investopedia.com/technical-analysis-4689657

---

## Support

For questions or issues:
1. Check `examples/demo_indicators_simple.py`
2. Review `src/indicators.py` source code
3. See pandas-ta documentation

Happy Trading! 📈
