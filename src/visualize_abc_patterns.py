#!/usr/bin/env python3
"""
ABC Pattern Visualization

Creates professional charts showing ABC patterns with:
- Pattern structure (0, A, B, C)
- Entry zones (BC zone from B to A2)
- Stop loss and take profit levels
- Pattern activation line
- Risk/reward visualization
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.dates import DateFormatter
from pathlib import Path
from datetime import datetime
from typing import List, Optional
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from abc_pattern_detector import ABCPatternDetector, ABCPattern
from abc_strategy import ABCStrategy
from indicators import TechnicalIndicators
from chart_utils import ChartOrganizer


class ABCPatternVisualizer:
    """Visualize ABC patterns on price charts"""
    
    def __init__(self, figsize=(16, 10), output_dir: str = 'charts'):
        self.figsize = figsize
        self.output_dir = output_dir
        self.chart_organizer = ChartOrganizer(output_dir)
        self.colors = {
            'bullish': '#00ff00',
            'bearish': '#ff0000',
            'entry_zone': '#4169E1',
            'target_zone': '#FFD700',
            'stop_loss': '#ff4444',
            'activation': '#FFA500',
            'a2_line': '#FF8C00'
        }
    
    def create_abc_chart(self, symbol: str, df: pd.DataFrame, 
                        pattern: ABCPattern, output_dir: str = 'charts') -> str:
        """
        Create comprehensive ABC pattern chart
        
        Returns:
            Path to saved chart
        """
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=self.figsize, 
                                       gridspec_kw={'height_ratios': [3, 1]})
        
        # Prepare data and zoom to pattern timeframe
        df_plot = df.copy()
        df_plot = df_plot.reset_index()
        
        # Zoom to pattern timeframe (from point 0 with some buffer)
        df_plot = self._zoom_to_pattern(df_plot, pattern)
        
        # Get column names
        date_col = 'Date' if 'Date' in df_plot.columns else df_plot.columns[0]
        close_col = self._get_col(df_plot, 'close')
        high_col = self._get_col(df_plot, 'high')
        low_col = self._get_col(df_plot, 'low')
        volume_col = self._get_col(df_plot, 'volume')
        
        # Plot price data
        ax1.plot(df_plot[date_col], df_plot[close_col], 
                color='#333333', linewidth=1.5, label='Price', zorder=1)
        
        # Plot pattern structure
        self._plot_pattern_structure(ax1, df_plot, pattern, date_col)
        
        # Plot activation line
        if pattern.activated:
            self._plot_activation_line(ax1, df_plot, pattern, date_col)
        
        # Plot A2 line (new high/low after activation)
        if pattern.a2_price and pattern.a2_bar:
            self._plot_a2_line(ax1, df_plot, pattern, date_col)
        
        # Plot entry zone (BC zone: B to A2)
        if pattern.activated and pattern.entry_levels:
            self._plot_entry_zone(ax1, df_plot, pattern, date_col)
        
        # Plot target zones
        if pattern.take_profits:
            self._plot_target_zone(ax1, df_plot, pattern, date_col)
        
        # Plot stop loss
        if pattern.stop_loss:
            self._plot_stop_loss(ax1, df_plot, pattern, date_col)
        
        # Add pattern info box
        self._add_info_box(ax1, pattern, df_plot[close_col].iloc[-1])
        
        # Format price chart
        ax1.set_ylabel('Price ($)', fontsize=12, fontweight='bold')
        ax1.grid(True, alpha=0.3, linestyle='--')
        ax1.legend(loc='upper left', fontsize=10)
        
        # Title with generation date
        from datetime import datetime
        trend_emoji = "🟢" if pattern.trend == "BULLISH" else "🔴"
        activation_status = "✅ ACTIVATED" if pattern.activated else "⏳ PENDING"
        generation_date = datetime.now().strftime('%Y-%m-%d %H:%M')
        title = f"{trend_emoji} ABC Pattern: {symbol} - {pattern.trend} ({activation_status})\nGenerated: {generation_date}"
        ax1.set_title(title, fontsize=16, fontweight='bold', pad=20)
        
        # Plot volume
        colors = ['green' if df_plot[close_col].iloc[i] >= df_plot[close_col].iloc[i-1] 
                 else 'red' for i in range(1, len(df_plot))]
        colors.insert(0, 'green')
        
        ax2.bar(df_plot[date_col], df_plot[volume_col], 
               color=colors, alpha=0.5, width=0.8)
        ax2.set_ylabel('Volume', fontsize=10, fontweight='bold')
        ax2.grid(True, alpha=0.3, linestyle='--')
        
        # Format dates
        date_format = DateFormatter('%Y-%m-%d')
        ax1.xaxis.set_major_formatter(date_format)
        ax2.xaxis.set_major_formatter(date_format)
        plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        # Adjust layout
        plt.tight_layout()
        
        # Save chart using organized structure
        filepath = self.chart_organizer.get_abc_pattern_path(
            symbol=symbol,
            pattern_type=pattern.trend,
            timestamp=False  # Consistent naming without timestamps
        )
        
        plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        
        return str(filepath)
    
    def _zoom_to_pattern(self, df_plot: pd.DataFrame, pattern: ABCPattern) -> pd.DataFrame:
        """
        Zoom dataframe to pattern timeframe for better visibility
        
        Args:
            df_plot: Full dataframe
            pattern: ABC pattern with bar indices
            
        Returns:
            Zoomed dataframe
        """
        # Add buffer before and after pattern (20% on each side)
        total_pattern_length = len(df_plot) - pattern.bar_0
        buffer = max(int(total_pattern_length * 0.2), 30)  # At least 30 bars buffer
        
        # Calculate zoom window
        start_idx = max(0, pattern.bar_0 - buffer)
        end_idx = min(len(df_plot), len(df_plot) + buffer)
        
        # Zoom to window
        df_zoomed = df_plot.iloc[start_idx:end_idx].copy()
        df_zoomed = df_zoomed.reset_index(drop=True)
        
        # Adjust pattern bar indices to new dataframe
        pattern.bar_0 = pattern.bar_0 - start_idx
        pattern.bar_a = pattern.bar_a - start_idx
        pattern.bar_b = pattern.bar_b - start_idx
        if pattern.bar_c:
            pattern.bar_c = pattern.bar_c - start_idx
        if pattern.a2_bar:
            pattern.a2_bar = pattern.a2_bar - start_idx
        
        return df_zoomed
    
    def _plot_pattern_structure(self, ax, df_plot, pattern: ABCPattern, date_col: str):
        """Plot 0-A-B-C pattern structure"""
        close_col = self._get_col(df_plot, 'close')
        
        # Get dates for pattern points
        date_0 = df_plot[date_col].iloc[pattern.bar_0]
        date_a = df_plot[date_col].iloc[pattern.bar_a]
        date_b = df_plot[date_col].iloc[pattern.bar_b]
        
        color = self.colors['bullish'] if pattern.trend == "BULLISH" else self.colors['bearish']
        
        # Draw 0-A-B lines
        ax.plot([date_0, date_a], [pattern.point_0, pattern.point_a],
               color=color, linewidth=3, linestyle='-', alpha=0.8, zorder=3)
        ax.plot([date_a, date_b], [pattern.point_a, pattern.point_b],
               color=color, linewidth=3, linestyle='-', alpha=0.8, zorder=3)
        
        # Draw projection to C
        if pattern.take_profits:
            target_c = pattern.take_profits[0]  # 1.618 extension
            date_future = df_plot[date_col].iloc[-1]
            ax.plot([date_b, date_future], [pattern.point_b, target_c],
                   color=color, linewidth=2, linestyle='--', alpha=0.5, zorder=2)
        
        # Mark points 0, A, B with larger markers
        marker_size = 400  # Increased from 200
        ax.scatter([date_0], [pattern.point_0], s=marker_size, c=color, 
                  marker='o', edgecolors='white', linewidths=3, zorder=5,
                  label='Pattern Points')
        ax.scatter([date_a], [pattern.point_a], s=marker_size, c=color,
                  marker='o', edgecolors='white', linewidths=3, zorder=5)
        ax.scatter([date_b], [pattern.point_b], s=marker_size, c=color,
                  marker='o', edgecolors='white', linewidths=3, zorder=5)
        
        # Add labels with larger font and better visibility
        label_offset = (df_plot[close_col].max() - df_plot[close_col].min()) * 0.03
        ax.text(date_0, pattern.point_0 - label_offset, '0\n${:.2f}'.format(pattern.point_0), 
               ha='center', va='top', fontsize=14, fontweight='bold',
               bbox=dict(boxstyle='round,pad=0.5', facecolor='white', edgecolor=color, linewidth=2))
        ax.text(date_a, pattern.point_a + label_offset, 'A\n${:.2f}'.format(pattern.point_a),
               ha='center', va='bottom', fontsize=14, fontweight='bold',
               bbox=dict(boxstyle='round,pad=0.5', facecolor='white', edgecolor=color, linewidth=2))
        ax.text(date_b, pattern.point_b - label_offset if pattern.trend == "BULLISH" else pattern.point_b + label_offset, 
               'B\n${:.2f}'.format(pattern.point_b), ha='center', va='top' if pattern.trend == "BULLISH" else 'bottom',
               fontsize=14, fontweight='bold',
               bbox=dict(boxstyle='round,pad=0.5', facecolor='white', edgecolor=color, linewidth=2))
        
        # Mark point C if reached
        if pattern.c_reached and pattern.point_c and pattern.bar_c:
            date_c = df_plot[date_col].iloc[pattern.bar_c]
            ax.scatter([date_c], [pattern.point_c], s=marker_size * 1.2, 
                      c=self.colors['target_zone'], marker='*',
                      edgecolors='white', linewidths=3, zorder=5)
            ax.text(date_c, pattern.point_c + label_offset, 'C\n${:.2f}'.format(pattern.point_c),
                   ha='center', va='bottom', fontsize=14, fontweight='bold',
                   bbox=dict(boxstyle='round,pad=0.5', 
                           facecolor=self.colors['target_zone'], edgecolor='white', linewidth=2))
    
    def _plot_activation_line(self, ax, df_plot, pattern: ABCPattern, date_col: str):
        """Plot activation line at point A"""
        date_a = df_plot[date_col].iloc[pattern.bar_a]
        date_end = df_plot[date_col].iloc[-1]
        
        ax.axhline(y=pattern.point_a, color=self.colors['activation'],
                  linestyle='--', linewidth=2, alpha=0.7,
                  label=f'Activation Line (${pattern.point_a:.2f})', zorder=2)
        
        # Add activation label
        ax.text(date_end, pattern.point_a, '  ACTIVATED ✓',
               va='center', ha='left', fontsize=10, fontweight='bold',
               color=self.colors['activation'],
               bbox=dict(boxstyle='round,pad=0.3', facecolor='white', 
                        edgecolor=self.colors['activation'], alpha=0.8))
    
    def _plot_a2_line(self, ax, df_plot, pattern: ABCPattern, date_col: str):
        """Plot A2 line (new high/low after activation)"""
        date_a2 = df_plot[date_col].iloc[pattern.a2_bar]
        date_end = df_plot[date_col].iloc[-1]
        
        ax.axhline(y=pattern.a2_price, color=self.colors['a2_line'],
                  linestyle='-.', linewidth=2, alpha=0.7,
                  label=f'A2 - New {"High" if pattern.trend == "BULLISH" else "Low"} (${pattern.a2_price:.2f})',
                  zorder=2)
        
        # Mark A2 point with larger marker
        ax.scatter([date_a2], [pattern.a2_price], s=300,
                  c=self.colors['a2_line'], marker='D',
                  edgecolors='white', linewidths=3, zorder=5)
        ax.text(date_a2, pattern.a2_price, ' A2\n ${:.2f}'.format(pattern.a2_price),
               va='center', ha='left', fontsize=12, fontweight='bold',
               color=self.colors['a2_line'],
               bbox=dict(boxstyle='round,pad=0.3', facecolor='white', 
                        edgecolor=self.colors['a2_line'], alpha=0.9))
    
    def _plot_entry_zone(self, ax, df_plot, pattern: ABCPattern, date_col: str):
        """Plot BC entry zone (B to A2)"""
        date_start = df_plot[date_col].iloc[pattern.bar_b]
        date_end = df_plot[date_col].iloc[-1]
        
        # Entry zone box
        entry_min = min(pattern.entry_levels)
        entry_max = max(pattern.entry_levels)
        
        rect = patches.Rectangle(
            (date_start, entry_min),
            date_end - date_start,
            entry_max - entry_min,
            linewidth=2,
            edgecolor=self.colors['entry_zone'],
            facecolor=self.colors['entry_zone'],
            alpha=0.2,
            zorder=1,
            label='BC Entry Zone (B→A2)'
        )
        ax.add_patch(rect)
        
        # Plot individual entry levels
        for i, entry in enumerate(pattern.entry_levels):
            label_text = ['0.5', '0.559', '0.618', '0.667'][i]
            ax.axhline(y=entry, color=self.colors['entry_zone'],
                      linestyle=':', linewidth=1.5, alpha=0.6, zorder=2)
            ax.text(date_end, entry, f'  Entry {i+1} ({label_text}): ${entry:.2f}',
                   va='center', ha='left', fontsize=11, fontweight='bold',
                   color=self.colors['entry_zone'],
                   bbox=dict(boxstyle='round,pad=0.4', facecolor='white',
                           edgecolor=self.colors['entry_zone'], alpha=0.9, linewidth=2))
    
    def _plot_target_zone(self, ax, df_plot, pattern: ABCPattern, date_col: str):
        """Plot target zone (1.618 to 2.0 extension)"""
        date_start = df_plot[date_col].iloc[pattern.bar_b]
        date_end = df_plot[date_col].iloc[-1]
        
        # Target zone box (TP1 to TP3)
        tp_min = min(pattern.take_profits)
        tp_max = max(pattern.take_profits)
        
        rect = patches.Rectangle(
            (date_start, tp_min if pattern.trend == "BULLISH" else tp_max),
            date_end - date_start,
            abs(tp_max - tp_min),
            linewidth=2,
            edgecolor=self.colors['target_zone'],
            facecolor=self.colors['target_zone'],
            alpha=0.15,
            zorder=1,
            label='Target Zone'
        )
        ax.add_patch(rect)
        
        # Plot individual targets
        labels = ['TP1 (1.618)', 'TP2 (1.809)', 'TP3 (2.0)']
        for i, (tp, label) in enumerate(zip(pattern.take_profits, labels)):
            linestyle = '-' if i == 0 else '--'
            alpha = 0.8 if i == 0 else 0.5
            ax.axhline(y=tp, color=self.colors['target_zone'],
                      linestyle=linestyle, linewidth=2, alpha=alpha, zorder=2)
            ax.text(date_end, tp, f'  {label}: ${tp:.2f}',
                   va='center', ha='left', fontsize=11 if i == 0 else 10, 
                   fontweight='bold',
                   color=self.colors['target_zone'],
                   bbox=dict(boxstyle='round,pad=0.4', facecolor='white',
                           edgecolor=self.colors['target_zone'], alpha=0.9, linewidth=2))
    
    def _plot_stop_loss(self, ax, df_plot, pattern: ABCPattern, date_col: str):
        """Plot stop loss line"""
        date_start = df_plot[date_col].iloc[pattern.bar_b]
        date_end = df_plot[date_col].iloc[-1]
        
        ax.axhline(y=pattern.stop_loss, color=self.colors['stop_loss'],
                  linestyle='-', linewidth=3, alpha=0.8,
                  label=f'Stop Loss (${pattern.stop_loss:.2f})', zorder=3)
        
        ax.text(date_end, pattern.stop_loss, '  STOP LOSS ✋',
               va='center', ha='left', fontsize=10, fontweight='bold',
               color='white',
               bbox=dict(boxstyle='round,pad=0.3', 
                        facecolor=self.colors['stop_loss'], 
                        edgecolor='white', linewidth=2))
    
    def _add_info_box(self, ax, pattern: ABCPattern, current_price: float):
        """Add information box with pattern details"""
        info_lines = [
            f"📊 {pattern.trend} ABC Pattern",
            f"{'─' * 35}",
            f"Status: {'✅ Activated' if pattern.activated else '⏳ Pending'}",
            f"Point C: {'✅ Reached' if pattern.c_reached else '❌ Not Yet'}",
            f"",
            f"Pattern Points:",
            f"  0: ${pattern.point_0:.2f}",
            f"  A: ${pattern.point_a:.2f}",
            f"  B: ${pattern.point_b:.2f}",
        ]
        
        if pattern.a2_price:
            info_lines.append(f"  A2: ${pattern.a2_price:.2f}")
        
        if pattern.point_c:
            info_lines.append(f"  C: ${pattern.point_c:.2f}")
        
        info_lines.append(f"")
        info_lines.append(f"Retracement: {pattern.retracement_ratio*100:.1f}%")
        
        if pattern.risk_reward > 0:
            info_lines.append(f"Risk:Reward: 1:{pattern.risk_reward:.1f}")
        
        info_lines.append(f"")
        info_lines.append(f"Current: ${current_price:.2f}")
        
        info_text = '\n'.join(info_lines)
        
        # Add text box
        props = dict(boxstyle='round,pad=0.8', facecolor='white', 
                    edgecolor='gray', alpha=0.95, linewidth=2)
        ax.text(0.02, 0.98, info_text, transform=ax.transAxes,
               fontsize=9, verticalalignment='top', fontfamily='monospace',
               bbox=props, zorder=10)
    
    def _get_col(self, df: pd.DataFrame, pattern: str) -> Optional[str]:
        """Get column name by pattern (case-insensitive)"""
        pattern_lower = pattern.lower()
        for col in df.columns:
            if pattern_lower in col.lower():
                return col
        return None


def generate_abc_charts(data_dir: str = 'data', output_dir: str = 'charts',
                       symbols: List[str] = None):
    """
    Generate ABC pattern charts for all symbols
    
    Args:
        data_dir: Directory containing CSV files
        output_dir: Directory to save charts
        symbols: List of symbols to process (None = all)
    """
    print("\n" + "="*80)
    print("📐 ABC PATTERN CHART GENERATOR")
    print("="*80)
    
    data_path = Path(data_dir)
    
    # Discover symbols
    if symbols is None:
        csv_files = list(data_path.glob('*.csv'))
        symbols = [f.stem for f in csv_files]
    
    if not symbols:
        print("❌ No symbols found")
        return
    
    print(f"\n📊 Processing {len(symbols)} symbols...")
    
    visualizer = ABCPatternVisualizer()
    detector = ABCPatternDetector(swing_length=10)
    
    charts_generated = 0
    
    for symbol in symbols:
        print(f"\n🔍 Analyzing {symbol}...")
        
        # Load data
        file_path = data_path / f'{symbol}.csv'
        if not file_path.exists():
            print(f"  ⚠️  Data file not found")
            continue
        
        try:
            df = pd.read_csv(file_path, parse_dates=['Date']).set_index('Date')
            df = df.sort_index()
            df.columns = df.columns.str.title()
            
            # Add indicators
            ta = TechnicalIndicators(df)
            df = ta.add_all_indicators()
            
            # Detect patterns
            patterns = detector.get_current_patterns(df, max_patterns=1)
            
            if not patterns:
                print(f"  ℹ️  No ABC patterns detected")
                continue
            
            pattern = patterns[0]
            
            # Analyze pattern
            pattern = detector.analyze_pattern(pattern, df)
            
            # Check current status
            for i in range(pattern.bar_a + 1, len(df)):
                pattern = detector.check_activation(pattern, df, i)
                if pattern.activated:
                    pattern = detector.update_a2(pattern, df, i)
                pattern = detector.check_targets_reached(pattern, df, i)
            
            pattern = detector.analyze_pattern(pattern, df)
            
            print(f"  ✅ {pattern.trend} ABC pattern found")
            print(f"     Activated: {pattern.activated}")
            print(f"     Retracement: {pattern.retracement_ratio*100:.1f}%")
            if pattern.risk_reward > 0:
                print(f"     Risk:Reward: 1:{pattern.risk_reward:.1f}")
            
            # Generate chart
            chart_path = visualizer.create_abc_chart(symbol, df, pattern, output_dir)
            print(f"  💾 Chart saved: {chart_path}")
            
            charts_generated += 1
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*80)
    print(f"✅ Generated {charts_generated} ABC pattern charts")
    print("="*80)


def main():
    """CLI interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate ABC pattern charts')
    parser.add_argument('--symbols', nargs='+', help='Symbols to analyze')
    parser.add_argument('--data-dir', default='data', help='Data directory')
    parser.add_argument('--output-dir', default='charts', help='Output directory')
    
    args = parser.parse_args()
    
    generate_abc_charts(
        data_dir=args.data_dir,
        output_dir=args.output_dir,
        symbols=args.symbols
    )


if __name__ == "__main__":
    main()

