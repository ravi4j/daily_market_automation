#!/usr/bin/env python3
"""
Backtesting Demo
Shows how to test trading strategies with historical data
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import pandas as pd
from indicators import TechnicalIndicators
from backtester import (
    Backtester,
    rsi_strategy,
    macd_crossover_strategy,
    moving_average_crossover_strategy,
    bollinger_bounce_strategy,
    multi_indicator_strategy,
    optimize_rsi_parameters
)


def load_data(symbol: str = 'TQQQ') -> pd.DataFrame:
    """Load and prepare data"""
    data_path = Path(__file__).parent.parent / 'data' / f'{symbol}.csv'
    df = pd.read_csv(data_path, index_col='Date', parse_dates=True)
    df = df.sort_index()
    return df


def demo_1_simple_rsi_strategy():
    """Demo 1: Simple RSI Strategy"""
    print("\n" + "="*80)
    print("DEMO 1: Simple RSI Strategy")
    print("="*80)
    print("Strategy: Buy when RSI < 30, Sell when RSI > 70")
    
    # Load data
    df = load_data('TQQQ')
    
    # Add RSI indicator
    indicators = TechnicalIndicators(df)
    indicators.add_rsi(14)
    df_with_indicators = indicators.df
    
    # Run backtest
    backtester = Backtester(
        df_with_indicators,
        symbol='TQQQ',
        initial_capital=10000
    )
    
    results = backtester.run_strategy(
        rsi_strategy,
        strategy_name="RSI Oversold/Overbought"
    )
    
    return results


def demo_2_macd_strategy():
    """Demo 2: MACD Crossover Strategy"""
    print("\n" + "="*80)
    print("DEMO 2: MACD Crossover Strategy")
    print("="*80)
    print("Strategy: Buy on MACD bullish cross, Sell on bearish cross")
    
    # Load data
    df = load_data('AAPL')
    
    # Add MACD indicator
    indicators = TechnicalIndicators(df)
    indicators.add_macd()
    df_with_indicators = indicators.df
    
    # Run backtest
    backtester = Backtester(
        df_with_indicators,
        symbol='AAPL',
        initial_capital=10000
    )
    
    results = backtester.run_strategy(
        macd_crossover_strategy,
        strategy_name="MACD Crossover"
    )
    
    return results


def demo_3_moving_average_strategy():
    """Demo 3: Moving Average Crossover"""
    print("\n" + "="*80)
    print("DEMO 3: Moving Average Crossover")
    print("="*80)
    print("Strategy: Buy when SMA20 > SMA50, Sell when SMA20 < SMA50")
    
    # Load data
    df = load_data('SP500')
    
    # Add moving averages
    indicators = TechnicalIndicators(df)
    indicators.add_sma(20)
    indicators.add_sma(50)
    df_with_indicators = indicators.df
    
    # Run backtest
    backtester = Backtester(
        df_with_indicators,
        symbol='SP500',
        initial_capital=10000
    )
    
    results = backtester.run_strategy(
        moving_average_crossover_strategy,
        strategy_name="SMA 20/50 Crossover"
    )
    
    return results


def demo_4_custom_strategy():
    """Demo 4: Custom Strategy"""
    print("\n" + "="*80)
    print("DEMO 4: Custom Strategy")
    print("="*80)
    print("Strategy: Mean reversion with RSI + Bollinger Bands")
    
    # Load data
    df = load_data('UBER')
    
    # Add indicators
    indicators = TechnicalIndicators(df)
    indicators.add_rsi(14)
    indicators.add_bbands(length=20, std=2.0)
    df_with_indicators = indicators.df
    
    # Define custom strategy
    def mean_reversion_strategy(row, position):
        """
        Buy when:
        - RSI < 35 AND price near lower BB
        
        Sell when:
        - RSI > 55 OR price near upper BB
        """
        if 'RSI_14' not in row.index:
            return 'HOLD'
        
        rsi = row['RSI_14']
        price = row['Close']
        
        # Find BB columns
        bb_lower = [col for col in row.index if 'BBL' in col]
        bb_upper = [col for col in row.index if 'BBU' in col]
        
        if not bb_lower or not bb_upper:
            return 'HOLD'
        
        lower = row[bb_lower[0]]
        upper = row[bb_upper[0]]
        
        if position is None:
            # Buy conditions
            if rsi < 35 and price < lower * 1.02:
                return 'BUY'
        else:
            # Sell conditions
            if rsi > 55 or price > upper * 0.98:
                return 'SELL'
        
        return 'HOLD'
    
    # Run backtest
    backtester = Backtester(
        df_with_indicators,
        symbol='UBER',
        initial_capital=10000
    )
    
    results = backtester.run_strategy(
        mean_reversion_strategy,
        strategy_name="RSI + BB Mean Reversion"
    )
    
    return results


def demo_5_multi_indicator_strategy():
    """Demo 5: Multi-Indicator Strategy"""
    print("\n" + "="*80)
    print("DEMO 5: Multi-Indicator Confirmation Strategy")
    print("="*80)
    print("Strategy: Requires RSI, MACD, and ADX confirmation")
    
    # Load data
    df = load_data('TQQQ')
    
    # Add multiple indicators
    indicators = TechnicalIndicators(df)
    indicators.add_rsi(14)
    indicators.add_macd()
    indicators.add_adx()
    df_with_indicators = indicators.df
    
    # Run backtest
    backtester = Backtester(
        df_with_indicators,
        symbol='TQQQ',
        initial_capital=10000
    )
    
    results = backtester.run_strategy(
        multi_indicator_strategy,
        strategy_name="Multi-Indicator Confirmation"
    )
    
    return results


def demo_6_strategy_comparison():
    """Demo 6: Compare Multiple Strategies"""
    print("\n" + "="*80)
    print("DEMO 6: Strategy Comparison")
    print("="*80)
    print("Compare performance of different strategies on same data")
    
    # Load and prepare data
    df = load_data('TQQQ')
    indicators = TechnicalIndicators(df)
    indicators.add_common_indicators()
    df_with_indicators = indicators.df
    
    strategies = [
        ('RSI Strategy', rsi_strategy),
        ('MACD Strategy', macd_crossover_strategy),
        ('MA Crossover', moving_average_crossover_strategy),
        ('BB Bounce', bollinger_bounce_strategy),
        ('Multi-Indicator', multi_indicator_strategy)
    ]
    
    results_list = []
    
    for name, strategy_func in strategies:
        backtester = Backtester(
            df_with_indicators,
            symbol='TQQQ',
            initial_capital=10000
        )
        
        result = backtester.run_strategy(strategy_func, strategy_name=name)
        results_list.append(result.to_dict())
    
    # Create comparison table
    comparison_df = pd.DataFrame(results_list)
    comparison_df = comparison_df.sort_values('total_return_pct', ascending=False)
    
    print("\n" + "="*80)
    print("📊 STRATEGY COMPARISON RESULTS")
    print("="*80)
    print("\nRanked by Total Return %:")
    print(comparison_df[['strategy_name', 'total_return_pct', 'win_rate', 
                         'num_trades', 'profit_factor', 'max_drawdown']].to_string(index=False))
    
    return comparison_df


def demo_7_parameter_optimization():
    """Demo 7: Optimize Strategy Parameters"""
    print("\n" + "="*80)
    print("DEMO 7: Parameter Optimization")
    print("="*80)
    print("Find the best RSI parameters for the data")
    
    # Load data
    df = load_data('AAPL')
    
    # Optimize RSI parameters
    results_df = optimize_rsi_parameters(
        df,
        symbol='AAPL',
        rsi_lengths=[9, 14, 21],
        oversold_levels=[25, 30, 35],
        overbought_levels=[65, 70, 75]
    )
    
    # Show best parameters
    best = results_df.iloc[0]
    print(f"\n🏆 BEST PARAMETERS:")
    print(f"   RSI Length:     {best['rsi_length']}")
    print(f"   Oversold:       {best['oversold']}")
    print(f"   Overbought:     {best['overbought']}")
    print(f"   Return:         {best['total_return_pct']:.2f}%")
    print(f"   Win Rate:       {best['win_rate']:.2f}%")
    print(f"   Profit Factor:  {best['profit_factor']:.2f}")
    
    return results_df


def demo_8_buy_and_hold_comparison():
    """Demo 8: Compare Strategy vs Buy & Hold"""
    print("\n" + "="*80)
    print("DEMO 8: Strategy vs Buy & Hold")
    print("="*80)
    
    # Load data
    df = load_data('TQQQ')
    
    # Calculate buy & hold return
    buy_hold_return = ((df.iloc[-1]['Close'] - df.iloc[0]['Close']) / df.iloc[0]['Close']) * 100
    
    # Add indicators and run strategy
    indicators = TechnicalIndicators(df)
    indicators.add_rsi(14)
    indicators.add_macd()
    indicators.add_adx()
    df_with_indicators = indicators.df
    
    backtester = Backtester(
        df_with_indicators,
        symbol='TQQQ',
        initial_capital=10000
    )
    
    results = backtester.run_strategy(
        multi_indicator_strategy,
        strategy_name="Multi-Indicator vs Buy & Hold"
    )
    
    print(f"\n{'='*80}")
    print(f"📊 COMPARISON: Strategy vs Buy & Hold")
    print(f"{'='*80}")
    print(f"\n📈 Buy & Hold:")
    print(f"   Return:         {buy_hold_return:>12.2f}%")
    print(f"   Max Drawdown:   N/A (hold through all)")
    
    print(f"\n🎯 Active Strategy:")
    print(f"   Return:         {results.total_return_pct:>12.2f}%")
    print(f"   Max Drawdown:   {results.max_drawdown:>12.2f}%")
    print(f"   Number of Trades: {results.num_trades:>10}")
    
    if results.total_return_pct > buy_hold_return:
        print(f"\n✅ Strategy OUTPERFORMED Buy & Hold by {results.total_return_pct - buy_hold_return:.2f}%")
    else:
        print(f"\n❌ Strategy UNDERPERFORMED Buy & Hold by {buy_hold_return - results.total_return_pct:.2f}%")
    
    return results


def main():
    """Run all demos"""
    print("\n" + "="*80)
    print("🔬 BACKTESTING FRAMEWORK - COMPREHENSIVE DEMO")
    print("="*80)
    print("\nThis demo shows how to:")
    print("  1. Test pre-built strategies")
    print("  2. Create custom strategies")
    print("  3. Compare multiple strategies")
    print("  4. Optimize parameters")
    print("  5. Compare to buy & hold")
    
    # Run demos
    try:
        demo_1_simple_rsi_strategy()
        input("\nPress Enter to continue to next demo...")
        
        demo_2_macd_strategy()
        input("\nPress Enter to continue to next demo...")
        
        demo_3_moving_average_strategy()
        input("\nPress Enter to continue to next demo...")
        
        demo_4_custom_strategy()
        input("\nPress Enter to continue to next demo...")
        
        demo_5_multi_indicator_strategy()
        input("\nPress Enter to continue to next demo...")
        
        demo_6_strategy_comparison()
        input("\nPress Enter to continue to next demo...")
        
        # demo_7_parameter_optimization()  # Commented out - takes a while
        # input("\nPress Enter to continue to next demo...")
        
        demo_8_buy_and_hold_comparison()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted by user")
    
    print("\n" + "="*80)
    print("✅ Demo complete!")
    print("="*80)
    print("\nNext steps:")
    print("  • Modify the strategies in src/backtester.py")
    print("  • Create your own custom strategies")
    print("  • Run parameter optimization")
    print("  • Test on different symbols and timeframes")
    print("="*80)


if __name__ == "__main__":
    main()

