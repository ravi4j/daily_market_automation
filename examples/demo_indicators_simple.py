#!/usr/bin/env python3
"""
Simple Demo: Technical Indicators with pandas-ta

Quick demonstration of how to use technical indicators
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import pandas as pd
from indicators import TechnicalIndicators


def main():
    # Load data
    print("="*80)
    print("📊 Technical Indicators Demo")
    print("="*80)

    df = pd.read_csv('data/TQQQ.csv', index_col='Date', parse_dates=True)
    df = df.sort_index()  # Ensure chronological order

    print(f"\n✅ Loaded {len(df)} days of TQQQ data")
    print(f"   From: {df.index[0].date()} to {df.index[-1].date()}")

    # Create indicators instance
    indicators = TechnicalIndicators(df)

    # Add common indicators
    print("\n📊 Calculating indicators...")
    indicators.add_sma(20)
    indicators.add_sma(50)
    indicators.add_rsi(14)
    indicators.add_macd()
    indicators.add_bbands()
    indicators.add_atr()
    indicators.add_obv()

    # Get latest values
    latest = indicators.df.iloc[-1]

    print(f"\n📈 Latest Values ({latest.name.date()}):")
    print("-"*80)
    print(f"Close:    ${latest['Close']:.2f}")
    print(f"SMA 20:   ${latest['SMA_20']:.2f}")
    print(f"SMA 50:   ${latest['SMA_50']:.2f}")
    print(f"RSI:      {latest['RSI_14']:.2f}")
    print(f"MACD:     {latest['MACD_12_26_9']:.2f}")
    print(f"ATR:      ${latest['ATR_14']:.2f}")

    # Trading signals
    print(f"\n🎯 Trading Signals:")
    print("-"*80)

    if latest['Close'] > latest['SMA_50']:
        print("✅ Price above SMA50 - BULLISH")
    else:
        print("❌ Price below SMA50 - BEARISH")

    if latest['RSI_14'] > 70:
        print("⚠️  RSI Overbought (>70)")
    elif latest['RSI_14'] < 30:
        print("💰 RSI Oversold (<30)")
    else:
        print("✅ RSI Neutral (30-70)")

    if latest['MACD_12_26_9'] > latest['MACDs_12_26_9']:
        print("🟢 MACD Bullish (above signal)")
    else:
        print("🔴 MACD Bearish (below signal)")

    # Show all available columns
    print(f"\n📊 All Calculated Indicators ({len(indicators.df.columns)} total):")
    print("-"*80)
    for col in indicators.df.columns:
        print(f"  • {col}")

    print("\n" + "="*80)
    print("✅ Demo complete!")
    print("="*80)


if __name__ == "__main__":
    main()
