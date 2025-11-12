# 🔬 Backtesting Guide

Complete guide to testing and optimizing trading strategies with historical data.

## Table of Contents
- [Quick Start](#quick-start)
- [Understanding Backtesting](#understanding-backtesting)
- [Pre-Built Strategies](#pre-built-strategies)
- [Custom Strategies](#custom-strategies)
- [Performance Metrics](#performance-metrics)
- [Parameter Optimization](#parameter-optimization)
- [Best Practices](#best-practices)

---

## Quick Start

### 5-Minute Backtest

```python
from src.indicators import TechnicalIndicators
from src.backtester import Backtester, rsi_strategy
import pandas as pd

# 1. Load data
df = pd.read_csv('data/TQQQ.csv', index_col='Date', parse_dates=True)

# 2. Add indicators
indicators = TechnicalIndicators(df)
indicators.add_rsi(14)

# 3. Run backtest
backtester = Backtester(indicators.df, symbol='TQQQ', initial_capital=10000)
results = backtester.run_strategy(rsi_strategy, "RSI Strategy")

# 4. View results
print(f"Return: {results.total_return_pct:.2f}%")
print(f"Win Rate: {results.win_rate:.2f}%")
```

### Run Pre-Built Demo

```bash
python examples/quick_backtest.py
```

---

## Understanding Backtesting

### What is Backtesting?

Backtesting is testing a trading strategy on historical data to see how it would have performed. It helps you:

- **Validate ideas** before risking real money
- **Compare strategies** objectively
- **Optimize parameters** for better performance
- **Understand risk** (drawdowns, win rate, etc.)

### How It Works

1. **Historical Data**: Load OHLCV price data
2. **Indicators**: Calculate technical indicators
3. **Strategy Logic**: Define buy/sell rules
4. **Simulate Trades**: Execute trades based on rules
5. **Calculate Results**: Measure performance metrics

### Important Limitations

⚠️ **Backtesting is NOT perfect:**
- Past performance ≠ future results
- Can't account for market changes
- Doesn't include slippage/commissions (by default)
- Risk of overfitting
- Survivorship bias in data

---

## Pre-Built Strategies

### 1. RSI Strategy

**Logic:**
- Buy when RSI < 30 (oversold)
- Sell when RSI > 70 (overbought)

```python
from src.backtester import rsi_strategy

indicators.add_rsi(14)
results = backtester.run_strategy(rsi_strategy, "RSI")
```

**Typical Performance:**
- Good for mean reversion markets
- High win rate (70-90%)
- Fewer trades

### 2. MACD Crossover

**Logic:**
- Buy when MACD crosses above signal line
- Sell when MACD crosses below signal line

```python
from src.backtester import macd_crossover_strategy

indicators.add_macd()
results = backtester.run_strategy(macd_crossover_strategy, "MACD")
```

**Typical Performance:**
- Good for trending markets
- Moderate win rate (50-65%)
- More trades

### 3. Moving Average Crossover

**Logic:**
- Buy when SMA20 crosses above SMA50
- Sell when SMA20 crosses below SMA50

```python
from src.backtester import moving_average_crossover_strategy

indicators.add_sma(20)
indicators.add_sma(50)
results = backtester.run_strategy(moving_average_crossover_strategy, "MA Cross")
```

**Typical Performance:**
- Classic trend-following
- Moderate win rate (50-60%)
- Long holding periods

### 4. Bollinger Band Bounce

**Logic:**
- Buy when price touches lower band
- Sell when price touches upper band

```python
from src.backtester import bollinger_bounce_strategy

indicators.add_bbands()
results = backtester.run_strategy(bollinger_bounce_strategy, "BB Bounce")
```

**Typical Performance:**
- Mean reversion strategy
- Good in ranging markets
- Quick trades

### 5. Multi-Indicator Confirmation

**Logic:**
- Buy when: RSI < 40 AND MACD bullish AND ADX > 20
- Sell when: RSI > 60 OR MACD bearish

```python
from src.backtester import multi_indicator_strategy

indicators.add_rsi(14)
indicators.add_macd()
indicators.add_adx()
results = backtester.run_strategy(multi_indicator_strategy, "Multi-Indicator")
```

**Typical Performance:**
- More selective entries
- Higher win rate
- Fewer trades

---

## Custom Strategies

### Strategy Template

```python
def my_strategy(row, position):
    """
    Args:
        row: Current bar data (pandas Series with OHLCV + indicators)
        position: Current open position (Trade object or None)

    Returns:
        'BUY', 'SELL', or 'HOLD'
    """

    # Check if indicators exist
    if 'RSI_14' not in row.index:
        return 'HOLD'

    # Get indicator values
    rsi = row['RSI_14']
    price = row['Close']

    # Entry logic (when position is None)
    if position is None:
        if rsi < 30:  # Oversold
            return 'BUY'

    # Exit logic (when position exists)
    else:
        if rsi > 70:  # Overbought
            return 'SELL'

    return 'HOLD'
```

### Example 1: Trend + Momentum

```python
def trend_momentum_strategy(row, position):
    """Buy when price is in uptrend AND momentum is strong"""

    required = ['SMA_20', 'SMA_50', 'RSI_14', 'ADX_14']
    if not all(ind in row.index for ind in required):
        return 'HOLD'

    price = row['Close']
    sma20 = row['SMA_20']
    sma50 = row['SMA_50']
    rsi = row['RSI_14']
    adx = row['ADX_14']

    if position is None:
        # Buy conditions: All must be true
        if (price > sma20 > sma50 and  # Uptrend
            rsi > 50 and rsi < 70 and   # Momentum but not overbought
            adx > 25):                  # Strong trend
            return 'BUY'
    else:
        # Sell conditions: Any is true
        if (price < sma20 or            # Trend broken
            rsi < 40 or                 # Momentum lost
            adx < 20):                  # Trend weakening
            return 'SELL'

    return 'HOLD'
```

### Example 2: Mean Reversion with Volume

```python
def volume_mean_reversion(row, position):
    """Buy dips with volume confirmation"""

    if 'RSI_14' not in row.index:
        return 'HOLD'

    rsi = row['RSI_14']
    volume = row['Volume']

    # Get BB columns
    bb_lower = [col for col in row.index if 'BBL' in col]
    if not bb_lower:
        return 'HOLD'

    price = row['Close']
    lower_band = row[bb_lower[0]]

    # Calculate volume MA (would need to add this indicator)

    if position is None:
        # Buy on oversold with volume spike
        if (rsi < 35 and
            price < lower_band * 1.01):  # Near lower BB
            return 'BUY'
    else:
        # Exit on reversion
        if rsi > 60:
            return 'SELL'

    return 'HOLD'
```

### Example 3: Breakout Strategy

```python
def breakout_strategy(row, position):
    """Buy on volatility breakout"""

    # Find Donchian Channel columns
    dc_upper = [col for col in row.index if 'DCU' in col]
    if not dc_upper:
        return 'HOLD'

    price = row['Close']
    dc_high = row[dc_upper[0]]

    if 'ATR_14' not in row.index:
        return 'HOLD'

    atr = row['ATR_14']

    if position is None:
        # Buy on breakout above 20-day high
        if price > dc_high:
            return 'BUY'
    else:
        # Exit with ATR-based stop
        entry_price = position.entry_price
        if price < entry_price - (2 * atr):
            return 'SELL'

    return 'HOLD'
```

---

## Performance Metrics

### Key Metrics Explained

| Metric | Description | Good Value |
|--------|-------------|------------|
| **Total Return %** | Overall profit/loss | > 0% (positive) |
| **Win Rate** | % of winning trades | > 50% |
| **Profit Factor** | Gross profit / Gross loss | > 1.5 |
| **Max Drawdown** | Largest peak-to-trough decline | < 20% |
| **Sharpe Ratio** | Return per unit of risk | > 1.0 |
| **Avg Win** | Average profit per winning trade | > Avg Loss |
| **Avg Loss** | Average loss per losing trade | Small & controlled |
| **Number of Trades** | Total trades executed | Enough for statistics (>30) |

### Interpreting Results

**Strong Strategy:**
- Win rate > 60%
- Profit factor > 2.0
- Max drawdown < 15%
- Sharpe ratio > 1.5

**Acceptable Strategy:**
- Win rate 50-60%
- Profit factor 1.5-2.0
- Max drawdown 15-25%
- Sharpe ratio 1.0-1.5

**Weak Strategy:**
- Win rate < 50%
- Profit factor < 1.2
- Max drawdown > 30%
- Sharpe ratio < 0.5

---

## Parameter Optimization

### Optimize RSI Parameters

```python
from src.backtester import optimize_rsi_parameters

# Test different RSI combinations
results_df = optimize_rsi_parameters(
    df,
    symbol='AAPL',
    rsi_lengths=[9, 14, 21],
    oversold_levels=[25, 30, 35],
    overbought_levels=[65, 70, 75]
)

# View best parameters
print(results_df.head())
```

### Custom Parameter Grid Search

```python
def optimize_ma_crossover(df, symbol):
    """Optimize moving average crossover parameters"""

    results = []

    for fast in [10, 20, 30]:
        for slow in [50, 100, 200]:
            if fast >= slow:
                continue

            # Add indicators
            indicators = TechnicalIndicators(df)
            indicators.add_sma(fast)
            indicators.add_sma(slow)

            # Define strategy with these parameters
            def ma_strategy(row, position):
                if f'SMA_{fast}' not in row.index:
                    return 'HOLD'

                fast_ma = row[f'SMA_{fast}']
                slow_ma = row[f'SMA_{slow}']

                if position is None and fast_ma > slow_ma:
                    return 'BUY'
                elif position is not None and fast_ma < slow_ma:
                    return 'SELL'

                return 'HOLD'

            # Backtest
            backtester = Backtester(indicators.df, symbol=symbol)
            result = backtester.run_strategy(ma_strategy, f"MA{fast}/{slow}")

            results.append({
                'fast': fast,
                'slow': slow,
                'return_pct': result.total_return_pct,
                'win_rate': result.win_rate,
                'profit_factor': result.profit_factor
            })

    return pd.DataFrame(results).sort_values('return_pct', ascending=False)
```

---

## Best Practices

### 1. **Use Enough Data**
- Minimum: 1-2 years
- Ideal: 5+ years
- Include different market conditions (bull, bear, sideways)

### 2. **Avoid Overfitting**
- Don't optimize too many parameters
- Use walk-forward analysis
- Test on out-of-sample data
- Keep strategies simple

### 3. **Include Transaction Costs**
```python
backtester = Backtester(
    df,
    symbol='AAPL',
    initial_capital=10000,
    commission=1.0,     # $1 per trade
    slippage=0.001      # 0.1% slippage
)
```

### 4. **Validate Results**
- Compare to buy & hold
- Test on multiple symbols
- Check win rate vs profit factor balance
- Review individual trades

### 5. **Risk Management**
- Set max drawdown limits
- Use stop losses
- Position sizing rules
- Don't risk more than 2% per trade

### 6. **Walk-Forward Testing**
```python
# Train on 2020-2022, test on 2023-2024
train_df = df['2020':'2022']
test_df = df['2023':'2024']

# Optimize on train data
# Test final strategy on test data
```

### 7. **Compare Strategies**
```python
# Run multiple strategies on same data
strategies = [
    ('RSI', rsi_strategy),
    ('MACD', macd_crossover_strategy),
    ('MA Cross', moving_average_crossover_strategy)
]

for name, strategy in strategies:
    results = backtester.run_strategy(strategy, name)
    print(f"{name}: {results.total_return_pct:.2f}%")
```

---

## Common Pitfalls

### ❌ **Don't Do This:**

1. **Cherry-picking**: Only testing on favorable periods
2. **Curve-fitting**: Over-optimizing to historical data
3. **Ignoring costs**: Not including commissions/slippage
4. **Unrealistic fills**: Assuming perfect entry/exit prices
5. **Look-ahead bias**: Using future data in signals
6. **Survivorship bias**: Only testing on existing symbols

### ✅ **Do This Instead:**

1. Test across multiple time periods
2. Keep strategies simple with few parameters
3. Include realistic transaction costs
4. Use conservative fill assumptions
5. Ensure indicators use only past data
6. Test on delisted/failed companies too

---

## Example Results

### TQQQ RSI Strategy (2010-2025)

```
Initial Capital:    $10,000
Final Capital:      $320,333
Total Return:       +3,103%
Win Rate:           93.75%
Profit Factor:      3.68
Max Drawdown:       49.88%
Trades:             16
```

**Analysis:**
- ✅ Excellent return
- ✅ Very high win rate
- ⚠️  High drawdown (nearly 50%)
- ⚠️  Only 16 trades (limited sample)
- ⚠️  TQQQ is 3x leveraged (high risk)

**Takeaway:** Great backtest, but high risk. Consider:
- Testing on non-leveraged ETFs
- Adding risk management (stops)
- More robust exit strategy

---

## Quick Commands

```bash
# Quick backtest
python examples/quick_backtest.py

# Full demo (8 examples)
python examples/backtest_demo.py

# Custom backtest
python -c "from examples.quick_backtest import *; main()"
```

---

## Resources

- **Original Turtle Trading Rules**: http://www.originalturtles.org/
- **Quantitative Trading**: Ernie Chan's books
- **Walk-Forward Analysis**: https://www.investopedia.com/articles/trading/11/walk-forward-optimization.asp
- **Backtesting Best Practices**: https://www.quantstart.com/

---

## Next Steps

1. ✅ Run `python examples/quick_backtest.py`
2. ✅ Try different pre-built strategies
3. ✅ Create your own custom strategy
4. ✅ Optimize parameters
5. ✅ Compare to buy & hold
6. ✅ Test on multiple symbols
7. ✅ Add risk management rules
8. ✅ Paper trade before going live!

**Happy Backtesting! 📈**
