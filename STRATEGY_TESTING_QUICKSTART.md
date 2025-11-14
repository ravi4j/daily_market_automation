# 🚀 Strategy Testing Quick Start

## Test All 35+ Strategies in One Command

```bash
python examples/test_all_strategies.py --symbol AAPL
```

## What This Does

✅ Tests **35+ pre-built strategies** based on all major indicators  
✅ Ranks them by performance (return, Sharpe ratio, win rate)  
✅ Shows you which ones work best for your symbol  
✅ Tells you which strategies to follow  

## Quick Examples

```bash
# Test on TQQQ
python examples/test_all_strategies.py --symbol TQQQ

# Test only momentum strategies
python examples/test_all_strategies.py --category momentum

# Export results to CSV
python examples/test_all_strategies.py --export results.csv

# Show top 10 only
python examples/test_all_strategies.py --top 10
```

## 35+ Strategies Included

### Momentum (10)
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

### Trend (9)
- SMA Golden Cross (50/200)
- EMA Fast Cross (12/26)
- SMA Triple Cross (20/50/200)
- Price Above SMA
- ADX Strong Trend
- ADX Trend Start
- Aroon Crossover
- Supertrend Follow

### Volatility (6)
- Bollinger Band Bounce
- BB Squeeze Breakout
- BB Width Expansion
- Keltner Breakout
- ATR Volatility Breakout

### Volume (3)
- OBV Trend
- Volume Surge
- MFI Flow

### Combination (3)
- Trend + Momentum
- MA + MACD
- BB + RSI

## Understanding Results

### Key Metrics

| Metric | What It Means | Good Value |
|--------|---------------|------------|
| Total Return | Overall profit/loss | >100% |
| Sharpe Ratio | Risk-adjusted return | >1.5 |
| Max Drawdown | Worst decline | <30% |
| Win Rate | % profitable trades | >55% |
| Profit Factor | Gains ÷ Losses | >1.5 |

### Sample Output

```
🥇 MACD_Histogram
   💰 Total Return: +347.85%
   📊 Sharpe Ratio: 1.82
   📉 Max Drawdown: -22.45%
   🎯 Win Rate: 58.3%
   🔄 Trades: 48
```

## All Command Options

```bash
python examples/test_all_strategies.py \
    --symbol TQQQ              # Symbol to test
    --capital 50000            # Starting capital
    --min-trades 10            # Min trades required
    --category momentum        # Filter by category
    --top 15                   # Show top N
    --export results.csv       # Save to CSV
```

## What To Do Next

1. **Run the test** on your symbols
2. **Review top 5-10** strategies
3. **Pick 2-3 that fit** your style
4. **Add to daily automation** in `src/strategy_runner.py`
5. **Get daily alerts** via Telegram

## Pro Tips

✅ Test on multiple symbols (stocks, ETFs, indices)  
✅ Look at Sharpe ratio, not just returns  
✅ Require at least 20 trades for significance  
✅ Consider your risk tolerance (drawdowns)  
✅ Combine multiple strategies for confirmation  

## Full Documentation

📖 [Complete Strategy Testing Guide](docs/STRATEGY_TESTING_GUIDE.md)

---

**Ready to find your winning strategies? Run the test now!** 🚀

