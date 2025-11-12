#!/usr/bin/env python3
"""
Backtesting Framework
Test trading strategies with historical data and indicators
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Callable, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import json


@dataclass
class Trade:
    """Represents a single trade"""
    symbol: str
    entry_date: datetime
    entry_price: float
    exit_date: Optional[datetime] = None
    exit_price: Optional[float] = None
    position_type: str = 'LONG'  # 'LONG' or 'SHORT'
    shares: int = 100
    
    @property
    def is_open(self) -> bool:
        return self.exit_date is None
    
    @property
    def profit_loss(self) -> float:
        if self.is_open:
            return 0.0
        if self.position_type == 'LONG':
            return (self.exit_price - self.entry_price) * self.shares
        else:  # SHORT
            return (self.entry_price - self.exit_price) * self.shares
    
    @property
    def profit_loss_pct(self) -> float:
        if self.is_open:
            return 0.0
        if self.position_type == 'LONG':
            return ((self.exit_price - self.entry_price) / self.entry_price) * 100
        else:  # SHORT
            return ((self.entry_price - self.exit_price) / self.entry_price) * 100
    
    @property
    def holding_days(self) -> int:
        if self.is_open:
            return 0
        return (self.exit_date - self.entry_date).days


@dataclass
class BacktestResults:
    """Results from a backtest"""
    strategy_name: str
    symbol: str
    start_date: datetime
    end_date: datetime
    initial_capital: float
    final_capital: float
    trades: List[Trade] = field(default_factory=list)
    
    @property
    def total_return(self) -> float:
        return self.final_capital - self.initial_capital
    
    @property
    def total_return_pct(self) -> float:
        return (self.total_return / self.initial_capital) * 100
    
    @property
    def num_trades(self) -> int:
        return len([t for t in self.trades if not t.is_open])
    
    @property
    def num_winning_trades(self) -> int:
        return len([t for t in self.trades if not t.is_open and t.profit_loss > 0])
    
    @property
    def num_losing_trades(self) -> int:
        return len([t for t in self.trades if not t.is_open and t.profit_loss < 0])
    
    @property
    def win_rate(self) -> float:
        if self.num_trades == 0:
            return 0.0
        return (self.num_winning_trades / self.num_trades) * 100
    
    @property
    def avg_win(self) -> float:
        wins = [t.profit_loss for t in self.trades if not t.is_open and t.profit_loss > 0]
        return np.mean(wins) if wins else 0.0
    
    @property
    def avg_loss(self) -> float:
        losses = [t.profit_loss for t in self.trades if not t.is_open and t.profit_loss < 0]
        return np.mean(losses) if losses else 0.0
    
    @property
    def profit_factor(self) -> float:
        """Gross profit / Gross loss"""
        total_wins = sum(t.profit_loss for t in self.trades if not t.is_open and t.profit_loss > 0)
        total_losses = abs(sum(t.profit_loss for t in self.trades if not t.is_open and t.profit_loss < 0))
        return total_wins / total_losses if total_losses > 0 else float('inf')
    
    @property
    def max_drawdown(self) -> float:
        """Maximum drawdown percentage"""
        # Calculate equity curve
        equity = [self.initial_capital]
        for trade in sorted(self.trades, key=lambda t: t.entry_date):
            if not trade.is_open:
                equity.append(equity[-1] + trade.profit_loss)
        
        if len(equity) < 2:
            return 0.0
        
        # Calculate drawdown
        peak = equity[0]
        max_dd = 0.0
        
        for value in equity:
            if value > peak:
                peak = value
            dd = ((peak - value) / peak) * 100
            max_dd = max(max_dd, dd)
        
        return max_dd
    
    @property
    def sharpe_ratio(self) -> float:
        """Simplified Sharpe ratio (assuming 0% risk-free rate)"""
        if not self.trades:
            return 0.0
        
        returns = [t.profit_loss_pct for t in self.trades if not t.is_open]
        if not returns:
            return 0.0
        
        return np.mean(returns) / np.std(returns) if np.std(returns) > 0 else 0.0
    
    @property
    def avg_holding_days(self) -> float:
        closed_trades = [t for t in self.trades if not t.is_open]
        if not closed_trades:
            return 0.0
        return np.mean([t.holding_days for t in closed_trades])
    
    def to_dict(self) -> Dict:
        """Convert results to dictionary"""
        return {
            'strategy_name': self.strategy_name,
            'symbol': self.symbol,
            'period': f"{self.start_date.date()} to {self.end_date.date()}",
            'initial_capital': self.initial_capital,
            'final_capital': self.final_capital,
            'total_return': self.total_return,
            'total_return_pct': round(self.total_return_pct, 2),
            'num_trades': self.num_trades,
            'win_rate': round(self.win_rate, 2),
            'num_winning': self.num_winning_trades,
            'num_losing': self.num_losing_trades,
            'avg_win': round(self.avg_win, 2),
            'avg_loss': round(self.avg_loss, 2),
            'profit_factor': round(self.profit_factor, 2),
            'max_drawdown': round(self.max_drawdown, 2),
            'sharpe_ratio': round(self.sharpe_ratio, 2),
            'avg_holding_days': round(self.avg_holding_days, 1)
        }


class Backtester:
    """
    Backtesting engine for trading strategies
    
    Usage:
        backtester = Backtester(df, initial_capital=10000)
        results = backtester.run_strategy(my_strategy_function)
    """
    
    def __init__(self, 
                 df: pd.DataFrame,
                 symbol: str = 'Unknown',
                 initial_capital: float = 10000.0,
                 commission: float = 0.0,
                 slippage: float = 0.0):
        """
        Initialize backtester
        
        Args:
            df: DataFrame with OHLCV data and indicators
            symbol: Symbol name
            initial_capital: Starting capital
            commission: Commission per trade ($ or %)
            slippage: Slippage per trade ($ or %)
        """
        self.df = df.copy()
        self.symbol = symbol
        self.initial_capital = initial_capital
        self.commission = commission
        self.slippage = slippage
        
        self.current_capital = initial_capital
        self.current_position: Optional[Trade] = None
        self.trades: List[Trade] = []
    
    def run_strategy(self, 
                     strategy_func: Callable,
                     strategy_name: str = "Custom Strategy") -> BacktestResults:
        """
        Run a strategy on historical data
        
        Args:
            strategy_func: Function that returns 'BUY', 'SELL', or 'HOLD'
                          Takes (row, position) and returns signal
            strategy_name: Name of the strategy
        
        Returns:
            BacktestResults object
        """
        print(f"\n{'='*80}")
        print(f"🔄 Running Backtest: {strategy_name}")
        print(f"{'='*80}")
        print(f"Symbol: {self.symbol}")
        print(f"Period: {self.df.index[0].date()} to {self.df.index[-1].date()}")
        print(f"Initial Capital: ${self.initial_capital:,.2f}")
        print(f"Total Bars: {len(self.df)}")
        
        # Reset state
        self.current_capital = self.initial_capital
        self.current_position = None
        self.trades = []
        
        # Iterate through historical data
        for i, (date, row) in enumerate(self.df.iterrows()):
            # Get strategy signal
            signal = strategy_func(row, self.current_position)
            
            # Execute signal
            if signal == 'BUY' and self.current_position is None:
                self._open_position(date, row['Close'], 'LONG')
            
            elif signal == 'SELL' and self.current_position is not None:
                self._close_position(date, row['Close'])
        
        # Close any open position at end
        if self.current_position is not None:
            self._close_position(self.df.index[-1], self.df.iloc[-1]['Close'])
        
        # Create results
        results = BacktestResults(
            strategy_name=strategy_name,
            symbol=self.symbol,
            start_date=self.df.index[0],
            end_date=self.df.index[-1],
            initial_capital=self.initial_capital,
            final_capital=self.current_capital,
            trades=self.trades
        )
        
        self._print_results(results)
        
        return results
    
    def _open_position(self, date: datetime, price: float, position_type: str = 'LONG'):
        """Open a new position"""
        # Calculate shares we can buy
        adjusted_price = price * (1 + self.slippage)
        shares = int((self.current_capital * 0.95) / adjusted_price)  # Use 95% of capital
        
        if shares > 0:
            trade = Trade(
                symbol=self.symbol,
                entry_date=date,
                entry_price=adjusted_price,
                position_type=position_type,
                shares=shares
            )
            
            self.current_position = trade
            self.current_capital -= (shares * adjusted_price + self.commission)
            
            print(f"📈 OPEN  {date.date()}: {shares} shares @ ${adjusted_price:.2f}")
    
    def _close_position(self, date: datetime, price: float):
        """Close the current position"""
        if self.current_position is None:
            return
        
        adjusted_price = price * (1 - self.slippage)
        
        self.current_position.exit_date = date
        self.current_position.exit_price = adjusted_price
        
        # Calculate proceeds
        proceeds = self.current_position.shares * adjusted_price - self.commission
        self.current_capital += proceeds
        
        # Record trade
        self.trades.append(self.current_position)
        
        pl = self.current_position.profit_loss
        pl_pct = self.current_position.profit_loss_pct
        emoji = "🟢" if pl > 0 else "🔴"
        
        print(f"{emoji} CLOSE {date.date()}: {self.current_position.shares} shares @ ${adjusted_price:.2f} | "
              f"P/L: ${pl:,.2f} ({pl_pct:+.2f}%)")
        
        self.current_position = None
    
    def _print_results(self, results: BacktestResults):
        """Print backtest results"""
        print(f"\n{'='*80}")
        print(f"📊 BACKTEST RESULTS")
        print(f"{'='*80}")
        
        data = results.to_dict()
        
        print(f"\n💰 Performance:")
        print(f"   Initial Capital:    ${data['initial_capital']:>12,.2f}")
        print(f"   Final Capital:      ${data['final_capital']:>12,.2f}")
        print(f"   Total Return:       ${data['total_return']:>12,.2f}")
        print(f"   Return %:           {data['total_return_pct']:>12.2f}%")
        
        print(f"\n📈 Trade Statistics:")
        print(f"   Total Trades:       {data['num_trades']:>12}")
        print(f"   Winning Trades:     {data['num_winning']:>12}")
        print(f"   Losing Trades:      {data['num_losing']:>12}")
        print(f"   Win Rate:           {data['win_rate']:>12.2f}%")
        print(f"   Avg Win:            ${data['avg_win']:>12,.2f}")
        print(f"   Avg Loss:           ${data['avg_loss']:>12,.2f}")
        
        print(f"\n📊 Risk Metrics:")
        print(f"   Profit Factor:      {data['profit_factor']:>12.2f}")
        print(f"   Max Drawdown:       {data['max_drawdown']:>12.2f}%")
        print(f"   Sharpe Ratio:       {data['sharpe_ratio']:>12.2f}")
        print(f"   Avg Holding Days:   {data['avg_holding_days']:>12.1f}")
        
        print(f"\n{'='*80}")


# ==================== PRE-BUILT STRATEGIES ====================

def rsi_strategy(row, position) -> str:
    """
    Simple RSI Strategy:
    - Buy when RSI < 30 (oversold)
    - Sell when RSI > 70 (overbought)
    """
    if 'RSI_14' not in row.index:
        return 'HOLD'
    
    rsi = row['RSI_14']
    
    if position is None and rsi < 30:
        return 'BUY'
    elif position is not None and rsi > 70:
        return 'SELL'
    
    return 'HOLD'


def macd_crossover_strategy(row, position) -> str:
    """
    MACD Crossover Strategy:
    - Buy when MACD crosses above signal
    - Sell when MACD crosses below signal
    """
    if 'MACD_12_26_9' not in row.index or 'MACDs_12_26_9' not in row.index:
        return 'HOLD'
    
    macd = row['MACD_12_26_9']
    signal = row['MACDs_12_26_9']
    
    if position is None and macd > signal:
        return 'BUY'
    elif position is not None and macd < signal:
        return 'SELL'
    
    return 'HOLD'


def moving_average_crossover_strategy(row, position) -> str:
    """
    Moving Average Crossover:
    - Buy when SMA20 crosses above SMA50
    - Sell when SMA20 crosses below SMA50
    """
    if 'SMA_20' not in row.index or 'SMA_50' not in row.index:
        return 'HOLD'
    
    sma20 = row['SMA_20']
    sma50 = row['SMA_50']
    
    if position is None and sma20 > sma50:
        return 'BUY'
    elif position is not None and sma20 < sma50:
        return 'SELL'
    
    return 'HOLD'


def bollinger_bounce_strategy(row, position) -> str:
    """
    Bollinger Band Bounce:
    - Buy when price touches lower band
    - Sell when price touches upper band
    """
    bb_lower = [col for col in row.index if 'BBL' in col]
    bb_upper = [col for col in row.index if 'BBU' in col]
    
    if not bb_lower or not bb_upper:
        return 'HOLD'
    
    price = row['Close']
    lower = row[bb_lower[0]]
    upper = row[bb_upper[0]]
    
    if position is None and price <= lower * 1.01:  # Within 1% of lower band
        return 'BUY'
    elif position is not None and price >= upper * 0.99:  # Within 1% of upper band
        return 'SELL'
    
    return 'HOLD'


def multi_indicator_strategy(row, position) -> str:
    """
    Multi-Indicator Strategy:
    Requires RSI, MACD, and ADX confirmation
    
    BUY when:
    - RSI < 40 (slight oversold)
    - MACD > Signal (bullish)
    - ADX > 20 (trending)
    
    SELL when:
    - RSI > 60 (slight overbought)
    - OR MACD < Signal (bearish)
    """
    required = ['RSI_14', 'MACD_12_26_9', 'MACDs_12_26_9', 'ADX_14']
    if not all(ind in row.index for ind in required):
        return 'HOLD'
    
    rsi = row['RSI_14']
    macd = row['MACD_12_26_9']
    signal = row['MACDs_12_26_9']
    adx = row['ADX_14']
    
    if position is None:
        # All conditions must be met to buy
        if rsi < 40 and macd > signal and adx > 20:
            return 'BUY'
    else:
        # Exit on any bearish signal
        if rsi > 60 or macd < signal:
            return 'SELL'
    
    return 'HOLD'


# ==================== STRATEGY OPTIMIZATION ====================

def optimize_rsi_parameters(df: pd.DataFrame, 
                           symbol: str,
                           rsi_lengths: List[int] = [7, 14, 21],
                           oversold_levels: List[int] = [20, 25, 30],
                           overbought_levels: List[int] = [70, 75, 80]) -> pd.DataFrame:
    """
    Optimize RSI strategy parameters
    
    Returns DataFrame with results for each combination
    """
    from indicators import TechnicalIndicators
    
    results = []
    
    print(f"\n{'='*80}")
    print(f"🔍 OPTIMIZING RSI STRATEGY")
    print(f"{'='*80}")
    print(f"Testing {len(rsi_lengths)} x {len(oversold_levels)} x {len(overbought_levels)} = "
          f"{len(rsi_lengths) * len(oversold_levels) * len(overbought_levels)} combinations")
    
    for rsi_length in rsi_lengths:
        # Add RSI indicator
        indicators = TechnicalIndicators(df)
        indicators.add_rsi(rsi_length)
        df_with_indicators = indicators.df
        
        for oversold in oversold_levels:
            for overbought in overbought_levels:
                # Create strategy with these parameters
                def parameterized_rsi_strategy(row, position):
                    rsi_col = f'RSI_{rsi_length}'
                    if rsi_col not in row.index:
                        return 'HOLD'
                    
                    rsi = row[rsi_col]
                    
                    if position is None and rsi < oversold:
                        return 'BUY'
                    elif position is not None and rsi > overbought:
                        return 'SELL'
                    
                    return 'HOLD'
                
                # Run backtest
                backtester = Backtester(df_with_indicators, symbol=symbol)
                result = backtester.run_strategy(
                    parameterized_rsi_strategy,
                    strategy_name=f"RSI({rsi_length}) OS={oversold} OB={overbought}"
                )
                
                # Store results
                result_dict = result.to_dict()
                result_dict.update({
                    'rsi_length': rsi_length,
                    'oversold': oversold,
                    'overbought': overbought
                })
                results.append(result_dict)
    
    # Convert to DataFrame and sort by return
    results_df = pd.DataFrame(results)
    results_df = results_df.sort_values('total_return_pct', ascending=False)
    
    print(f"\n{'='*80}")
    print(f"🏆 TOP 5 PARAMETER COMBINATIONS")
    print(f"{'='*80}")
    print(results_df[['rsi_length', 'oversold', 'overbought', 
                      'total_return_pct', 'win_rate', 'num_trades']].head())
    
    return results_df


if __name__ == "__main__":
    print("📊 Backtesting Framework")
    print("=" * 80)
    print("\nAvailable strategies:")
    print("  • rsi_strategy")
    print("  • macd_crossover_strategy")
    print("  • moving_average_crossover_strategy")
    print("  • bollinger_bounce_strategy")
    print("  • multi_indicator_strategy")
    print("\nSee examples/backtest_demo.py for usage examples")

