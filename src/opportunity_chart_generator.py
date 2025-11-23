#!/usr/bin/env python3
"""
OPPORTUNITY CHART GENERATOR

Generates comprehensive visual analysis for trading opportunities:
- Price action with support/resistance
- Technical indicators (RSI, MACD, Volume, Bollinger Bands)
- ABC pattern detection and visualization
- Entry/Stop/Target zones clearly marked
- Intraday buy signals and timing guidance

Used by master_daily_scan.py to create charts for each opportunity.
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle
from datetime import datetime, timedelta
from pathlib import Path
import numpy as np

# Import existing modules
from src.indicators import TechnicalIndicators
from src.abc_pattern_detector import ABCPatternDetector

# Directories
CHARTS_BASE_DIR = Path('charts')
CHARTS_STOCKS_DIR = CHARTS_BASE_DIR / 'stocks'
CHARTS_ETFS_DIR = CHARTS_BASE_DIR / 'etfs'

# Create directories
CHARTS_STOCKS_DIR.mkdir(parents=True, exist_ok=True)
CHARTS_ETFS_DIR.mkdir(parents=True, exist_ok=True)


class OpportunityChartGenerator:
    """
    Generate comprehensive trading opportunity charts with:
    - Multi-panel layout (Price + Indicators)
    - Entry/Stop/Target zones
    - ABC patterns (if present)
    - Intraday buy signals
    """

    def __init__(self):
        self.abc_detector = ABCPatternDetector()

    def generate_opportunity_chart(self, symbol: str, df: pd.DataFrame,
                                   opportunity_data: dict,
                                   asset_type: str = 'stock',
                                   lookback_days: int = 60) -> Path:
        """
        Generate comprehensive opportunity chart.

        Args:
            symbol: Stock/ETF symbol
            df: Price data (must have OHLC + Volume)
            opportunity_data: Dict with entry, stop, target, scores, etc.
            asset_type: 'stock' or 'etf' (determines subfolder)
            lookback_days: Days of history to show (default 60)

        Returns:
            Path to generated chart file
        """
        # Ensure data is sorted ascending
        df = df.sort_index(ascending=True)

        # Take only recent data
        df_recent = df.tail(lookback_days).copy()

        if len(df_recent) < 20:
            raise ValueError(f"Insufficient data for {symbol}: {len(df_recent)} days")

        # Calculate indicators
        indicators = TechnicalIndicators(df_recent)
        df_recent = indicators.add_common_indicators()  # Adds RSI, MACD, BBands, Volume, etc.

        # Detect ABC patterns
        abc_patterns = self.abc_detector.detect_abc_patterns(df_recent)

        # Create figure with 4 panels
        fig = plt.figure(figsize=(16, 12))
        gs = fig.add_gridspec(4, 1, height_ratios=[3, 1, 1, 1], hspace=0.05)

        # Panel 1: Price + ABC Pattern + Entry/Stop/Target
        ax_price = fig.add_subplot(gs[0])
        self._plot_price_action(ax_price, df_recent, symbol, opportunity_data, abc_patterns)

        # Panel 2: RSI
        ax_rsi = fig.add_subplot(gs[1], sharex=ax_price)
        self._plot_rsi(ax_rsi, df_recent)

        # Panel 3: MACD
        ax_macd = fig.add_subplot(gs[2], sharex=ax_price)
        self._plot_macd(ax_macd, df_recent)

        # Panel 4: Volume
        ax_volume = fig.add_subplot(gs[3], sharex=ax_price)
        self._plot_volume(ax_volume, df_recent)

        # Hide x-axis labels on upper panels
        plt.setp(ax_price.get_xticklabels(), visible=False)
        plt.setp(ax_rsi.get_xticklabels(), visible=False)
        plt.setp(ax_macd.get_xticklabels(), visible=False)

        # Format x-axis on bottom panel
        ax_volume.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
        ax_volume.xaxis.set_major_locator(mdates.DayLocator(interval=5))
        plt.xticks(rotation=45)

        # Overall title with opportunity info
        fig.suptitle(
            f'{symbol} - Trading Opportunity Analysis\n'
            f'Score: {opportunity_data.get("composite_score", 0):.1f} | '
            f'Confidence: {opportunity_data.get("confidence", "N/A")} | '
            f'R/R: {opportunity_data.get("risk_reward_ratio", 0):.2f}:1 | '
            f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}',
            fontsize=14, fontweight='bold'
        )

        plt.tight_layout()

        # Save chart to appropriate subfolder (stocks/ or etfs/)
        # Format: SYMBOL_YYYYMMDD.png
        date_str = datetime.now().strftime("%Y%m%d")
        chart_filename = f'{symbol}_{date_str}.png'

        if asset_type.lower() == 'etf':
            chart_file = CHARTS_ETFS_DIR / chart_filename
        else:
            chart_file = CHARTS_STOCKS_DIR / chart_filename

        plt.savefig(chart_file, dpi=150, bbox_inches='tight')
        plt.close()

        return chart_file

    def _plot_price_action(self, ax, df, symbol, opp_data, abc_patterns):
        """Plot price with candlesticks, support/resistance, ABC patterns, and trade zones."""

        # Candlestick chart
        dates = df.index
        opens = df['Open'].values
        highs = df['High'].values
        lows = df['Low'].values
        closes = df['Close'].values

        # Plot candlesticks
        for i in range(len(df)):
            date = dates[i]
            open_price = opens[i]
            close_price = closes[i]
            high_price = highs[i]
            low_price = lows[i]

            color = 'green' if close_price >= open_price else 'red'
            alpha = 0.7

            # Wick (high-low line)
            ax.plot([date, date], [low_price, high_price], color='black', linewidth=0.5, alpha=0.5)

            # Body (open-close rectangle)
            height = abs(close_price - open_price)
            bottom = min(open_price, close_price)
            if height == 0:
                height = (high_price - low_price) * 0.01  # Doji - tiny body

            rect = Rectangle((mdates.date2num(date) - 0.3, bottom), 0.6, height,
                           facecolor=color, edgecolor='black', linewidth=0.5, alpha=alpha)
            ax.add_patch(rect)

        # Plot moving averages
        if 'SMA_20' in df.columns:
            ax.plot(dates, df['SMA_20'], label='SMA 20', color='blue', linewidth=1.5, alpha=0.7)
        if 'EMA_50' in df.columns:
            ax.plot(dates, df['EMA_50'], label='EMA 50', color='orange', linewidth=1.5, alpha=0.7)

        # Plot Bollinger Bands
        if 'BB_Upper' in df.columns and 'BB_Lower' in df.columns:
            ax.plot(dates, df['BB_Upper'], 'gray', linewidth=1, linestyle='--', alpha=0.5)
            ax.plot(dates, df['BB_Lower'], 'gray', linewidth=1, linestyle='--', alpha=0.5)
            ax.fill_between(dates, df['BB_Upper'], df['BB_Lower'], alpha=0.1, color='gray')

        # Plot ABC Pattern if detected
        if abc_patterns:
            self._plot_abc_pattern(ax, df, abc_patterns[0])  # Use first pattern

        # Mark Entry/Stop/Target zones
        entry_price = opp_data.get('entry_price')
        stop_price = opp_data.get('stop_loss')
        target_price = opp_data.get('target_price')

        if entry_price:
            # Entry zone (±1%)
            entry_low = entry_price * 0.99
            entry_high = entry_price * 1.01
            ax.axhspan(entry_low, entry_high, alpha=0.2, color='blue', label=f'Entry Zone ${entry_price:.2f}')
            ax.axhline(entry_price, color='blue', linestyle='--', linewidth=2, label=f'Entry: ${entry_price:.2f}')

        if stop_price:
            ax.axhline(stop_price, color='red', linestyle='--', linewidth=2, label=f'Stop: ${stop_price:.2f}')

        if target_price:
            ax.axhline(target_price, color='green', linestyle='--', linewidth=2, label=f'Target: ${target_price:.2f}')
            # Target zone (price to target)
            if entry_price and target_price > entry_price:
                ax.axhspan(entry_price, target_price, alpha=0.05, color='green')

        # Current price
        current_price = closes[-1]
        ax.axhline(current_price, color='black', linestyle='-', linewidth=1, alpha=0.5)
        ax.text(dates[-1], current_price, f'  ${current_price:.2f}',
               verticalalignment='center', fontweight='bold', fontsize=10)

        # Support and Resistance levels (recent swing highs/lows)
        support, resistance = self._find_support_resistance(df)
        if support:
            ax.axhline(support, color='green', linestyle=':', linewidth=1.5, alpha=0.6, label=f'Support ${support:.2f}')
        if resistance:
            ax.axhline(resistance, color='red', linestyle=':', linewidth=1.5, alpha=0.6, label=f'Resistance ${resistance:.2f}')
        
        # Fibonacci Retracement Levels (Golden Pocket: 0.5, 0.618, 0.65)
        self._plot_fibonacci_levels(ax, df, dates)

        ax.set_ylabel('Price ($)', fontweight='bold')
        ax.legend(loc='upper left', fontsize=8, ncol=2)
        ax.grid(True, alpha=0.3)
        ax.set_title(f'{symbol} - Price Action & Trading Zones', fontweight='bold', pad=10)

    def _plot_abc_pattern(self, ax, df, pattern):
        """Overlay ABC pattern on price chart."""
        dates = df.index

        # Get pattern points
        point_0_idx = pattern.get('point_0_idx')
        point_a_idx = pattern.get('point_a_idx')
        point_b_idx = pattern.get('point_b_idx')

        if point_0_idx is None or point_a_idx is None or point_b_idx is None:
            return

        # Plot ABC pattern lines
        point_0_date = dates[point_0_idx]
        point_a_date = dates[point_a_idx]
        point_b_date = dates[point_b_idx]

        point_0_price = pattern['point_0_price']
        point_a_price = pattern['point_a_price']
        point_b_price = pattern['point_b_price']

        # Draw pattern lines
        ax.plot([point_0_date, point_a_date], [point_0_price, point_a_price],
               'purple', linewidth=2, marker='o', markersize=8, label='ABC Pattern')
        ax.plot([point_a_date, point_b_date], [point_a_price, point_b_price],
               'purple', linewidth=2, marker='o', markersize=8)

        # Labels
        ax.text(point_0_date, point_0_price, '  0', fontweight='bold', color='purple')
        ax.text(point_a_date, point_a_price, '  A', fontweight='bold', color='purple')
        ax.text(point_b_date, point_b_price, '  B', fontweight='bold', color='purple')

    def _find_support_resistance(self, df, window=20):
        """Find recent support and resistance levels."""
        recent = df.tail(window)

        # Support = recent low
        support = recent['Low'].min()

        # Resistance = recent high
        resistance = recent['High'].max()

        return support, resistance

    def _plot_rsi(self, ax, df):
        """Plot RSI with overbought/oversold zones."""
        if 'RSI_14' not in df.columns:
            return

        dates = df.index
        rsi = df['RSI_14']

        ax.plot(dates, rsi, color='purple', linewidth=1.5)
        ax.axhline(70, color='red', linestyle='--', linewidth=1, alpha=0.5)
        ax.axhline(30, color='green', linestyle='--', linewidth=1, alpha=0.5)
        ax.axhline(50, color='gray', linestyle=':', linewidth=0.5, alpha=0.5)

        # Shade overbought/oversold zones
        ax.fill_between(dates, 70, 100, alpha=0.1, color='red')
        ax.fill_between(dates, 0, 30, alpha=0.1, color='green')

        # Highlight current RSI
        current_rsi = rsi.iloc[-1]
        ax.plot(dates[-1], current_rsi, 'o', markersize=8, color='purple')
        ax.text(dates[-1], current_rsi, f'  {current_rsi:.1f}',
               verticalalignment='center', fontweight='bold', fontsize=9)

        ax.set_ylabel('RSI', fontweight='bold')
        ax.set_ylim(0, 100)
        ax.grid(True, alpha=0.3)
        ax.set_title('RSI (14) - Buy when < 30, Sell when > 70', fontsize=10)

    def _plot_macd(self, ax, df):
        """Plot MACD with histogram."""
        if 'MACD' not in df.columns:
            return

        dates = df.index
        macd = df['MACD']
        signal = df['MACD_Signal']
        histogram = df['MACD_Histogram']

        # Plot MACD and Signal lines
        ax.plot(dates, macd, label='MACD', color='blue', linewidth=1.5)
        ax.plot(dates, signal, label='Signal', color='red', linewidth=1.5)

        # Plot histogram (positive = green, negative = red)
        colors = ['green' if h >= 0 else 'red' for h in histogram]
        ax.bar(dates, histogram, color=colors, alpha=0.3, width=0.8)

        ax.axhline(0, color='black', linewidth=0.5, alpha=0.5)
        ax.set_ylabel('MACD', fontweight='bold')
        ax.legend(loc='upper left', fontsize=8)
        ax.grid(True, alpha=0.3)
        ax.set_title('MACD - Buy when crosses above signal', fontsize=10)

    def _plot_volume(self, ax, df):
        """Plot volume with average line."""
        dates = df.index
        volume = df['Volume']

        # Color bars by price movement
        colors = ['green' if df['Close'].iloc[i] >= df['Open'].iloc[i] else 'red'
                 for i in range(len(df))]

        ax.bar(dates, volume, color=colors, alpha=0.6, width=0.8)

        # Plot average volume
        avg_volume = volume.rolling(window=20).mean()
        ax.plot(dates, avg_volume, color='orange', linewidth=2, label='20-day Avg', alpha=0.8)

        # Highlight recent volume spike
        recent_vol = volume.iloc[-1]
        recent_avg = avg_volume.iloc[-1]
        if recent_vol > recent_avg * 1.5:
            ax.plot(dates[-1], recent_vol, '*', markersize=15, color='yellow',
                   markeredgecolor='black', markeredgewidth=1, label='Volume Spike!')

        ax.set_ylabel('Volume', fontweight='bold')
        ax.set_xlabel('Date', fontweight='bold')
        ax.legend(loc='upper left', fontsize=8)
        ax.grid(True, alpha=0.3)
        ax.set_title('Volume - High volume on drop = capitulation/bottom', fontsize=10)

        # Format y-axis for volume (millions)
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x/1e6:.1f}M'))

    def _plot_fibonacci_levels(self, ax, df, dates):
        """
        Calculate and plot Fibonacci retracement levels (Golden Pocket).
        Uses recent swing high and low to calculate key retracement levels.
        
        Golden Pocket = 0.5 to 0.618 (most common reversal zone)
        Classic levels: 0.382, 0.5, 0.618
        """
        # Find swing high and low in the lookback period
        # Use last 30 days to find the swing points
        lookback = min(30, len(df))
        recent_df = df.tail(lookback)
        
        swing_high = recent_df['High'].max()
        swing_low = recent_df['Low'].min()
        
        # Calculate Fibonacci levels
        diff = swing_high - swing_low
        
        if diff < 0.01:  # Avoid division by zero or very flat price action
            return
        
        # Classic Fibonacci retracement levels
        fib_levels = {
            0.382: swing_low + diff * 0.382,  # 38.2% retracement
            0.5: swing_low + diff * 0.5,      # 50% retracement
            0.618: swing_low + diff * 0.618   # 61.8% - Golden Ratio
        }
        
        # Plot the golden pocket zone (50% to 61.8%) as a shaded region
        golden_low = fib_levels[0.5]
        golden_high = fib_levels[0.618]
        ax.axhspan(golden_low, golden_high, alpha=0.15, color='gold', 
                  label='Golden Pocket (50-61.8%)', zorder=1)
        
        # Plot each Fibonacci level line
        colors = {0.382: '#DAA520', 0.5: '#FFD700', 0.618: '#FFA500'}  # Gold shades
        for level, price in fib_levels.items():
            ax.axhline(price, color=colors[level], linestyle='-.', linewidth=1.5, 
                      alpha=0.7, zorder=2)
            # Add price label on the right side
            ax.text(dates[-1], price, f'  Fib {level:.3f} (${price:.2f})',
                   verticalalignment='center', fontsize=8, color=colors[level],
                   fontweight='bold', bbox=dict(boxstyle='round,pad=0.3', 
                   facecolor='white', edgecolor=colors[level], alpha=0.8))


def generate_chart_for_opportunity(symbol: str, csv_path: Path, opportunity_data: dict, asset_type: str = 'stock') -> Path:
    """
    Convenience function to generate chart from CSV file.

    Args:
        symbol: Stock/ETF symbol
        csv_path: Path to CSV file with price data
        opportunity_data: Dict with entry, stop, target, scores
        asset_type: 'stock' or 'etf' (determines subfolder)

    Returns:
        Path to generated chart
    """
    # Load data
    df = pd.read_csv(csv_path, index_col=0, parse_dates=True)
    df = df.sort_index(ascending=True)

    # Generate chart
    generator = OpportunityChartGenerator()
    chart_path = generator.generate_opportunity_chart(symbol, df, opportunity_data, asset_type=asset_type)

    return chart_path


if __name__ == '__main__':
    # Test with sample data
    from pathlib import Path

    test_symbol = 'AAPL'
    test_csv = Path('data/market_data/stocks/AAPL.csv')

    if test_csv.exists():
        test_opportunity = {
            'composite_score': 75.5,
            'confidence': 'MEDIUM',
            'risk_reward_ratio': 3.2,
            'entry_price': 265.00,
            'stop_loss': 260.00,
            'target_price': 280.00
        }

        chart_path = generate_chart_for_opportunity(test_symbol, test_csv, test_opportunity)
        print(f"✅ Test chart generated: {chart_path}")
    else:
        print(f"❌ Test CSV not found: {test_csv}")
