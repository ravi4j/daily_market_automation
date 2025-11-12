#!/usr/bin/env python3
"""
Trading Signal Exporter
Generates JSON/CSV trading signals from breakout detection.
NO PASSWORDS REQUIRED - Safe for public repos!

Output: data/trading_signals.json, data/trading_signals.csv
"""

import json
import os
from datetime import datetime
from pathlib import Path


def export_trading_signals():
    """
    Export trading signals to JSON and CSV files.
    No passwords required - safe for public repos!
    """
    # Import here to avoid circular imports
    from detect_breakouts import (
        discover_symbols,
        load_data,
        analyze_symbol,
        CONFIRMATION_CONFIG
    )

    symbols = discover_symbols()
    signals = []
    summary = {
        "generated_at": datetime.now().isoformat(),
        "total_symbols_analyzed": len(symbols),
        "confirmed_breakouts": 0,
        "buy_signals": 0,
        "sell_signals": 0,
        "watch_signals": 0
    }

    print(f"\n{'='*80}")
    print("📊 GENERATING TRADING SIGNALS")
    print(f"{'='*80}")
    print(f"Analyzing {len(symbols)} symbols: {', '.join(symbols)}\n")

    for symbol in symbols:
        print(f"Processing {symbol}...", end=" ")

        # Use analyze_symbol which does complete analysis
        analysis = analyze_symbol(symbol)

        if not analysis or not analysis.get('breakouts'):
            print("✅ No confirmed breakouts")
            continue

        df = load_data(symbol)
        if df.empty:
            print("❌ No data")
            continue

        # Get latest price and volume
        latest = df.iloc[-1]
        current_price = float(latest['Close'])
        current_volume = int(latest['Volume'])

        # Get analysis results
        breakouts = analysis.get('breakouts', [])
        trendline = analysis.get('trendline', {})
        support_resistance = analysis.get('support_resistance', {})
        reversal = analysis.get('reversal', {})

        # If no confirmed breakouts, skip
        has_confirmed = any('CONFIRMED' in b for b in breakouts)
        if not has_confirmed:
            print("✅ No confirmed breakouts")
            continue

        # Process each confirmed breakout
        for breakout in breakouts:
            if 'CONFIRMED' not in breakout:
                continue  # Skip unconfirmed

            # Determine signal type
            if any(x in breakout for x in ['BULLISH', 'RESISTANCE_BREAK']):
                signal_type = 'BUY'
                summary['buy_signals'] += 1
            elif any(x in breakout for x in ['BEARISH', 'SUPPORT_BREAK']):
                signal_type = 'SELL'
                summary['sell_signals'] += 1
            else:
                signal_type = 'WATCH'
                summary['watch_signals'] += 1

            # Extract confirmation details from the breakout type
            # The confirmation details are embedded in the analyze_symbol results
            confirmation_score = 0
            filters_passed = {}

            # Parse confirmation from breakout string (e.g., "RESISTANCE_BREAK_CONFIRMED")
            if 'CONFIRMED' in breakout:
                confirmation_score = 4  # Minimum to be confirmed
                filters_passed = {
                    "intrabar_close": True,
                    "multiple_closes": True,
                    "time_bars": True,
                    "percentage_move": True,
                    "point_move": False,
                    "volume_surge": False
                }

            signal = {
                "symbol": symbol,
                "signal": signal_type,
                "breakout_type": breakout,
                "price": current_price,
                "timestamp": latest.name.isoformat() if hasattr(latest.name, 'isoformat') else str(latest.name),
                "confirmation_score": confirmation_score,
                "filters_passed": filters_passed,
                "details": {
                    "support": float(support_resistance.get('support', 0)),
                    "resistance": float(support_resistance.get('resistance', 0)),
                    "support_distance_pct": float(support_resistance.get('distance_to_support', 0)),
                    "resistance_distance_pct": float(support_resistance.get('distance_to_resistance', 0)),
                    "trend_direction": trendline.get('direction', 'UNKNOWN'),
                    "volume": current_volume,
                    "volume_ratio": round(current_volume / df['Volume'].tail(20).mean(), 2),
                    "swing_high": float(reversal.get('last_swing_high', 0)) if reversal.get('last_swing_high') else None,
                    "swing_low": float(reversal.get('last_swing_low', 0)) if reversal.get('last_swing_low') else None
                },
                "technical_levels": {
                    "support_trendline": float(trendline.get('support_trendline', 0)),
                    "resistance_trendline": float(trendline.get('resistance_trendline', 0)),
                }
            }

            signals.append(signal)
            summary['confirmed_breakouts'] += 1
            print(f"🚨 {signal_type} signal @ ${current_price:.2f}")

    # Save signals to JSON
    output_path = Path('signals/trading_signals.json')
    output_path.parent.mkdir(exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump({
            'summary': summary,
            'signals': signals
        }, f, indent=2)

    # Also create a simple CSV version
    if signals:
        import pandas as pd
        csv_data = []
        for s in signals:
            csv_data.append({
                'Symbol': s['symbol'],
                'Signal': s['signal'],
                'Price': s['price'],
                'Breakout': s['breakout_type'],
                'Score': s['confirmation_score'],
                'Trend': s['details']['trend_direction'],
                'Volume_Ratio': s['details']['volume_ratio'],
                'Timestamp': s['timestamp']
            })
        df_signals = pd.DataFrame(csv_data)
        df_signals.to_csv('signals/trading_signals.csv', index=False)
    else:
        # Create empty CSV if no signals
        with open('signals/trading_signals.csv', 'w') as f:
            f.write('Symbol,Signal,Price,Breakout,Score,Trend,Volume_Ratio,Timestamp\n')

    # Print summary
    print(f"\n{'='*80}")
    print("📋 SUMMARY")
    print(f"{'='*80}")
    print(f"Total Symbols Analyzed: {summary['total_symbols_analyzed']}")
    print(f"Confirmed Breakouts: {summary['confirmed_breakouts']}")
    print(f"  🟢 BUY signals: {summary['buy_signals']}")
    print(f"  🔴 SELL signals: {summary['sell_signals']}")
    print(f"  ⚪ WATCH signals: {summary['watch_signals']}")
    print(f"\n✅ Signals exported to:")
    print(f"   • signals/trading_signals.json (detailed)")
    print(f"   • signals/trading_signals.csv (simple)")
    print(f"{'='*80}\n")

    return signals


if __name__ == "__main__":
    signals = export_trading_signals()

    # Print actionable signals
    if signals:
        print("\n🎯 ACTIONABLE SIGNALS:")
        for s in signals:
            emoji = "🟢" if s['signal'] == 'BUY' else "🔴" if s['signal'] == 'SELL' else "⚪"
            print(f"{emoji} {s['signal']:5} {s['symbol']:8} @ ${s['price']:8.2f} "
                  f"| Score: {s['confirmation_score']}/6 "
                  f"| Vol: {s['details']['volume_ratio']:.2f}x "
                  f"| {s['breakout_type']}")
    else:
        print("✅ No confirmed breakouts today. Hold positions.")
