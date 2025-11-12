#!/usr/bin/env python3
"""
Fetch Trading Signals from GitHub (Public Repo)
NO AUTHENTICATION REQUIRED - Works with public repos!

Usage:
    python scripts/fetch_signals.py
    python scripts/fetch_signals.py --repo YOUR_USERNAME/daily_market_automation
"""

import requests
import json
import argparse
from datetime import datetime


def fetch_signals(repo="your-username/daily_market_automation", branch="main"):
    """
    Fetch trading signals from GitHub raw URL.
    No authentication needed for public repos!
    """
    # GitHub raw content URL
    url = f"https://raw.githubusercontent.com/{repo}/{branch}/signals/trading_signals.json"

    print(f"📡 Fetching signals from: {repo}")
    print(f"🔗 URL: {url}\n")

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        data = response.json()
        summary = data.get('summary', {})
        signals = data.get('signals', [])

        # Print summary
        print("=" * 80)
        print("📊 TRADING SIGNALS SUMMARY")
        print("=" * 80)
        print(f"Generated: {summary.get('generated_at', 'Unknown')}")
        print(f"Symbols Analyzed: {summary.get('total_symbols_analyzed', 0)}")
        print(f"Confirmed Breakouts: {summary.get('confirmed_breakouts', 0)}")
        print(f"  🟢 BUY signals: {summary.get('buy_signals', 0)}")
        print(f"  🔴 SELL signals: {summary.get('sell_signals', 0)}")
        print(f"  ⚪ WATCH signals: {summary.get('watch_signals', 0)}")
        print()

        if signals:
            print("=" * 80)
            print("🎯 ACTIONABLE SIGNALS")
            print("=" * 80)

            for signal in signals:
                emoji = "🟢" if signal['signal'] == 'BUY' else "🔴" if signal['signal'] == 'SELL' else "⚪"
                print(f"{emoji} {signal['signal']:5} {signal['symbol']:8} @ ${signal['price']:8.2f} "
                      f"| Score: {signal['confirmation_score']}/6 "
                      f"| Vol: {signal['details']['volume_ratio']:.2f}x")
                print(f"   └─ {signal['breakout_type']}")
                print(f"   └─ Trend: {signal['details']['trend_direction']}")
                print()
        else:
            print("✅ No confirmed breakouts today. Hold positions.\n")

        return data

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            print("❌ Error: Signals file not found.")
            print("   Make sure the repo exists and signals have been generated.")
            print(f"   URL: {url}")
        else:
            print(f"❌ HTTP Error: {e}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Network Error: {e}")
    except json.JSONDecodeError as e:
        print(f"❌ JSON Parse Error: {e}")

    return None


def filter_signals(signals, signal_type=None, min_score=4):
    """
    Filter signals by type and minimum confirmation score.

    Args:
        signals: List of signal dictionaries
        signal_type: 'BUY', 'SELL', 'WATCH', or None for all
        min_score: Minimum confirmation score (0-6)

    Returns:
        Filtered list of signals
    """
    filtered = signals

    if signal_type:
        filtered = [s for s in filtered if s['signal'] == signal_type.upper()]

    filtered = [s for s in filtered if s['confirmation_score'] >= min_score]

    return filtered


def main():
    parser = argparse.ArgumentParser(
        description='Fetch trading signals from GitHub (no auth required)'
    )
    parser.add_argument(
        '--repo',
        default='your-username/daily_market_automation',
        help='GitHub repo (format: username/repo)'
    )
    parser.add_argument(
        '--branch',
        default='main',
        help='Branch name (default: main)'
    )
    parser.add_argument(
        '--signal',
        choices=['BUY', 'SELL', 'WATCH'],
        help='Filter by signal type'
    )
    parser.add_argument(
        '--min-score',
        type=int,
        default=4,
        help='Minimum confirmation score (default: 4)'
    )

    args = parser.parse_args()

    # Fetch signals
    data = fetch_signals(args.repo, args.branch)

    if data and args.signal:
        # Apply filters
        signals = data.get('signals', [])
        filtered = filter_signals(signals, args.signal, args.min_score)

        print("=" * 80)
        print(f"🔍 FILTERED RESULTS ({args.signal}, score >= {args.min_score})")
        print("=" * 80)

        if filtered:
            for signal in filtered:
                emoji = "🟢" if signal['signal'] == 'BUY' else "🔴" if signal['signal'] == 'SELL' else "⚪"
                print(f"{emoji} {signal['symbol']:8} @ ${signal['price']:8.2f} "
                      f"| Score: {signal['confirmation_score']}/6")
        else:
            print("No signals match the filter criteria.\n")


if __name__ == "__main__":
    main()
