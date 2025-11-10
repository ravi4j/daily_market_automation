#!/usr/bin/env python3
"""
Detect breakouts: trendline violations, support/resistance breaks, and reversal points.

Features:
- Trendline breakout detection (higher highs/lower lows)
- Support/Resistance level breaks
- Swing high/low reversal points
- Configurable lookback periods and thresholds
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Get project root
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR) if os.path.basename(SCRIPT_DIR) == "src" else SCRIPT_DIR
DATA_DIR = os.path.join(PROJECT_ROOT, "data")

# Configuration
# Option 1: Hardcoded symbols (comment out to use auto-discovery)
# SYMBOLS = ["TQQQ", "SP500", "AAPL", "UBER"]

# Option 2: Auto-discover all CSV files in data folder (recommended)
SYMBOLS = None  # Will be auto-populated from data/*.csv

LOOKBACK_DAYS = 60  # Look back 60 days for pattern detection
SUPPORT_RESISTANCE_WINDOW = 20  # Window for S/R calculation
BREAKOUT_THRESHOLD = 0.02  # 2% threshold for significant breakout

# Confirmation Filters
CONFIRMATION_CONFIG = {
    'percentage_threshold': 0.02,  # 2% move required
    'point_threshold': 2.0,         # $2 move required (adjustable per symbol)
    'multiple_closes': 1,           # Number of consecutive closes required
    'time_bars': 1,                 # Number of bars to confirm (1 = same day, 2 = next day)
    'volume_multiplier': 1.2,       # Volume must be 1.2x average
}


def log(msg: str):
    """Print timestamped log message."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now}] {msg}")


def discover_symbols() -> list:
    """
    Auto-discover all symbols by scanning CSV files in data directory.
    Returns list of symbol names (without .csv extension).
    """
    import glob

    csv_files = glob.glob(os.path.join(DATA_DIR, "*.csv"))
    symbols = []

    for csv_file in csv_files:
        # Get filename without path and extension
        symbol = os.path.splitext(os.path.basename(csv_file))[0]
        symbols.append(symbol)

    return sorted(symbols)  # Return alphabetically sorted


def load_data(symbol: str) -> pd.DataFrame:
    """Load CSV data for a symbol."""
    csv_path = os.path.join(DATA_DIR, f"{symbol}.csv")
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Data file not found: {csv_path}")

    df = pd.read_csv(csv_path, parse_dates=["Date"])
    df = df.sort_values("Date", ascending=True)  # Ensure ascending order
    df.set_index("Date", inplace=True)
    return df


def find_swing_highs_lows(df: pd.DataFrame, window: int = 5) -> pd.DataFrame:
    """
    Identify swing highs and lows (reversal points).
    A swing high is a high that's higher than the surrounding candles.
    A swing low is a low that's lower than the surrounding candles.
    """
    df = df.copy()

    # Find swing highs (local maxima)
    df['swing_high'] = False
    df['swing_low'] = False

    for i in range(window, len(df) - window):
        # Swing high: high is greater than surrounding highs
        if df['High'].iloc[i] == df['High'].iloc[i-window:i+window+1].max():
            df.iloc[i, df.columns.get_loc('swing_high')] = True

        # Swing low: low is less than surrounding lows
        if df['Low'].iloc[i] == df['Low'].iloc[i-window:i+window+1].min():
            df.iloc[i, df.columns.get_loc('swing_low')] = True

    return df


def calculate_support_resistance(df: pd.DataFrame, window: int = 20) -> tuple:
    """
    Calculate support and resistance levels based on recent swing points.
    Returns (support_level, resistance_level)
    """
    recent_df = df.tail(window)

    # Support: lowest low in window
    support = recent_df['Low'].min()

    # Resistance: highest high in window
    resistance = recent_df['High'].max()

    return support, resistance


def detect_trendline_breakout(df: pd.DataFrame, lookback: int = 20) -> dict:
    """
    Detect if price has broken out of its recent trendline.
    Uses linear regression on highs (for resistance) and lows (for support).
    """
    recent_df = df.tail(lookback).copy()
    recent_df['day_num'] = range(len(recent_df))

    # Fit trendline to highs (resistance trendline)
    z_high = np.polyfit(recent_df['day_num'], recent_df['High'], 1)
    p_high = np.poly1d(z_high)
    resistance_trendline = p_high(len(recent_df) - 1)

    # Fit trendline to lows (support trendline)
    z_low = np.polyfit(recent_df['day_num'], recent_df['Low'], 1)
    p_low = np.poly1d(z_low)
    support_trendline = p_low(len(recent_df) - 1)

    # Check for breakout
    latest = df.iloc[-1]

    breakout_type = None
    if latest['Close'] > resistance_trendline * (1 + BREAKOUT_THRESHOLD):
        breakout_type = "BULLISH_TRENDLINE_BREAKOUT"
    elif latest['Close'] < support_trendline * (1 - BREAKOUT_THRESHOLD):
        breakout_type = "BEARISH_TRENDLINE_BREAKOUT"

    return {
        'breakout_type': breakout_type,
        'resistance_trendline': resistance_trendline,
        'support_trendline': support_trendline,
        'current_price': latest['Close'],
        'trend_slope_high': z_high[0],  # Positive = uptrend, Negative = downtrend
        'trend_slope_low': z_low[0]
    }


def apply_confirmation_filters(df: pd.DataFrame, breakout_level: float,
                              breakout_direction: str, config: dict = CONFIRMATION_CONFIG) -> dict:
    """
    Apply confirmation filters to validate a breakout.

    Filters:
    1. Intrabar: Check if Close is beyond level (not just wick)
    2. Multiple Closes: Require N consecutive closes beyond level
    3. Time: Require N bars to confirm
    4. Percentage: Minimum % move from level
    5. Point: Minimum $ move from level
    6. Volume: Volume above average

    Args:
        df: DataFrame with OHLCV data
        breakout_level: The support or resistance level
        breakout_direction: 'up' for resistance break, 'down' for support break
        config: Configuration dict with thresholds

    Returns:
        dict with confirmation status and details
    """
    if len(df) < config['time_bars'] + 20:  # Need enough data for volume avg
        return {'confirmed': False, 'reason': 'Insufficient data'}

    # Get recent bars for analysis
    recent_bars = df.tail(config['time_bars'] + 1)
    latest = recent_bars.iloc[-1]

    # Calculate 20-day average volume
    avg_volume = df.tail(20)['Volume'].mean()

    confirmations = {
        'intrabar_close': False,
        'multiple_closes': False,
        'time_confirmed': False,
        'percentage_met': False,
        'point_met': False,
        'volume_confirmed': False,
    }

    # 1. Intrabar Confirmation: Close beyond level (not just wicks)
    if breakout_direction == 'up':
        confirmations['intrabar_close'] = latest['Close'] > breakout_level
    else:  # down
        confirmations['intrabar_close'] = latest['Close'] < breakout_level

    # 2. Multiple Closes Confirmation: N consecutive closes beyond level
    closes_beyond = 0
    for i in range(1, config['multiple_closes'] + 1):
        if len(recent_bars) >= i + 1:
            bar = recent_bars.iloc[-i]
            if breakout_direction == 'up' and bar['Close'] > breakout_level:
                closes_beyond += 1
            elif breakout_direction == 'down' and bar['Close'] < breakout_level:
                closes_beyond += 1

    confirmations['multiple_closes'] = closes_beyond >= config['multiple_closes']

    # 3. Time Confirmation: Sustained for N bars
    bars_beyond = 0
    for i in range(1, config['time_bars'] + 1):
        if len(recent_bars) >= i + 1:
            bar = recent_bars.iloc[-i]
            if breakout_direction == 'up' and bar['Low'] > breakout_level:
                bars_beyond += 1
            elif breakout_direction == 'down' and bar['High'] < breakout_level:
                bars_beyond += 1

    confirmations['time_confirmed'] = bars_beyond >= config['time_bars']

    # 4. Percentage Move Confirmation
    pct_move = abs((latest['Close'] - breakout_level) / breakout_level)
    confirmations['percentage_met'] = pct_move >= config['percentage_threshold']

    # 5. Point Move Confirmation
    point_move = abs(latest['Close'] - breakout_level)
    confirmations['point_met'] = point_move >= config['point_threshold']

    # 6. Volume Confirmation
    confirmations['volume_confirmed'] = latest['Volume'] >= (avg_volume * config['volume_multiplier'])

    # Calculate confirmation score (out of 6)
    confirmation_score = sum(confirmations.values())

    # Require at least 4 out of 6 confirmations
    confirmed = confirmation_score >= 4

    return {
        'confirmed': confirmed,
        'score': confirmation_score,
        'max_score': 6,
        'confirmations': confirmations,
        'percentage_move': pct_move * 100,
        'point_move': point_move,
        'volume_ratio': latest['Volume'] / avg_volume if avg_volume > 0 else 0,
        'level': breakout_level,
        'current_price': latest['Close']
    }


def detect_support_resistance_breakout(df: pd.DataFrame, support: float, resistance: float) -> dict:
    """
    Detect if price has broken through support or resistance levels with confirmation filters.
    """
    latest = df.iloc[-1]
    prev = df.iloc[-2]

    breakout_type = None
    confirmation_result = None

    # Resistance breakout: close above resistance
    if prev['Close'] <= resistance and latest['Close'] > resistance:
        # Apply confirmation filters
        confirmation_result = apply_confirmation_filters(df, resistance, 'up')
        if confirmation_result['confirmed']:
            breakout_type = "RESISTANCE_BREAKOUT_CONFIRMED"
        else:
            breakout_type = "RESISTANCE_BREAKOUT_UNCONFIRMED"

    # Support breakdown: close below support
    elif prev['Close'] >= support and latest['Close'] < support:
        # Apply confirmation filters
        confirmation_result = apply_confirmation_filters(df, support, 'down')
        if confirmation_result['confirmed']:
            breakout_type = "SUPPORT_BREAKDOWN_CONFIRMED"
        else:
            breakout_type = "SUPPORT_BREAKDOWN_UNCONFIRMED"

    result = {
        'breakout_type': breakout_type,
        'support_level': support,
        'resistance_level': resistance,
        'current_price': latest['Close'],
        'distance_from_support': ((latest['Close'] - support) / support) * 100,
        'distance_from_resistance': ((resistance - latest['Close']) / resistance) * 100,
        'confirmation': confirmation_result
    }

    return result


def detect_reversal_points(df: pd.DataFrame) -> dict:
    """
    Detect if current candle is near a previous reversal point (swing high/low).
    """
    df_with_swings = find_swing_highs_lows(df, window=5)
    latest = df_with_swings.iloc[-1]

    # Get recent swing points
    recent_swing_highs = df_with_swings[df_with_swings['swing_high']].tail(5)
    recent_swing_lows = df_with_swings[df_with_swings['swing_low']].tail(5)

    # Check if current price is near a previous swing point
    near_reversal = None
    reversal_price = None

    for idx, row in recent_swing_highs.iterrows():
        if abs(latest['Close'] - row['High']) / row['High'] < 0.02:  # Within 2%
            near_reversal = "NEAR_PREVIOUS_HIGH"
            reversal_price = row['High']
            break

    if not near_reversal:
        for idx, row in recent_swing_lows.iterrows():
            if abs(latest['Close'] - row['Low']) / row['Low'] < 0.02:  # Within 2%
                near_reversal = "NEAR_PREVIOUS_LOW"
                reversal_price = row['Low']
                break

    return {
        'near_reversal': near_reversal,
        'reversal_price': reversal_price,
        'current_price': latest['Close'],
        'latest_swing_high': recent_swing_highs['High'].iloc[-1] if len(recent_swing_highs) > 0 else None,
        'latest_swing_low': recent_swing_lows['Low'].iloc[-1] if len(recent_swing_lows) > 0 else None
    }


def analyze_symbol(symbol: str) -> dict:
    """
    Run complete breakout analysis for a symbol.
    """
    log(f"Analyzing {symbol}...")

    try:
        df = load_data(symbol)
        recent_df = df.tail(LOOKBACK_DAYS)

        # Calculate support and resistance
        support, resistance = calculate_support_resistance(recent_df, SUPPORT_RESISTANCE_WINDOW)

        # Detect breakouts
        trendline_result = detect_trendline_breakout(recent_df, lookback=20)
        sr_result = detect_support_resistance_breakout(recent_df, support, resistance)
        reversal_result = detect_reversal_points(recent_df)

        latest = recent_df.iloc[-1]

        return {
            'symbol': symbol,
            'date': recent_df.index[-1].strftime('%Y-%m-%d'),
            'close': latest['Close'],
            'volume': latest['Volume'],
            'trendline_analysis': trendline_result,
            'support_resistance_analysis': sr_result,
            'reversal_analysis': reversal_result
        }

    except Exception as e:
        log(f"Error analyzing {symbol}: {e}")
        return None


def print_analysis_report(analysis: dict):
    """Print formatted analysis report."""
    if not analysis:
        return

    print("\n" + "="*80)
    print(f"📊 {analysis['symbol']} - {analysis['date']}")
    print("="*80)
    print(f"Current Price: ${analysis['close']:.2f} | Volume: {analysis['volume']:,.0f}")

    # Trendline Analysis
    tl = analysis['trendline_analysis']
    print(f"\n🔹 TRENDLINE ANALYSIS:")
    print(f"   Trend Direction: {'📈 UPTREND' if tl['trend_slope_high'] > 0 else '📉 DOWNTREND'}")
    print(f"   Support Trendline: ${tl['support_trendline']:.2f}")
    print(f"   Resistance Trendline: ${tl['resistance_trendline']:.2f}")
    if tl['breakout_type']:
        print(f"   🚨 BREAKOUT DETECTED: {tl['breakout_type']}")

    # Support/Resistance Analysis
    sr = analysis['support_resistance_analysis']
    print(f"\n🔹 SUPPORT/RESISTANCE ANALYSIS:")
    print(f"   Support: ${sr['support_level']:.2f} ({sr['distance_from_support']:.2f}% away)")
    print(f"   Resistance: ${sr['resistance_level']:.2f} ({sr['distance_from_resistance']:.2f}% away)")
    if sr['breakout_type']:
        print(f"   🚨 BREAKOUT DETECTED: {sr['breakout_type']}")

        # Show confirmation details
        if sr['confirmation']:
            conf = sr['confirmation']
            print(f"\n   📋 CONFIRMATION FILTERS (Score: {conf['score']}/{conf['max_score']}):")
            print(f"      ✓ Intrabar Close: {'✅' if conf['confirmations']['intrabar_close'] else '❌'}")
            print(f"      ✓ Multiple Closes: {'✅' if conf['confirmations']['multiple_closes'] else '❌'}")
            print(f"      ✓ Time Sustained: {'✅' if conf['confirmations']['time_confirmed'] else '❌'}")
            print(f"      ✓ Percentage Move: {'✅' if conf['confirmations']['percentage_met'] else '❌'} ({conf['percentage_move']:.2f}%)")
            print(f"      ✓ Point Move: {'✅' if conf['confirmations']['point_met'] else '❌'} (${conf['point_move']:.2f})")
            print(f"      ✓ Volume Surge: {'✅' if conf['confirmations']['volume_confirmed'] else '❌'} ({conf['volume_ratio']:.2f}x avg)")

            if conf['confirmed']:
                print(f"      ✅ BREAKOUT CONFIRMED!")
            else:
                print(f"      ⚠️  BREAKOUT UNCONFIRMED (needs more confirmation)")

    # Reversal Analysis
    rv = analysis['reversal_analysis']
    print(f"\n🔹 REVERSAL POINT ANALYSIS:")
    if rv['latest_swing_high']:
        print(f"   Latest Swing High: ${rv['latest_swing_high']:.2f}")
    if rv['latest_swing_low']:
        print(f"   Latest Swing Low: ${rv['latest_swing_low']:.2f}")
    if rv['near_reversal']:
        print(f"   ⚠️  {rv['near_reversal']} at ${rv['reversal_price']:.2f}")


def main():
    """Main function to analyze all symbols."""
    log("Starting breakout analysis...")

    # Auto-discover symbols if not hardcoded
    global SYMBOLS
    if SYMBOLS is None:
        SYMBOLS = discover_symbols()
        log(f"Auto-discovered {len(SYMBOLS)} symbols: {', '.join(SYMBOLS)}")
    else:
        log(f"Using configured symbols: {', '.join(SYMBOLS)}")

    if not SYMBOLS:
        log("ERROR: No CSV files found in data/ directory!")
        return

    results = []
    breakouts_found = []

    for symbol in SYMBOLS:
        analysis = analyze_symbol(symbol)
        if analysis:
            results.append(analysis)
            print_analysis_report(analysis)

            # Collect breakouts
            if analysis['trendline_analysis']['breakout_type']:
                breakouts_found.append(f"{symbol}: {analysis['trendline_analysis']['breakout_type']}")
            if analysis['support_resistance_analysis']['breakout_type']:
                breakouts_found.append(f"{symbol}: {analysis['support_resistance_analysis']['breakout_type']}")

    # Summary
    print("\n" + "="*80)
    print("📋 SUMMARY")
    print("="*80)
    if breakouts_found:
        print("🚨 BREAKOUTS DETECTED:")
        for breakout in breakouts_found:
            print(f"   • {breakout}")
    else:
        print("✅ No significant breakouts detected.")

    log(f"Analysis complete. Analyzed {len(results)} symbols.")


if __name__ == "__main__":
    main()
