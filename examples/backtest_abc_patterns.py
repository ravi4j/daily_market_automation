#!/usr/bin/env python3
"""
ABC Pattern Backtesting Demo

Test ABC pattern trading strategy on historical data
and analyze performance metrics.
"""

import sys
from pathlib import Path
import pandas as pd

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from abc_strategy import ABCStrategy
from backtester import Backtester
from indicators import TechnicalIndicators


def backtest_abc_strategy(symbol: str = 'TQQQ', 
                          initial_capital: float = 10000,
                          swing_length: int = 10,
                          min_retrace: float = 0.382,
                          max_retrace: float = 0.786,
                          stop_loss_pips: int = 20,
                          min_risk_reward: float = 2.5):
    """
    Backtest ABC pattern strategy on historical data
    
    Args:
        symbol: Symbol to backtest
        initial_capital: Starting capital
        swing_length: Swing detection length
        min_retrace: Minimum retracement (0.382 = 38.2%)
        max_retrace: Maximum retracement (0.786 = 78.6%)
        stop_loss_pips: Stop loss distance in pips
        min_risk_reward: Minimum risk:reward ratio
    """
    print("\n" + "="*80)
    print(f"📐 ABC PATTERN BACKTEST: {symbol}")
    print("="*80)
    
    # Load data
    data_path = Path('data') / f'{symbol}.csv'
    if not data_path.exists():
        print(f"❌ Data file not found: {data_path}")
        print("   Run: python src/fetch_daily_prices.py")
        return
    
    print(f"\n📊 Loading data from {data_path}...")
    df = pd.read_csv(data_path, parse_dates=['Date']).set_index('Date')
    df = df.sort_index()
    df.columns = df.columns.str.title()
    
    print(f"   Period: {df.index[0].date()} to {df.index[-1].date()}")
    print(f"   Total bars: {len(df)}")
    
    # Add technical indicators
    print("\n🔧 Calculating technical indicators...")
    ta = TechnicalIndicators(df)
    df = ta.add_all_indicators()
    
    # Initialize ABC strategy
    print("\n📐 Initializing ABC pattern strategy...")
    print(f"   Swing Length: {swing_length}")
    print(f"   Retracement Range: {min_retrace*100:.1f}% - {max_retrace*100:.1f}%")
    print(f"   Stop Loss: {stop_loss_pips} pips")
    print(f"   Min Risk:Reward: 1:{min_risk_reward}")
    
    abc_strategy = ABCStrategy(
        swing_length=swing_length,
        min_retrace=min_retrace,
        max_retrace=max_retrace,
        stop_loss_pips=stop_loss_pips,
        min_risk_reward=min_risk_reward
    )
    
    # Generate signals for each bar
    print("\n🔍 Scanning for ABC patterns...")
    signals = []
    patterns_found = 0
    
    for i in range(len(df)):
        df_slice = df.iloc[:i+1]
        if len(df_slice) < swing_length * 3:
            signals.append(None)
            continue
        
        abc_signal = abc_strategy.generate_signal(symbol, df_slice)
        signals.append(abc_signal)
        
        if abc_signal and abc_signal.signal in ['BUY', 'SELL']:
            patterns_found += 1
    
    print(f"   Patterns detected: {patterns_found}")
    
    if patterns_found == 0:
        print("\n⚠️  No ABC patterns found in the data.")
        print("   Try adjusting parameters or using a different symbol/timeframe.")
        return
    
    # Create strategy function for backtester
    def abc_strategy_func(row, position):
        """Strategy function for backtester"""
        idx = row.name if hasattr(row, 'name') else row['Date']
        row_idx = df.index.get_loc(idx)
        
        signal = signals[row_idx]
        
        if signal is None:
            return None
        
        # BUY signal
        if signal.signal == 'BUY' and position is None:
            return {
                'action': 'BUY',
                'entry': signal.best_entry if signal.best_entry else signal.entry_levels[0],
                'stop_loss': signal.stop_loss,
                'take_profit': signal.take_profit_1,
                'reason': f"ABC {signal.pattern_type}"
            }
        
        # SELL signal
        elif signal.signal == 'SELL' and position is None:
            return {
                'action': 'SELL',
                'entry': signal.best_entry if signal.best_entry else signal.entry_levels[0],
                'stop_loss': signal.stop_loss,
                'take_profit': signal.take_profit_1,
                'reason': f"ABC {signal.pattern_type}"
            }
        
        return None
    
    # Run backtest
    print("\n🔬 Running backtest...")
    backtester = Backtester(df=df, symbol=symbol, initial_capital=initial_capital)
    results = backtester.run_strategy(abc_strategy_func)
    
    # Print results
    print("\n" + "="*80)
    print("📊 BACKTEST RESULTS")
    print("="*80)
    
    print(f"\n💰 Performance Metrics:")
    print(f"   Initial Capital:    ${results.initial_capital:,.2f}")
    print(f"   Final Capital:      ${results.final_capital:,.2f}")
    print(f"   Total Return:       {results.total_return:.2f}%")
    print(f"   Max Drawdown:       {results.max_drawdown:.2f}%")
    
    print(f"\n📈 Trade Statistics:")
    print(f"   Total Trades:       {results.total_trades}")
    print(f"   Winning Trades:     {results.winning_trades} ({results.win_rate:.1f}%)")
    print(f"   Losing Trades:      {results.losing_trades}")
    
    if results.total_trades > 0:
        winning_trades = [t for t in results.trades if t.profit > 0]
        losing_trades = [t for t in results.trades if t.profit <= 0]
        
        avg_win = sum(t.profit_pct for t in winning_trades) / len(winning_trades) if winning_trades else 0
        avg_loss = sum(abs(t.profit_pct) for t in losing_trades) / len(losing_trades) if losing_trades else 0
        
        print(f"   Avg Win:            {avg_win:.2f}%")
        print(f"   Avg Loss:           -{avg_loss:.2f}%")
        if avg_loss > 0:
            print(f"   Profit Factor:      {avg_win/avg_loss:.2f}")
    
    # Show recent trades
    if results.trades:
        print(f"\n📝 Recent Trades (last 5):")
        print(f"{'Date':<12} {'Type':<6} {'Entry':<10} {'Exit':<10} {'P/L':<12} {'Reason':<30}")
        print("-" * 80)
        
        for trade in results.trades[-5:]:
            date_str = trade.entry_date.strftime('%Y-%m-%d')
            type_str = "🟢 LONG" if trade.trade_type == "LONG" else "🔴 SHORT"
            entry_str = f"${trade.entry_price:.2f}"
            exit_str = f"${trade.exit_price:.2f}"
            pl_str = f"{trade.profit_pct:+.2f}%"
            reason = trade.reason[:28] + "..." if len(trade.reason) > 28 else trade.reason
            
            print(f"{date_str:<12} {type_str:<6} {entry_str:<10} {exit_str:<10} {pl_str:<12} {reason:<30}")
    
    # Performance summary
    print("\n" + "="*80)
    
    if results.total_return > 0:
        print("✅ STRATEGY PROFITABLE")
    else:
        print("❌ STRATEGY UNPROFITABLE")
    
    print("="*80)
    
    # Parameter recommendations
    print("\n💡 Optimization Tips:")
    if results.win_rate < 40:
        print("   • Win rate is low - consider tightening retracement range")
        print("   • Try increasing min_risk_reward to filter low-quality setups")
    if results.max_drawdown > 20:
        print("   • Max drawdown is high - consider reducing position sizes")
        print("   • Try using tighter stop losses")
    if results.total_trades < 5:
        print("   • Few trades - consider widening retracement range")
        print("   • Try reducing swing_length for more pattern detection")
    
    return results


def main():
    """Run ABC pattern backtest demo"""
    
    print("\n" + "="*80)
    print("🎯 ABC PATTERN BACKTESTING DEMO")
    print("="*80)
    print("\nThis will backtest the ABC pattern strategy on historical data")
    print("and show you detailed performance metrics.")
    
    # Test on TQQQ (leveraged ETF - good for pattern testing)
    results = backtest_abc_strategy(
        symbol='TQQQ',
        initial_capital=10000,
        swing_length=10,
        min_retrace=0.382,
        max_retrace=0.786,
        stop_loss_pips=20,
        min_risk_reward=2.5
    )
    
    print("\n" + "="*80)
    print("✅ BACKTEST COMPLETE")
    print("="*80)
    print("\n💡 Next Steps:")
    print("   1. Try different symbols: AAPL, UBER, ^GSPC")
    print("   2. Optimize parameters: swing_length, retracement range")
    print("   3. Test different risk:reward ratios")
    print("   4. Compare with other strategies in examples/test_all_strategies.py")
    
    print("\n📚 Learn More:")
    print("   • ABC Pattern Guide: docs/ABC_PATTERNS_GUIDE.md")
    print("   • Backtesting Guide: docs/backtesting-guide.md")
    print("   • Strategy Testing: docs/STRATEGY_TESTING_GUIDE.md")


if __name__ == "__main__":
    main()

