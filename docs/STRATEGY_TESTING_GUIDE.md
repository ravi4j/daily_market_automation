# 🧪 Strategy Testing Guide

## Overview

This guide shows you how to systematically test all 35+ indicator-based strategies to find the best ones for your portfolio.

## Quick Start

### Test All Strategies on AAPL

```bash
python examples/test_all_strategies.py --symbol AAPL
```

This will:
1. Load historical data for AAPL
2. Calculate all 50+ technical indicators
3. Test all 35+ strategies
4. Rank them by performance
5. Show you the top 20

### Test on Your Symbols

```bash
# Test on TQQQ
python examples/test_all_strategies.py --symbol TQQQ

# Test on SP500
python examples/test_all_strategies.py --symbol SP500

# Test on multiple symbols
for symbol in TQQQ AAPL UBER SP500; do
    python examples/test_all_strategies.py --symbol $symbol --export results_$symbol.csv
done
```

## Advanced Usage

### Filter by Category

Test only specific types of strategies:

```bash
# Test only momentum strategies
python examples/test_all_strategies.py --category momentum

# Test only trend strategies
python examples/test_all_strategies.py --category trend

# Test only volatility strategies
python examples/test_all_strategies.py --category volatility

# Test only volume strategies
python examples/test_all_strategies.py --category volume

# Test only combination strategies
python examples/test_all_strategies.py --category combination
```

### Adjust Parameters

```bash
# Use different initial capital
python examples/test_all_strategies.py --capital 50000

# Require minimum 10 trades
python examples/test_all_strategies.py --min-trades 10

# Show top 10 strategies only
python examples/test_all_strategies.py --top 10

# Export results to CSV
python examples/test_all_strategies.py --export strategy_results.csv
```

### Combined Example

```bash
python examples/test_all_strategies.py \
    --symbol TQQQ \
    --category momentum \
    --capital 50000 \
    --min-trades 10 \
    --top 15 \
    --export tqqq_momentum_strategies.csv
```

## Understanding the Results

### Performance Metrics

Each strategy is evaluated on:

- **Total Return %**: Overall profit/loss percentage
- **Sharpe Ratio**: Risk-adjusted returns (higher is better)
- **Max Drawdown**: Worst peak-to-trough decline
- **Win Rate**: Percentage of profitable trades
- **Number of Trades**: How often the strategy trades
- **Avg Profit per Trade**: Average gain/loss per trade
- **Profit Factor**: Total gains ÷ total losses (>1 is profitable)
- **Final Capital**: Ending portfolio value

### Interpreting Results

**🏆 Best Overall Strategy**
- Highest total return
- Good for maximizing gains
- May have higher risk

**📈 Best Risk-Adjusted Strategy**
- Highest Sharpe ratio
- Balance between returns and risk
- More stable performance

**🎯 Most Consistent Strategy**
- Highest win rate (>60%)
- Fewer losing trades
- More predictable results

## Strategy Categories

### 1. Momentum Strategies (10 strategies)

Focus on price momentum and oscillators:
- RSI Oversold Bounce
- RSI Momentum
- RSI Extreme
- Stochastic Crossover
- MACD Crossover
- MACD Histogram
- MACD Zero Cross
- CCI Reversal
- Williams %R
- ROC Momentum

**Best for**: Short-term trades, volatile markets

### 2. Trend Strategies (9 strategies)

Follow the prevailing trend:
- SMA Golden Cross
- EMA Fast Cross
- SMA Triple Cross
- Price Above SMA
- ADX Strong Trend
- ADX Trend Start
- Aroon Crossover
- Supertrend Follow

**Best for**: Long-term holds, trending markets

### 3. Volatility Strategies (6 strategies)

Trade on price volatility:
- BB Bounce
- BB Squeeze Breakout
- BB Width Expansion
- Keltner Breakout
- ATR Volatility Breakout

**Best for**: Breakout trading, range-bound markets

### 4. Volume Strategies (3 strategies)

Use volume confirmation:
- OBV Trend
- Volume Surge
- MFI Flow

**Best for**: Confirming price moves

### 5. Combination Strategies (3 strategies)

Multi-indicator confirmation:
- Trend Momentum Combo
- MA MACD Combo
- BB RSI Combo

**Best for**: Higher confidence signals, reducing false positives

## Sample Output

```
🥇 MACD_Histogram (momentum)
   Description: Buy when histogram turns positive and growing
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   💰 Total Return: +347.85%
   📊 Sharpe Ratio: 1.82
   📉 Max Drawdown: -22.45%
   🎯 Win Rate: 58.3%
   🔄 Number of Trades: 48
   💵 Avg Profit per Trade: +7.25%
   ⚖️  Profit Factor: 2.15
   💎 Final Capital: $44,785.00

🥈 ADX_Strong_Trend (trend)
   Description: Buy when ADX > 25 and +DI > -DI (strong uptrend)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   💰 Total Return: +298.42%
   📊 Sharpe Ratio: 1.65
   📉 Max Drawdown: -18.23%
   🎯 Win Rate: 62.5%
   🔄 Number of Trades: 32
   💵 Avg Profit per Trade: +9.33%
   ⚖️  Profit Factor: 2.45
   💎 Final Capital: $39,842.00
```

## Finding Your Best Strategy

### Step 1: Test on Your Symbol

```bash
python examples/test_all_strategies.py --symbol YOUR_SYMBOL --export results.csv
```

### Step 2: Review Top Performers

Look at the top 5-10 strategies. Consider:
- Do they fit your trading style? (day trading vs holding)
- Can you handle the drawdowns?
- Is the win rate acceptable?
- Are there enough trades to be statistically significant?

### Step 3: Test on Multiple Timeframes

Different symbols may favor different strategies:

```bash
# Test on different asset types
python examples/test_all_strategies.py --symbol AAPL   # Stock
python examples/test_all_strategies.py --symbol TQQQ   # Leveraged ETF
python examples/test_all_strategies.py --symbol SP500  # Index
```

### Step 4: Implement Top Strategies

Add your top 2-3 strategies to `src/strategy_runner.py`:

```python
def your_new_strategy(self, row_idx: int) -> Optional[TradingAlert]:
    """Implement your top-performing strategy"""
    # Copy logic from strategy_generator.py
    # Add to daily alerts
    pass
```

## Tips for Best Results

### ✅ Do's

1. **Test on sufficient data**: Use at least 2-3 years of history
2. **Consider multiple metrics**: Don't just look at total return
3. **Account for fees**: Real trading has costs
4. **Validate on multiple symbols**: A good strategy works across assets
5. **Check recent performance**: Look at last 6 months separately

### ❌ Don'ts

1. **Don't overfit**: Avoid strategies that only work on one symbol
2. **Don't ignore drawdowns**: 500% return with 80% drawdown is risky
3. **Don't skip win rate**: Low win rates need large gains to compensate
4. **Don't use strategies with <20 trades**: Not statistically significant
5. **Don't ignore market conditions**: Bull market strategies may fail in bears

## Next Steps

After finding your best strategies:

1. **Add to daily automation**: Integrate into `src/strategy_runner.py`
2. **Set up alerts**: Configure Telegram notifications
3. **Monitor performance**: Track actual vs backtest results
4. **Adjust parameters**: Fine-tune thresholds based on live data
5. **Combine strategies**: Use multiple strategies for confirmation

## Troubleshooting

**No strategies have enough trades?**
```bash
python examples/test_all_strategies.py --min-trades 3
```

**Want to see all strategies, not just top 20?**
```bash
python examples/test_all_strategies.py --top 100
```

**Need help understanding a specific strategy?**
- Check `src/strategy_generator.py` for implementation details
- Each strategy has a description and parameter list

## Further Reading

- [Backtesting Guide](backtesting-guide.md) - Deep dive into backtesting
- [Indicators Guide](indicators-guide.md) - All available indicators
- [Daily Alerts Guide](daily-alerts-guide.md) - Setting up automation

