#!/usr/bin/env python3
"""
Backtest All 4 Daily Alert Strategies
Tests the strategies used in strategy_runner.py with historical data
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Optional
from indicators import TechnicalIndicators
from backtester import Backtester


# ==================== STRATEGY IMPLEMENTATIONS ====================

def get_value(row, key):
    """Helper to get value with case-insensitive column names"""
    if key in row.index:
        return row[key]
    key_lower = key.lower()
    if key_lower in row.index:
        return row[key_lower]
    key_upper = key.upper()
    if key_upper in row.index:
        return row[key_upper]
    # Try Close/CLOSE for close
    if key_lower == 'close' and 'Close' in row.index:
        return row['Close']
    return None


def rsi_macd_strategy(row: pd.Series, position: Optional[str]) -> str:
    """RSI + MACD Confluence Strategy"""
    rsi = get_value(row, 'RSI_14')
    macd = get_value(row, 'MACD_12_26_9')
    macd_signal = get_value(row, 'MACDs_12_26_9')
    adx = get_value(row, 'ADX_14') or 0
    
    if rsi is None or macd is None or macd_signal is None:
        return 'HOLD'
    
    # BUY: RSI oversold + MACD bullish + strong trend
    if position is None and rsi < 35 and macd > macd_signal and adx > 20:
        return 'BUY'
    
    # SELL: RSI overbought + MACD bearish
    elif position == 'LONG' and rsi > 65 and macd < macd_signal:
        return 'SELL'
    
    return 'HOLD'


def trend_following_strategy(row: pd.Series, position: Optional[str]) -> str:
    """Trend Following Strategy (SMA alignment)"""
    price = get_value(row, 'close')
    sma20 = get_value(row, 'SMA_20')
    sma50 = get_value(row, 'SMA_50')
    sma200 = get_value(row, 'SMA_200')
    rsi = get_value(row, 'RSI_14') or 50
    adx = get_value(row, 'ADX_14') or 0
    
    if price is None or sma20 is None or sma50 is None or sma200 is None:
        return 'HOLD'
    
    # BUY: Strong uptrend (all SMAs aligned)
    if (position is None and 
        price > sma20 > sma50 > sma200 and 
        40 < rsi < 70 and 
        adx > 25):
        return 'BUY'
    
    # SELL: Trend broken or momentum lost
    elif position == 'LONG' and (price < sma20 or rsi < 35):
        return 'SELL'
    
    return 'HOLD'


def mean_reversion_strategy(row: pd.Series, position: Optional[str]) -> str:
    """Bollinger Band Mean Reversion Strategy"""
    # Find BB columns dynamically
    bb_lower = None
    bb_upper = None
    
    for col in row.index:
        if 'BBL' in col or 'bbl' in col:
            bb_lower = col
        elif 'BBU' in col or 'bbu' in col:
            bb_upper = col
    
    if bb_lower is None or bb_upper is None:
        return 'HOLD'
    
    price = get_value(row, 'close')
    if price is None:
        return 'HOLD'
        
    lower = row[bb_lower]
    upper = row[bb_upper]
    rsi = get_value(row, 'RSI_14') or 50
    
    # BUY: Price at lower band + oversold
    if position is None and price <= lower * 1.01 and rsi < 40:
        return 'BUY'
    
    # SELL: Price at upper band + overbought
    elif position == 'LONG' and price >= upper * 0.99 and rsi > 60:
        return 'SELL'
    
    return 'HOLD'


def momentum_breakout_strategy(row: pd.Series, position: Optional[str]) -> str:
    """Momentum Breakout Strategy"""
    price = get_value(row, 'close')
    high_20 = get_value(row, 'high_20d')
    low_20 = get_value(row, 'low_20d')
    adx = get_value(row, 'ADX_14') or 0
    rsi = get_value(row, 'RSI_14') or 50
    volume_ratio = get_value(row, 'volume_ratio') or 1.0
    
    if price is None or high_20 is None or low_20 is None:
        return 'HOLD'
    
    # BUY: Breakout above 20-day high with volume
    if position is None and price > high_20 and volume_ratio > 1.5 and adx > 25:
        return 'BUY'
    
    # SELL: Breakdown below 20-day low or oversold
    elif position == 'LONG' and (price < low_20 or rsi < 30):
        return 'SELL'
    
    return 'HOLD'


# ==================== HELPER FUNCTIONS ====================

def add_momentum_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Add indicators needed for momentum breakout strategy"""
    # Handle case-insensitive column names
    high_col = 'high' if 'high' in df.columns else 'High'
    low_col = 'low' if 'low' in df.columns else 'Low'
    vol_col = 'volume' if 'volume' in df.columns else 'Volume'
    
    # 20-day high/low
    df['high_20d'] = df[high_col].rolling(window=20).max().shift(1)
    df['low_20d'] = df[low_col].rolling(window=20).min().shift(1)
    
    # Volume ratio
    df['volume_ratio'] = df[vol_col] / df[vol_col].rolling(window=20).mean()
    
    return df


def prepare_data_for_strategy(df: pd.DataFrame, strategy_name: str) -> pd.DataFrame:
    """Add required indicators for a specific strategy"""
    indicators = TechnicalIndicators(df)
    
    if strategy_name == 'rsi_macd':
        indicators.add_rsi(14)
        indicators.add_macd()
        indicators.add_adx()
    
    elif strategy_name == 'trend_following':
        indicators.add_sma([20, 50, 200])
        indicators.add_rsi(14)
        indicators.add_adx()
    
    elif strategy_name == 'mean_reversion':
        indicators.add_bbands(length=20, std=2.0)
        indicators.add_rsi(14)
    
    elif strategy_name == 'momentum_breakout':
        indicators.add_adx()
        indicators.add_rsi(14)
        df_with_ind = indicators.df
        df_with_ind = add_momentum_indicators(df_with_ind)
        return df_with_ind.dropna()
    
    return indicators.df.dropna()


# ==================== MAIN BACKTEST RUNNER ====================

def backtest_all_strategies(symbol: str, initial_capital: float = 10000):
    """
    Backtest all 4 strategies on a symbol and compare results
    """
    print("\n" + "="*80)
    print(f"📊 BACKTESTING ALL STRATEGIES ON {symbol}")
    print("="*80)
    
    # Load data and ensure ascending date order
    df = pd.read_csv(f'data/{symbol}.csv', index_col='Date', parse_dates=True)
    df = df.sort_index()  # CRITICAL: Ensure chronological order!
    print(f"\n📅 Data Range: {df.index.min().strftime('%Y-%m-%d')} to {df.index.max().strftime('%Y-%m-%d')}")
    print(f"📊 Total Days: {len(df)}")
    
    strategies = {
        'RSI+MACD': ('rsi_macd', rsi_macd_strategy),
        'Trend Following': ('trend_following', trend_following_strategy),
        'Mean Reversion': ('mean_reversion', mean_reversion_strategy),
        'Momentum Breakout': ('momentum_breakout', momentum_breakout_strategy)
    }
    
    results = []
    
    for strategy_name, (data_prep_name, strategy_func) in strategies.items():
        print(f"\n{'─'*80}")
        print(f"🔍 Testing: {strategy_name}")
        print(f"{'─'*80}")
        
        # Prepare data with required indicators
        df_prepared = prepare_data_for_strategy(df.copy(), data_prep_name)
        
        if len(df_prepared) < 250:
            print(f"⚠️  Insufficient data after adding indicators ({len(df_prepared)} bars)")
            continue
        
        # Run backtest
        backtester = Backtester(
            df=df_prepared,
            symbol=symbol,
            initial_capital=initial_capital
        )
        result = backtester.run_strategy(
            strategy_func=strategy_func,
            strategy_name=strategy_name
        )
        
        # Store results
        if result and result.num_trades > 0:
            results.append({
                'strategy': strategy_name,
                'return_pct': result.total_return_pct,
                'win_rate': result.win_rate,
                'profit_factor': result.profit_factor,
                'max_drawdown': result.max_drawdown,
                'total_trades': result.num_trades,
                'final_capital': result.final_capital
            })
        else:
            print(f"⚠️  No trades generated for {strategy_name}")
    
    # Print comparison table
    print("\n" + "="*80)
    print("📊 STRATEGY COMPARISON TABLE")
    print("="*80)
    
    if results:
        df_results = pd.DataFrame(results)
        df_results = df_results.sort_values('return_pct', ascending=False)
        
        print(f"\n{'Strategy':<20} {'Return%':<12} {'Win Rate%':<12} {'PF':<8} {'Drawdown%':<12} {'Trades':<8}")
        print("─" * 80)
        
        for _, row in df_results.iterrows():
            pf_str = f"{row['profit_factor']:.2f}" if row['profit_factor'] < 999 else "∞"
            
            # Color coding for return
            if row['return_pct'] > 50:
                emoji = "🟢"
            elif row['return_pct'] > 0:
                emoji = "🟡"
            else:
                emoji = "🔴"
            
            print(f"{emoji} {row['strategy']:<18} {row['return_pct']:>10.2f}% {row['win_rate']:>10.2f}% "
                  f"{pf_str:>6} {row['max_drawdown']:>10.2f}% {row['total_trades']:>6}")
        
        print("\n" + "="*80)
        
        # Best strategy
        best = df_results.iloc[0]
        print(f"🏆 BEST STRATEGY: {best['strategy']}")
        print(f"   Return: {best['return_pct']:.2f}%")
        print(f"   Win Rate: {best['win_rate']:.2f}%")
        print(f"   Profit Factor: {best['profit_factor']:.2f}")
        print("="*80)
    else:
        print("\n⚠️  No valid backtest results generated")
        print("   This might mean insufficient data or no trades generated")


def backtest_multiple_symbols(symbols: list, initial_capital: float = 10000):
    """
    Backtest all strategies on multiple symbols
    """
    print("\n" + "="*80)
    print("🔍 MULTI-SYMBOL STRATEGY BACKTEST")
    print("="*80)
    print(f"Symbols: {', '.join(symbols)}")
    print(f"Initial Capital: ${initial_capital:,.2f} per symbol")
    
    all_results = []
    
    for symbol in symbols:
        try:
            print(f"\n\n{'█'*80}")
            print(f"{'█'*80}")
            print(f"  TESTING {symbol}")
            print(f"{'█'*80}")
            print(f"{'█'*80}")
            
            backtest_all_strategies(symbol, initial_capital)
            
        except Exception as e:
            print(f"\n❌ Error testing {symbol}: {e}")
            continue
    
    print("\n\n" + "="*80)
    print("✅ MULTI-SYMBOL BACKTEST COMPLETE!")
    print("="*80)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Backtest trading strategies')
    parser.add_argument('--symbol', default='TQQQ', help='Symbol to test (default: TQQQ)')
    parser.add_argument('--all', action='store_true', help='Test all symbols in data/ folder')
    parser.add_argument('--capital', type=float, default=10000, help='Initial capital (default: 10000)')
    
    args = parser.parse_args()
    
    if args.all:
        # Test all CSV files in data folder
        data_dir = Path('data')
        symbols = [f.stem for f in data_dir.glob('*.csv')]
        backtest_multiple_symbols(symbols, args.capital)
    else:
        backtest_all_strategies(args.symbol, args.capital)

