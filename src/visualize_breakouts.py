#!/usr/bin/env python3
"""
Visualize breakouts with charts showing trendlines, support/resistance, and reversal points.

Features:
- Candlestick charts with trendlines
- Support/resistance level visualization
- Swing high/low markers
- Breakout alerts on charts
- Saves charts as PNG files
"""

import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
from matplotlib.patches import Rectangle
from matplotlib.lines import Line2D

# Import from detect_breakouts (reuse logic)
from detect_breakouts import (
    load_data,
    calculate_support_resistance,
    find_swing_highs_lows,
    detect_trendline_breakout,
    detect_support_resistance_breakout,
    discover_symbols,
    log
)
from chart_utils import get_chart_organizer

# Get project root
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR) if os.path.basename(SCRIPT_DIR) == "src" else SCRIPT_DIR
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
CHARTS_DIR = os.path.join(PROJECT_ROOT, "charts")

# Ensure charts directory exists
os.makedirs(CHARTS_DIR, exist_ok=True)

# Configuration
# Option 1: Hardcoded symbols (comment out to use auto-discovery)
# SYMBOLS = ["TQQQ", "SP500", "AAPL", "UBER"]

# Option 2: Auto-discover all CSV files in data folder (recommended)
SYMBOLS = None  # Will be auto-populated from data/*.csv

LOOKBACK_DAYS = 60
CHART_STYLE = 'seaborn-v0_8-darkgrid'  # Chart style


def plot_candlestick_simple(ax, df, title=""):
    """
    Plot a simplified candlestick chart using bars.
    """
    up = df[df['Close'] >= df['Open']]
    down = df[df['Close'] < df['Open']]

    # Width for bars
    width = 0.6
    width2 = 0.05

    # Plot up prices (green)
    ax.bar(up.index, up['Close'] - up['Open'], width, bottom=up['Open'],
           color='green', alpha=0.8, label='Up')
    ax.bar(up.index, up['High'] - up['Close'], width2, bottom=up['Close'],
           color='green', alpha=0.8)
    ax.bar(up.index, up['Low'] - up['Open'], width2, bottom=up['Open'],
           color='green', alpha=0.8)

    # Plot down prices (red)
    ax.bar(down.index, down['Close'] - down['Open'], width, bottom=down['Open'],
           color='red', alpha=0.8, label='Down')
    ax.bar(down.index, down['High'] - down['Open'], width2, bottom=down['Open'],
           color='red', alpha=0.8)
    ax.bar(down.index, down['Low'] - down['Close'], width2, bottom=down['Close'],
           color='red', alpha=0.8)

    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.set_ylabel('Price ($)', fontsize=11)
    ax.grid(True, alpha=0.3)


def plot_trendlines(ax, df, lookback=20):
    """
    Plot support and resistance trendlines using linear regression.
    """
    recent_df = df.tail(lookback).copy()
    recent_df['day_num'] = range(len(recent_df))

    # Fit trendline to highs (resistance)
    z_high = np.polyfit(recent_df['day_num'], recent_df['High'], 1)
    p_high = np.poly1d(z_high)
    trendline_high = [p_high(i) for i in range(len(recent_df))]

    # Fit trendline to lows (support)
    z_low = np.polyfit(recent_df['day_num'], recent_df['Low'], 1)
    p_low = np.poly1d(z_low)
    trendline_low = [p_low(i) for i in range(len(recent_df))]

    # Plot trendlines
    ax.plot(recent_df.index, trendline_high,
            color='orange', linewidth=2, linestyle='--',
            label='Resistance Trendline', alpha=0.8)
    ax.plot(recent_df.index, trendline_low,
            color='blue', linewidth=2, linestyle='--',
            label='Support Trendline', alpha=0.8)

    return z_high[0], z_low[0]  # Return slopes


def plot_support_resistance(ax, df, support, resistance, window=20):
    """
    Plot horizontal support and resistance levels.
    """
    recent_df = df.tail(window)

    # Plot support level
    ax.axhline(y=support, color='blue', linewidth=2,
               linestyle=':', label=f'Support: ${support:.2f}', alpha=0.7)

    # Plot resistance level
    ax.axhline(y=resistance, color='red', linewidth=2,
               linestyle=':', label=f'Resistance: ${resistance:.2f}', alpha=0.7)


def plot_swing_points(ax, df):
    """
    Mark swing highs and lows on the chart.
    """
    df_with_swings = find_swing_highs_lows(df, window=5)

    # Get swing points
    swing_highs = df_with_swings[df_with_swings['swing_high']]
    swing_lows = df_with_swings[df_with_swings['swing_low']]

    # Plot swing highs (red triangles pointing down)
    if len(swing_highs) > 0:
        ax.scatter(swing_highs.index, swing_highs['High'],
                  marker='v', color='red', s=100,
                  label='Swing High', zorder=5, alpha=0.8)

    # Plot swing lows (green triangles pointing up)
    if len(swing_lows) > 0:
        ax.scatter(swing_lows.index, swing_lows['Low'],
                  marker='^', color='green', s=100,
                  label='Swing Low', zorder=5, alpha=0.8)


def add_breakout_annotations(ax, df, trendline_result, sr_result):
    """
    Add annotations for detected breakouts.
    """
    latest = df.iloc[-1]
    annotations = []

    # Trendline breakout
    if trendline_result['breakout_type']:
        breakout_type = trendline_result['breakout_type']
        color = 'red' if 'BEARISH' in breakout_type else 'green'
        text = '🚨 BREAKOUT!\n' + breakout_type.replace('_', ' ')

        ax.annotate(text,
                   xy=(df.index[-1], latest['Close']),
                   xytext=(20, 20), textcoords='offset points',
                   bbox=dict(boxstyle='round,pad=0.5', fc=color, alpha=0.7),
                   arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0',
                                 color=color, lw=2),
                   fontsize=10, color='white', fontweight='bold')

    # Support/Resistance breakout
    if sr_result['breakout_type']:
        breakout_type = sr_result['breakout_type']
        color = 'red' if 'BREAKDOWN' in breakout_type else 'green'
        text = '⚠️ ' + breakout_type.replace('_', ' ')

        ax.annotate(text,
                   xy=(df.index[-1], latest['Close']),
                   xytext=(20, -30), textcoords='offset points',
                   bbox=dict(boxstyle='round,pad=0.5', fc=color, alpha=0.7),
                   arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0',
                                 color=color, lw=2),
                   fontsize=10, color='white', fontweight='bold')


def create_breakout_chart(symbol: str, lookback_days: int = 60):
    """
    Create a comprehensive breakout chart for a symbol.
    """
    try:
        log(f"Creating chart for {symbol}...")

        # Load data
        df = load_data(symbol)
        recent_df = df.tail(lookback_days)

        # Calculate support and resistance
        support, resistance = calculate_support_resistance(recent_df, 20)

        # Detect breakouts
        trendline_result = detect_trendline_breakout(recent_df, lookback=20)
        sr_result = detect_support_resistance_breakout(recent_df, support, resistance)

        # Create figure
        fig, ax = plt.subplots(figsize=(16, 9))

        # Plot candlesticks
        latest = recent_df.iloc[-1]
        trend = "📈 UPTREND" if trendline_result['trend_slope_high'] > 0 else "📉 DOWNTREND"
        title = f"{symbol} - Breakout Analysis ({recent_df.index[-1].strftime('%Y-%m-%d')})\n"
        title += f"Price: ${latest['Close']:.2f} | {trend}"

        plot_candlestick_simple(ax, recent_df, title)

        # Plot trendlines
        slope_high, slope_low = plot_trendlines(ax, recent_df, lookback=20)

        # Plot support/resistance
        plot_support_resistance(ax, recent_df, support, resistance, window=20)

        # Plot swing points
        plot_swing_points(ax, recent_df)

        # Add breakout annotations
        add_breakout_annotations(ax, recent_df, trendline_result, sr_result)

        # Format x-axis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
        plt.xticks(rotation=45, ha='right')

        # Legend (best position to avoid overlap)
        ax.legend(loc='best', fontsize=8, framealpha=0.95, ncol=2)

        # Add info box (bottom left to avoid overlap)
        info_text = f"Support: ${support:.2f} ({sr_result['distance_from_support']:.2f}% away)\n"
        info_text += f"Resistance: ${resistance:.2f} ({sr_result['distance_from_resistance']:.2f}% away)\n"
        info_text += f"Lookback: {lookback_days} days"

        ax.text(0.02, 0.02, info_text, transform=ax.transAxes,
               fontsize=9, verticalalignment='bottom',
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.9))

        # Tight layout
        plt.tight_layout()

        # Save chart using organized structure
        chart_organizer = get_chart_organizer(CHARTS_DIR)
        chart_path = chart_organizer.get_breakout_path(symbol, timestamp=False)
        plt.savefig(chart_path, dpi=150, bbox_inches='tight')
        plt.close()

        log(f"✅ Chart saved: {chart_path}")
        return chart_path

    except Exception as e:
        log(f"❌ Error creating chart for {symbol}: {e}")
        return None


def create_all_charts():
    """
    Create breakout charts for all symbols.
    """
    log("="*80)
    log("📊 Creating Breakout Visualization Charts")
    log("="*80)

    # Auto-discover symbols if not hardcoded
    global SYMBOLS
    if SYMBOLS is None:
        SYMBOLS = discover_symbols()
        log(f"Auto-discovered {len(SYMBOLS)} symbols: {', '.join(SYMBOLS)}")
    else:
        log(f"Using configured symbols: {', '.join(SYMBOLS)}")

    if not SYMBOLS:
        log("ERROR: No CSV files found in data/ directory!")
        return []

    chart_paths = []

    for symbol in SYMBOLS:
        chart_path = create_breakout_chart(symbol, LOOKBACK_DAYS)
        if chart_path:
            chart_paths.append(chart_path)

    log("\n" + "="*80)
    log("📋 SUMMARY")
    log("="*80)
    log(f"✅ Created {len(chart_paths)} charts")
    log(f"📁 Charts saved in: {CHARTS_DIR}/")

    for path in chart_paths:
        log(f"   • {os.path.basename(path)}")

    return chart_paths


def main():
    """Main function."""
    try:
        # Set matplotlib style
        try:
            plt.style.use(CHART_STYLE)
        except:
            log(f"Style '{CHART_STYLE}' not found, using default")

        # Create charts
        create_all_charts()

    except Exception as e:
        log(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
