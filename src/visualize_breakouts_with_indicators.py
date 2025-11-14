#!/usr/bin/env python3
"""
Enhanced Breakout Visualization with Technical Indicators

Generates charts with:
- Candlesticks
- Trendlines (support/resistance)
- Moving Averages (SMA 20, 50, 200)
- RSI subplot
- MACD subplot
- Volume subplot with colors
- Bollinger Bands
- Support/Resistance levels
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
from matplotlib.gridspec import GridSpec

# Import analysis functions
from detect_breakouts import (
    load_data,
    calculate_support_resistance,
    find_swing_highs_lows,
    detect_trendline_breakout,
    detect_support_resistance_breakout,
    discover_symbols,
    log
)

# Import indicators
from indicators import TechnicalIndicators
from chart_utils import get_chart_organizer

# Get project root
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR) if os.path.basename(SCRIPT_DIR) == "src" else SCRIPT_DIR
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
CHARTS_DIR = os.path.join(PROJECT_ROOT, "charts")

# Ensure charts directory exists
os.makedirs(CHARTS_DIR, exist_ok=True)

# Configuration
SYMBOLS = None  # Auto-discover from data/*.csv
LOOKBACK_DAYS = 60


def add_indicators_to_data(df):
    """Add technical indicators to dataframe"""
    ti = TechnicalIndicators(df)

    # Add key indicators
    ti.add_sma([20, 50, 200])
    ti.add_rsi(14)
    ti.add_macd()
    ti.add_bbands(length=20, std=2.0)

    return ti.df


def plot_candlestick_simple(ax, df):
    """Plot simplified candlestick chart"""
    up = df[df['Close'] >= df['Open']]
    down = df[df['Close'] < df['Open']]

    width = 0.6
    width2 = 0.05

    # Up candles (green)
    ax.bar(up.index, up['Close'] - up['Open'], width, bottom=up['Open'],
           color='green', alpha=0.8)
    ax.bar(up.index, up['High'] - up['Close'], width2, bottom=up['Close'],
           color='green', alpha=0.8)
    ax.bar(up.index, up['Low'] - up['Open'], width2, bottom=up['Open'],
           color='green', alpha=0.8)

    # Down candles (red)
    ax.bar(down.index, down['Close'] - down['Open'], width, bottom=down['Open'],
           color='red', alpha=0.8)
    ax.bar(down.index, down['High'] - down['Open'], width2, bottom=down['Open'],
           color='red', alpha=0.8)
    ax.bar(down.index, down['Low'] - down['Close'], width2, bottom=down['Close'],
           color='red', alpha=0.8)


def plot_trendlines(ax, df, lookback=20):
    """Plot support and resistance trendlines"""
    recent_df = df.tail(lookback).copy()
    recent_df['day_num'] = range(len(recent_df))

    # Resistance trendline (highs)
    z_high = np.polyfit(recent_df['day_num'], recent_df['High'], 1)
    p_high = np.poly1d(z_high)
    trendline_high = [p_high(i) for i in range(len(recent_df))]

    # Support trendline (lows)
    z_low = np.polyfit(recent_df['day_num'], recent_df['Low'], 1)
    p_low = np.poly1d(z_low)
    trendline_low = [p_low(i) for i in range(len(recent_df))]

    ax.plot(recent_df.index, trendline_high, 'r--', linewidth=2, alpha=0.7, label='Resistance')
    ax.plot(recent_df.index, trendline_low, 'g--', linewidth=2, alpha=0.7, label='Support')


def plot_moving_averages(ax, df):
    """Plot moving averages"""
    if 'SMA_20' in df.columns:
        ax.plot(df.index, df['SMA_20'], 'blue', linewidth=1.5, alpha=0.7, label='SMA 20')
    if 'SMA_50' in df.columns:
        ax.plot(df.index, df['SMA_50'], 'orange', linewidth=1.5, alpha=0.7, label='SMA 50')
    if 'SMA_200' in df.columns:
        ax.plot(df.index, df['SMA_200'], 'purple', linewidth=1.5, alpha=0.7, label='SMA 200')


def plot_bollinger_bands(ax, df):
    """Plot Bollinger Bands"""
    # Find BB columns
    bb_upper = [col for col in df.columns if 'BBU' in col or 'bbu' in col]
    bb_lower = [col for col in df.columns if 'BBL' in col or 'bbl' in col]
    bb_middle = [col for col in df.columns if 'BBM' in col or 'bbm' in col]

    if bb_upper and bb_lower:
        ax.plot(df.index, df[bb_upper[0]], 'gray', linewidth=1, alpha=0.5, linestyle='--')
        ax.plot(df.index, df[bb_lower[0]], 'gray', linewidth=1, alpha=0.5, linestyle='--')

        # Fill between bands
        ax.fill_between(df.index, df[bb_upper[0]], df[bb_lower[0]],
                        alpha=0.1, color='gray', label='Bollinger Bands')


def plot_support_resistance(ax, df, support, resistance):
    """Plot horizontal support and resistance levels"""
    if support:
        ax.axhline(y=support, color='green', linestyle=':', linewidth=2, alpha=0.6, label=f'Support ${support:.2f}')
    if resistance:
        ax.axhline(y=resistance, color='red', linestyle=':', linewidth=2, alpha=0.6, label=f'Resistance ${resistance:.2f}')


def plot_rsi(ax, df):
    """Plot RSI indicator"""
    if 'RSI_14' in df.columns:
        ax.plot(df.index, df['RSI_14'], 'purple', linewidth=1.5)
        ax.axhline(y=70, color='red', linestyle='--', linewidth=1, alpha=0.5)
        ax.axhline(y=30, color='green', linestyle='--', linewidth=1, alpha=0.5)
        ax.fill_between(df.index, 30, 70, alpha=0.1, color='gray')
        ax.set_ylabel('RSI', fontsize=10)
        ax.set_ylim(0, 100)
        ax.grid(True, alpha=0.3)
        ax.set_title('RSI (14)', fontsize=10)


def plot_macd(ax, df):
    """Plot MACD indicator"""
    macd_col = [col for col in df.columns if 'MACD_12_26_9' == col]
    signal_col = [col for col in df.columns if 'MACDs_12_26_9' == col]
    hist_col = [col for col in df.columns if 'MACDh_12_26_9' == col]

    if macd_col and signal_col and hist_col:
        # Plot histogram
        colors = ['green' if x >= 0 else 'red' for x in df[hist_col[0]]]
        ax.bar(df.index, df[hist_col[0]], color=colors, alpha=0.3, width=0.8)

        # Plot MACD and signal lines
        ax.plot(df.index, df[macd_col[0]], 'blue', linewidth=1.5, label='MACD')
        ax.plot(df.index, df[signal_col[0]], 'red', linewidth=1.5, label='Signal')

        ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        ax.set_ylabel('MACD', fontsize=10)
        ax.legend(loc='upper left', fontsize=8)
        ax.grid(True, alpha=0.3)
        ax.set_title('MACD (12, 26, 9)', fontsize=10)


def plot_volume(ax, df):
    """Plot volume bars"""
    colors = ['green' if df['Close'].iloc[i] >= df['Open'].iloc[i] else 'red'
              for i in range(len(df))]
    ax.bar(df.index, df['Volume'], color=colors, alpha=0.5, width=0.8)
    ax.set_ylabel('Volume', fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.set_title('Volume', fontsize=10)

    # Format y-axis to show millions/thousands
    ax.ticklabel_format(style='plain', axis='y')


def create_enhanced_chart(symbol, lookback_days=60):
    """
    Create enhanced chart with indicators for a symbol
    """
    log(f"Generating enhanced chart for {symbol}...")

    # Load data
    df = load_data(symbol)
    if df is None or len(df) < lookback_days:
        log(f"  ⚠️  Insufficient data for {symbol}")
        return None

    # Get recent data
    df_recent = df.tail(lookback_days).copy()

    # Add indicators
    df_with_indicators = add_indicators_to_data(df_recent)

    # Calculate support/resistance
    support, resistance = calculate_support_resistance(df_recent)

    # Detect breakouts
    trendline_result = detect_trendline_breakout(df_recent)
    sr_result = detect_support_resistance_breakout(df_recent, support, resistance)

    # Create figure with subplots
    fig = plt.figure(figsize=(16, 12))
    gs = GridSpec(5, 1, height_ratios=[3, 1, 1, 1, 1], hspace=0.3)

    # Main price chart (top, largest)
    ax_price = fig.add_subplot(gs[0])

    # Plot candlesticks
    plot_candlestick_simple(ax_price, df_with_indicators)

    # Add Bollinger Bands (behind everything)
    plot_bollinger_bands(ax_price, df_with_indicators)

    # Add moving averages
    plot_moving_averages(ax_price, df_with_indicators)

    # Add trendlines
    plot_trendlines(ax_price, df_with_indicators, lookback=lookback_days)

    # Add support/resistance
    plot_support_resistance(ax_price, df_with_indicators, support, resistance)

    # Mark swing highs/lows
    df_swings = find_swing_highs_lows(df_recent)
    swing_highs = df_swings[df_swings['swing_high']]
    swing_lows = df_swings[df_swings['swing_low']]

    ax_price.plot(swing_highs.index, swing_highs['High'], 'rv', markersize=8, alpha=0.7, label='Swing High')
    ax_price.plot(swing_lows.index, swing_lows['Low'], 'g^', markersize=8, alpha=0.7, label='Swing Low')

    # Title with breakout info
    latest_price = df_recent['Close'].iloc[-1]
    title = f"{symbol} - ${latest_price:.2f}"

    # Clean up trendline result (extract breakout_type from dict)
    if trendline_result and isinstance(trendline_result, dict):
        trend_type = trendline_result.get('breakout_type')
        if trend_type:
            # Make it more readable: BEARISH_TRENDLINE_BREAKOUT → Bearish Trendline
            trend_msg = trend_type.replace('_', ' ').title().replace('Breakout', '').strip()
            title += f" | 🔴 {trend_msg}"

    # Clean up S/R result (extract breakout_type from dict)
    if sr_result and isinstance(sr_result, dict):
        sr_type = sr_result.get('breakout_type')
        if sr_type:
            # Make it more readable
            sr_msg = sr_type.replace('_', ' ').title().replace('Breakout', '').strip()
            title += f" | 🟢 {sr_msg}"

    ax_price.set_title(title, fontsize=14, fontweight='bold', pad=15)
    ax_price.set_ylabel('Price ($)', fontsize=11)
    ax_price.grid(True, alpha=0.3)

    # Legend (compact, 2 columns)
    ax_price.legend(loc='upper left', fontsize=8, ncol=3)

    # RSI subplot
    ax_rsi = fig.add_subplot(gs[1], sharex=ax_price)
    plot_rsi(ax_rsi, df_with_indicators)

    # MACD subplot
    ax_macd = fig.add_subplot(gs[2], sharex=ax_price)
    plot_macd(ax_macd, df_with_indicators)

    # Volume subplot
    ax_volume = fig.add_subplot(gs[3], sharex=ax_price)
    plot_volume(ax_volume, df_with_indicators)

    # Info box (bottom)
    ax_info = fig.add_subplot(gs[4])
    ax_info.axis('off')

    # Compile analysis info
    info_text = f"📊 Technical Analysis Summary\n"
    info_text += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    info_text += f"Period: {df_recent.index[0].strftime('%Y-%m-%d')} to {df_recent.index[-1].strftime('%Y-%m-%d')}\n"
    info_text += f"Latest Close: ${latest_price:.2f}\n"

    # Add indicator values
    if 'RSI_14' in df_with_indicators.columns:
        rsi = df_with_indicators['RSI_14'].iloc[-1]
        info_text += f"RSI(14): {rsi:.2f} "
        if rsi > 70:
            info_text += "🔴 Overbought"
        elif rsi < 30:
            info_text += "🟢 Oversold"
        else:
            info_text += "⚪ Neutral"
        info_text += "\n"

    if 'SMA_20' in df_with_indicators.columns:
        sma20 = df_with_indicators['SMA_20'].iloc[-1]
        sma50 = df_with_indicators.get('SMA_50', pd.Series([None])).iloc[-1]
        sma200 = df_with_indicators.get('SMA_200', pd.Series([None])).iloc[-1]

        info_text += f"SMA20: ${sma20:.2f}"
        if sma50:
            info_text += f" | SMA50: ${sma50:.2f}"
        if sma200:
            info_text += f" | SMA200: ${sma200:.2f}"
        info_text += "\n"

        # Trend analysis
        if sma200 and latest_price > sma20 > sma50 > sma200:
            info_text += "Trend: 🟢 Strong Uptrend (Price > SMA20 > SMA50 > SMA200)\n"
        elif sma200 and latest_price < sma20 < sma50 < sma200:
            info_text += "Trend: 🔴 Strong Downtrend (Price < SMA20 < SMA50 < SMA200)\n"
        elif latest_price > sma20:
            info_text += "Trend: 🟡 Above SMA20 (Short-term bullish)\n"
        else:
            info_text += "Trend: 🟡 Below SMA20 (Short-term bearish)\n"

    if support:
        info_text += f"Support: ${support:.2f} | "
    if resistance:
        info_text += f"Resistance: ${resistance:.2f}\n"

    # Add breakout alerts (clean format)
    if trendline_result and isinstance(trendline_result, dict):
        trend_type = trendline_result.get('breakout_type')
        if trend_type:
            trend_msg = trend_type.replace('_', ' ').title()
            trend_conf = trendline_result.get('confirmation_score', '')
            info_text += f"⚠️  {trend_msg}"
            if trend_conf:
                info_text += f" (Score: {trend_conf}/6)"
            info_text += "\n"

    if sr_result and isinstance(sr_result, dict):
        sr_type = sr_result.get('breakout_type')
        if sr_type:
            sr_msg = sr_type.replace('_', ' ').title()
            sr_conf = sr_result.get('confirmation_score', '')
            info_text += f"⚠️  {sr_msg}"
            if sr_conf:
                info_text += f" (Score: {sr_conf}/6)"
            info_text += "\n"

    ax_info.text(0.02, 0.5, info_text, fontsize=9, verticalalignment='center',
                family='monospace', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))

    # Format x-axis
    ax_volume.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax_volume.xaxis.set_major_locator(mdates.AutoDateLocator())
    plt.setp(ax_volume.xaxis.get_majorticklabels(), rotation=45, ha='right')

    # Remove x-labels from upper subplots
    plt.setp(ax_price.get_xticklabels(), visible=False)
    plt.setp(ax_rsi.get_xticklabels(), visible=False)
    plt.setp(ax_macd.get_xticklabels(), visible=False)

    # Save chart
    # Save chart using organized structure
    chart_organizer = get_chart_organizer(CHARTS_DIR)
    output_file = chart_organizer.get_indicators_path(symbol, timestamp=False)
    plt.tight_layout()
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    plt.close()

    log(f"  ✅ Saved: {output_file}")
    return output_file


def create_all_enhanced_charts(symbols=None, lookback_days=60):
    """Create enhanced charts for all symbols"""
    if symbols is None:
        symbols = discover_symbols()

    log(f"\n{'='*80}")
    log(f"📊 GENERATING ENHANCED BREAKOUT CHARTS WITH INDICATORS")
    log(f"{'='*80}")
    log(f"Symbols: {', '.join(symbols)}")
    log(f"Lookback: {lookback_days} days")
    log(f"Output: {CHARTS_DIR}/")

    charts_created = []
    for symbol in symbols:
        try:
            chart_path = create_enhanced_chart(symbol, lookback_days)
            if chart_path:
                charts_created.append(chart_path)
        except Exception as e:
            import traceback
            log(f"  ❌ Error creating chart for {symbol}: {e}")
            traceback.print_exc()

    log(f"\n{'='*80}")
    log(f"✅ Created {len(charts_created)} enhanced charts")
    log(f"{'='*80}\n")

    return charts_created


if __name__ == "__main__":
    # Generate enhanced charts for all symbols
    create_all_enhanced_charts(SYMBOLS, LOOKBACK_DAYS)
