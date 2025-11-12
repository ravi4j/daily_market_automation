#!/usr/bin/env python3
"""
Quick Backtest Example
Fast demo of backtesting a strategy
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import pandas as pd
from indicators import TechnicalIndicators
from backtester import Backtester, rsi_strategy


def main():
    print("🚀 Quick Backtest Demo\n")
    
    # 1. Load data
    df = pd.read_csv('data/TQQQ.csv', index_col='Date', parse_dates=True)
    df = df.sort_index()
    print(f"✅ Loaded {len(df)} days of TQQQ data")
    
    # 2. Add RSI indicator
    indicators = TechnicalIndicators(df)
    indicators.add_rsi(14)
    df_with_indicators = indicators.df
    print(f"✅ Added RSI indicator")
    
    # 3. Run backtest
    backtester = Backtester(
        df_with_indicators,
        symbol='TQQQ',
        initial_capital=10000
    )
    
    results = backtester.run_strategy(
        rsi_strategy,
        strategy_name="RSI Strategy"
    )
    
    # 4. Show key results
    print(f"\n🎯 Quick Summary:")
    print(f"   Return: {results.total_return_pct:.2f}%")
    print(f"   Win Rate: {results.win_rate:.2f}%")
    print(f"   Trades: {results.num_trades}")
    print(f"   Profit Factor: {results.profit_factor:.2f}")
    
    print(f"\n✅ Done! See examples/backtest_demo.py for more examples")


if __name__ == "__main__":
    main()

