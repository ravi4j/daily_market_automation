#!/usr/bin/env python3
"""
Test All Strategies - Systematically test every indicator-based strategy

This script:
1. Loads historical data
2. Calculates all indicators
3. Tests all generated strategies
4. Ranks them by performance
5. Shows you the best ones to follow
"""

import sys
import os
from pathlib import Path
import pandas as pd
import argparse
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from indicators import TechnicalIndicators
from backtester import Backtester
from strategy_generator import StrategyGenerator


def load_and_prepare_data(symbol: str, data_dir: str = "data") -> pd.DataFrame:
    """Load data and add all indicators"""
    csv_path = Path(data_dir) / f"{symbol}.csv"
    
    if not csv_path.exists():
        raise FileNotFoundError(f"Data file not found: {csv_path}")
    
    print(f"📊 Loading data from {csv_path}...")
    df = pd.read_csv(csv_path, parse_dates=['Date']).set_index('Date')
    df = df.sort_index()  # Ensure ascending order
    
    # Ensure case-insensitive column access
    df.columns = df.columns.str.title()
    
    print(f"✅ Loaded {len(df)} rows of data ({df.index[0].date()} to {df.index[-1].date()})")
    
    # Add all technical indicators
    print("📈 Calculating all technical indicators...")
    ta = TechnicalIndicators(df)
    
    # Add everything
    df = ta.add_all_indicators()
    
    print(f"✅ Added indicators. DataFrame now has {len(df.columns)} columns")
    
    return df


def test_strategy(strategy, df: pd.DataFrame, symbol: str, 
                 initial_capital: float = 10000) -> dict:
    """Test a single strategy and return results"""
    try:
        # Generate signals
        generator = StrategyGenerator()
        signals = generator.generate_signal(strategy, df)
        
        # Skip if no signals generated
        if signals.sum() == 0:
            return None
        
        # Create a strategy function for backtester
        # The backtester expects: func(row, position) -> 'BUY', 'SELL', or 'HOLD'
        def strategy_func(row, position):
            # Get the signal for this row
            idx = df.index.get_loc(row.name)
            signal_val = signals.iloc[idx]
            
            if signal_val == 1 and position is None:
                return 'BUY'
            elif signal_val == -1 and position is not None:
                return 'SELL'
            else:
                return 'HOLD'
        
        # Run backtest
        backtester = Backtester(df=df, symbol=symbol, initial_capital=initial_capital)
        results = backtester.run_strategy(strategy_func, strategy.name)
        
        if results is None or len(results.trades) == 0:
            return None
        
        # Calculate avg profit percentage
        closed_trades = [t for t in results.trades if not t.is_open]
        avg_profit_pct = sum([t.profit_loss_pct for t in closed_trades]) / len(closed_trades) if closed_trades else 0.0
        
        return {
            'name': strategy.name,
            'category': strategy.category,
            'description': strategy.description,
            'total_return_pct': results.total_return_pct,
            'sharpe_ratio': results.sharpe_ratio,
            'max_drawdown_pct': results.max_drawdown,
            'win_rate': results.win_rate,
            'num_trades': len(results.trades),
            'avg_profit': avg_profit_pct,
            'profit_factor': results.profit_factor,
            'final_capital': results.final_capital
        }
    except Exception as e:
        print(f"  ⚠️  Error testing {strategy.name}: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(description='Test all indicator strategies')
    parser.add_argument('--symbol', default='AAPL', help='Symbol to test (default: AAPL)')
    parser.add_argument('--capital', type=float, default=10000, help='Initial capital (default: 10000)')
    parser.add_argument('--min-trades', type=int, default=5, help='Minimum number of trades (default: 5)')
    parser.add_argument('--category', help='Filter by category (momentum, trend, volatility, volume, combination)')
    parser.add_argument('--top', type=int, default=20, help='Show top N strategies (default: 20)')
    parser.add_argument('--export', help='Export results to CSV file')
    
    args = parser.parse_args()
    
    print("=" * 80)
    print("🚀 STRATEGY PERFORMANCE TESTING")
    print("=" * 80)
    print(f"\n📊 Symbol: {args.symbol}")
    print(f"💰 Initial Capital: ${args.capital:,.2f}")
    print(f"🎯 Minimum Trades: {args.min_trades}")
    if args.category:
        print(f"📂 Category Filter: {args.category}")
    print()
    
    # Load data and add indicators
    try:
        df = load_and_prepare_data(args.symbol)
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        return 1
    
    # Generate all strategies
    generator = StrategyGenerator()
    all_strategies = generator.get_all_strategies()
    
    if args.category:
        all_strategies = generator.get_strategies_by_category(args.category)
    
    print(f"\n🧪 Testing {len(all_strategies)} strategies...")
    print("=" * 80)
    
    # Test each strategy
    results = []
    for i, strategy in enumerate(all_strategies, 1):
        print(f"\n[{i}/{len(all_strategies)}] Testing: {strategy.name}")
        print(f"    Category: {strategy.category}")
        print(f"    Description: {strategy.description}")
        
        result = test_strategy(strategy, df, args.symbol, args.capital)
        
        if result and result['num_trades'] >= args.min_trades:
            results.append(result)
            print(f"    ✅ Return: {result['total_return_pct']:+.2f}% | "
                  f"Trades: {result['num_trades']} | "
                  f"Win Rate: {result['win_rate']:.1f}%")
        elif result:
            print(f"    ⏭️  Skipped (only {result['num_trades']} trades)")
        else:
            print(f"    ❌ No valid results")
    
    if not results:
        print("\n⚠️  No strategies generated enough trades to evaluate.")
        print(f"    Try lowering --min-trades (current: {args.min_trades})")
        return 1
    
    # Convert to DataFrame and sort by return
    df_results = pd.DataFrame(results)
    df_results = df_results.sort_values('total_return_pct', ascending=False)
    
    # Display top performers
    print("\n" + "=" * 80)
    print(f"📊 TOP {min(args.top, len(df_results))} STRATEGIES BY TOTAL RETURN")
    print("=" * 80)
    
    top_strategies = df_results.head(args.top)
    
    for i, row in enumerate(top_strategies.itertuples(), 1):
        emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
        
        print(f"\n{emoji} {row.name}")
        print(f"   Category: {row.category}")
        print(f"   Description: {row.description}")
        print(f"   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"   💰 Total Return: {row.total_return_pct:+.2f}%")
        print(f"   📊 Sharpe Ratio: {row.sharpe_ratio:.2f}")
        print(f"   📉 Max Drawdown: {row.max_drawdown_pct:.2f}%")
        print(f"   🎯 Win Rate: {row.win_rate:.1f}%")
        print(f"   🔄 Number of Trades: {row.num_trades}")
        print(f"   💵 Avg Profit per Trade: {row.avg_profit:+.2f}%")
        print(f"   ⚖️  Profit Factor: {row.profit_factor:.2f}")
        print(f"   💎 Final Capital: ${row.final_capital:,.2f}")
    
    # Summary by category
    print("\n" + "=" * 80)
    print("📂 AVERAGE PERFORMANCE BY CATEGORY")
    print("=" * 80)
    
    category_stats = df_results.groupby('category').agg({
        'total_return_pct': ['mean', 'median', 'max'],
        'win_rate': 'mean',
        'num_trades': 'sum',
        'name': 'count'
    }).round(2)
    
    for category in category_stats.index:
        stats = category_stats.loc[category]
        print(f"\n📁 {category.upper()}")
        print(f"   Strategies Tested: {int(stats[('name', 'count')])}")
        print(f"   Avg Return: {stats[('total_return_pct', 'mean')]:+.2f}%")
        print(f"   Median Return: {stats[('total_return_pct', 'median')]:+.2f}%")
        print(f"   Best Return: {stats[('total_return_pct', 'max')]:+.2f}%")
        print(f"   Avg Win Rate: {stats[('win_rate', 'mean')]:.1f}%")
        print(f"   Total Trades: {int(stats[('num_trades', 'sum')])}")
    
    # Recommendations
    print("\n" + "=" * 80)
    print("💡 RECOMMENDATIONS")
    print("=" * 80)
    
    # Best overall
    best = df_results.iloc[0]
    print(f"\n🏆 BEST OVERALL STRATEGY:")
    print(f"   {best['name']} ({best['category']})")
    print(f"   Return: {best['total_return_pct']:+.2f}% | Sharpe: {best['sharpe_ratio']:.2f}")
    
    # Best by Sharpe (risk-adjusted)
    best_sharpe = df_results.nlargest(1, 'sharpe_ratio').iloc[0]
    if best_sharpe['name'] != best['name']:
        print(f"\n📈 BEST RISK-ADJUSTED STRATEGY:")
        print(f"   {best_sharpe['name']} ({best_sharpe['category']})")
        print(f"   Sharpe: {best_sharpe['sharpe_ratio']:.2f} | Return: {best_sharpe['total_return_pct']:+.2f}%")
    
    # Highest win rate
    best_wr = df_results.nlargest(1, 'win_rate').iloc[0]
    if best_wr['win_rate'] > 60:
        print(f"\n🎯 MOST CONSISTENT STRATEGY:")
        print(f"   {best_wr['name']} ({best_wr['category']})")
        print(f"   Win Rate: {best_wr['win_rate']:.1f}% | Return: {best_wr['total_return_pct']:+.2f}%")
    
    # Best by category
    print(f"\n🏅 BEST STRATEGY PER CATEGORY:")
    for category in df_results['category'].unique():
        cat_best = df_results[df_results['category'] == category].iloc[0]
        print(f"   {category.title()}: {cat_best['name']} ({cat_best['total_return_pct']:+.2f}%)")
    
    # Export results
    if args.export:
        export_path = Path(args.export)
        df_results.to_csv(export_path, index=False)
        print(f"\n💾 Results exported to: {export_path}")
    
    print("\n" + "=" * 80)
    print("✅ TESTING COMPLETE!")
    print("=" * 80)
    print(f"\n📊 Tested {len(results)} strategies on {args.symbol}")
    print(f"📅 Data period: {df.index[0].date()} to {df.index[-1].date()}")
    print(f"⏰ Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

