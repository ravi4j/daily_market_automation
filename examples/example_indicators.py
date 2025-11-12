#!/usr/bin/env python3
"""
Example: Using Technical Indicators

This script demonstrates how to:
1. Load price data
2. Calculate technical indicators
3. Analyze signals from indicators
4. Combine multiple indicators for trading decisions
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import pandas as pd
from indicators import TechnicalIndicators, calculate_indicators, get_available_indicators


def load_data(symbol: str = 'AAPL') -> pd.DataFrame:
    """Load historical price data"""
    data_path = Path(__file__).parent.parent / 'data' / f'{symbol}.csv'

    if not data_path.exists():
        print(f"❌ Data file not found: {data_path}")
        return pd.DataFrame()

    df = pd.read_csv(data_path, index_col='Date', parse_dates=True)
    print(f"✅ Loaded {len(df)} days of {symbol} data")
    print(f"   Date range: {df.index[0].date()} to {df.index[-1].date()}")
    return df


def example_1_common_indicators():
    """Example 1: Add common/popular indicators"""
    print("\n" + "="*80)
    print("EXAMPLE 1: Common Indicators")
    print("="*80)

    df = load_data('TQQQ')
    if df.empty:
        return

    # Use preset to add common indicators
    df_with_indicators = calculate_indicators(df, preset='common')

    # Show latest values
    print("\n📊 Latest Indicator Values:")
    print("-" * 80)

    latest = df_with_indicators.iloc[-1]
    print(f"Date: {df_with_indicators.index[-1].date()}")
    print(f"Close: ${latest['Close']:.2f}")
    print(f"\nTrend:")
    print(f"  SMA 20:  ${latest['SMA_20']:.2f}")
    print(f"  SMA 50:  ${latest['SMA_50']:.2f}")
    print(f"  SMA 200: ${latest['SMA_200']:.2f}")
    print(f"\nMomentum:")
    print(f"  RSI:     {latest['RSI_14']:.2f} {'(Overbought)' if latest['RSI_14'] > 70 else '(Oversold)' if latest['RSI_14'] < 30 else ''}")
    print(f"  MACD:    {latest['MACD_12_26_9']:.2f}")
    print(f"  Signal:  {latest['MACDs_12_26_9']:.2f}")
    print(f"\nVolatility:")
    # Find BB columns (they have different naming patterns)
    bb_upper = [col for col in df_with_indicators.columns if 'BBU' in col][0]
    bb_middle = [col for col in df_with_indicators.columns if 'BBM' in col][0]
    bb_lower = [col for col in df_with_indicators.columns if 'BBL' in col][0]
    print(f"  BB Upper:  ${latest[bb_upper]:.2f}")
    print(f"  BB Middle: ${latest[bb_middle]:.2f}")
    print(f"  BB Lower:  ${latest[bb_lower]:.2f}")
    print(f"  ATR:       ${latest['ATR_14']:.2f}")
    print(f"\nVolume:")
    print(f"  OBV:  {latest['OBV']:,.0f}")
    print(f"  CMF:  {latest['CMF_20']:.2f}")
    print(f"  MFI:  {latest['MFI_14']:.2f}")

    # Trading signals
    print(f"\n🎯 Simple Trading Signals:")
    print("-" * 80)

    # Trend signal
    if latest['Close'] > latest['SMA_50'] > latest['SMA_200']:
        print("✅ BULLISH TREND: Price > SMA50 > SMA200")
    elif latest['Close'] < latest['SMA_50'] < latest['SMA_200']:
        print("❌ BEARISH TREND: Price < SMA50 < SMA200")
    else:
        print("⚪ MIXED TREND")

    # RSI signal
    if latest['RSI_14'] > 70:
        print("⚠️  RSI OVERBOUGHT: Consider taking profits")
    elif latest['RSI_14'] < 30:
        print("💰 RSI OVERSOLD: Potential buying opportunity")
    else:
        print("✅ RSI NEUTRAL")

    # MACD signal
    if latest['MACD_12_26_9'] > latest['MACDs_12_26_9']:
        print("🟢 MACD BULLISH: MACD above signal line")
    else:
        print("🔴 MACD BEARISH: MACD below signal line")


def example_2_custom_indicators():
    """Example 2: Add specific indicators"""
    print("\n" + "="*80)
    print("EXAMPLE 2: Custom Indicator Selection")
    print("="*80)

    df = load_data('AAPL')
    if df.empty:
        return

    # Create indicators instance
    indicators = TechnicalIndicators(df)

    # Add specific indicators
    indicators.add_rsi(14)
    indicators.add_macd()
    indicators.add_supertrend()
    indicators.add_vwap()
    indicators.add_adx()

    df_with_indicators = indicators.df
    latest = df_with_indicators.iloc[-1]

    print(f"\n📊 Custom Indicators for {latest.name.date()}:")
    print("-" * 80)
    print(f"Close:       ${latest['Close']:.2f}")
    print(f"VWAP:        ${latest['VWAP']:.2f}")
    print(f"SuperTrend:  ${latest['SUPERT_7_3.0']:.2f}")
    print(f"ADX:         {latest['ADX_14']:.2f} (Trend Strength)")
    print(f"RSI:         {latest['RSI_14']:.2f}")


def example_3_bollinger_squeeze():
    """Example 3: Bollinger Band Squeeze Detection"""
    print("\n" + "="*80)
    print("EXAMPLE 3: Bollinger Band Squeeze Detection")
    print("="*80)

    df = load_data('SP500')
    if df.empty:
        return

    indicators = TechnicalIndicators(df)
    indicators.add_bbands(length=20, std=2.0)
    indicators.add_atr(length=14)

    df = indicators.df.tail(20)  # Last 20 days

    # Calculate Bollinger Band Width
    bb_upper = [col for col in df.columns if 'BBU' in col][0]
    bb_middle = [col for col in df.columns if 'BBM' in col][0]
    bb_lower = [col for col in df.columns if 'BBL' in col][0]
    df['BB_Width'] = (df[bb_upper] - df[bb_lower]) / df[bb_middle]

    # Find squeeze (narrow bands = low volatility, expect breakout)
    current_width = df['BB_Width'].iloc[-1]
    avg_width = df['BB_Width'].mean()

    print(f"\n📊 Bollinger Band Analysis:")
    print("-" * 80)
    print(f"Current BB Width: {current_width:.4f}")
    print(f"Average BB Width: {avg_width:.4f}")

    if current_width < avg_width * 0.7:
        print("\n🔥 SQUEEZE DETECTED!")
        print("   Low volatility - Expect breakout soon!")
        print("   Watch for direction when price exits the bands")
    else:
        print("\n✅ Normal volatility range")


def example_4_divergence_detection():
    """Example 4: RSI Divergence Detection"""
    print("\n" + "="*80)
    print("EXAMPLE 4: RSI Divergence Detection")
    print("="*80)

    df = load_data('UBER')
    if df.empty:
        return

    indicators = TechnicalIndicators(df)
    indicators.add_rsi(14)

    df = indicators.df.tail(50)

    # Find recent highs/lows
    price_highs = df['Close'].rolling(window=5, center=True).max()
    rsi_highs = df['RSI_14'].rolling(window=5, center=True).max()

    # Bearish divergence: Price makes higher high, RSI makes lower high
    recent_price_high_idx = price_highs.tail(20).idxmax()
    recent_rsi_high_idx = rsi_highs.tail(20).idxmax()

    print(f"\n📊 Divergence Analysis:")
    print("-" * 80)
    print(f"Recent Price High: ${df.loc[recent_price_high_idx, 'Close']:.2f} on {recent_price_high_idx.date()}")
    print(f"Recent RSI High:   {df.loc[recent_rsi_high_idx, 'RSI_14']:.2f} on {recent_rsi_high_idx.date()}")

    if recent_price_high_idx > recent_rsi_high_idx:
        print("\n⚠️  POTENTIAL BEARISH DIVERGENCE")
        print("   Price making new highs but RSI not confirming")
        print("   Possible trend exhaustion")


def example_5_multi_timeframe_analysis():
    """Example 5: Multi-Timeframe Moving Average Analysis"""
    print("\n" + "="*80)
    print("EXAMPLE 5: Multi-Timeframe Moving Average Analysis")
    print("="*80)

    df = load_data('TQQQ')
    if df.empty:
        return

    indicators = TechnicalIndicators(df)

    # Add multiple moving averages
    indicators.add_sma(10)   # Short-term
    indicators.add_sma(20)   # Short-term
    indicators.add_sma(50)   # Medium-term
    indicators.add_sma(100)  # Medium-term
    indicators.add_sma(200)  # Long-term
    indicators.add_ema(12)
    indicators.add_ema(26)

    latest = indicators.df.iloc[-1]

    print(f"\n📊 Moving Average Ladder for {latest.name.date()}:")
    print("-" * 80)
    print(f"Current Price:  ${latest['Close']:.2f}")
    print(f"\nSimple Moving Averages:")
    print(f"  SMA 10:   ${latest['SMA_10']:.2f}")
    print(f"  SMA 20:   ${latest['SMA_20']:.2f}")
    print(f"  SMA 50:   ${latest['SMA_50']:.2f}")
    print(f"  SMA 100:  ${latest['SMA_100']:.2f}")
    print(f"  SMA 200:  ${latest['SMA_200']:.2f}")

    # Golden Cross / Death Cross detection
    df = indicators.df.tail(5)
    sma50_prev = df['SMA_50'].iloc[-2]
    sma200_prev = df['SMA_200'].iloc[-2]
    sma50_curr = df['SMA_50'].iloc[-1]
    sma200_curr = df['SMA_200'].iloc[-1]

    print(f"\n🎯 Cross Signals:")
    print("-" * 80)

    if sma50_prev < sma200_prev and sma50_curr > sma200_curr:
        print("🟢 GOLDEN CROSS! SMA50 crossed above SMA200")
        print("   Strong bullish signal - Long-term uptrend likely")
    elif sma50_prev > sma200_prev and sma50_curr < sma200_curr:
        print("🔴 DEATH CROSS! SMA50 crossed below SMA200")
        print("   Strong bearish signal - Long-term downtrend likely")
    else:
        if sma50_curr > sma200_curr:
            print("✅ Bullish alignment: SMA50 > SMA200")
        else:
            print("❌ Bearish alignment: SMA50 < SMA200")


def main():
    """Run all examples"""
    print("\n" + "="*80)
    print("📊 TECHNICAL INDICATORS - EXAMPLES")
    print("="*80)
    print("\nThis demonstrates how to use 50+ technical indicators")
    print("with your market data for signal generation.\n")

    # Run examples
    example_1_common_indicators()
    example_2_custom_indicators()
    example_3_bollinger_squeeze()
    example_4_divergence_detection()
    example_5_multi_timeframe_analysis()

    # Show available indicators
    print("\n" + "="*80)
    print("📚 AVAILABLE INDICATORS")
    print("="*80)

    available = get_available_indicators()
    total = sum(len(v) for v in available.values())
    print(f"\nTotal: {total} indicators across {len(available)} categories\n")

    for category, indicators in available.items():
        print(f"{category} ({len(indicators)}):")
        for i, indicator in enumerate(indicators, 1):
            print(f"  {i:2}. {indicator}")
        print()

    print("="*80)
    print("✅ Examples complete! Check src/indicators.py for full API")
    print("="*80)


if __name__ == "__main__":
    main()
