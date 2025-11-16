#!/usr/bin/env python3
"""
Update News Correlations

Updates the news correlation database with:
1. Price movements for recent news events
2. Recalculated correlation statistics

Run this daily or weekly to keep correlations up-to-date.
"""

import os
import sys
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.news_correlation import NewsCorrelationTracker


def main():
    print("📊 Updating News Correlations...")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    tracker = NewsCorrelationTracker()
    
    # Get stats before update
    stats_before = tracker.get_stats()
    print(f"Before Update:")
    print(f"  Events: {stats_before['total_events']}")
    print(f"  Movements: {stats_before['total_movements']}")
    print(f"  Correlations: {stats_before['total_correlations']}\n")
    
    # Get tracked symbols (you can customize this)
    # For now, we'll use symbols from existing events
    import sqlite3
    conn = sqlite3.connect(tracker.db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT DISTINCT symbol FROM news_events ORDER BY symbol")
    symbols = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    if not symbols:
        print("⚠️  No symbols found in database.")
        print("   News events will be added automatically when opportunities are scanned.")
        return
    
    print(f"📈 Updating price movements for {len(symbols)} symbols...")
    
    for symbol in symbols:
        try:
            print(f"  {symbol}...", end=" ", flush=True)
            tracker.update_price_movements(symbol, days_back=90)
            print("✅")
        except Exception as e:
            print(f"❌ {e}")
    
    print("\n🔄 Recalculating correlations...")
    tracker.calculate_correlations()
    
    # Get stats after update
    stats_after = tracker.get_stats()
    print(f"\nAfter Update:")
    print(f"  Events: {stats_after['total_events']}")
    print(f"  Movements: {stats_after['total_movements']} (+{stats_after['total_movements'] - stats_before['total_movements']})")
    print(f"  Correlations: {stats_after['total_correlations']}\n")
    
    # Show top correlations
    correlations = tracker.get_all_correlations()
    
    if correlations:
        print("📈 Top 5 Positive Correlations (Most Likely to Rebound):\n")
        for i, corr in enumerate(correlations[:5], 1):
            print(f"{i}. {corr.category} / {corr.sentiment}")
            print(f"   ✅ {corr.success_rate*100:.1f}% rebound rate")
            print(f"   📊 Avg gain: {corr.avg_rebound_pct:+.1f}%")
            print(f"   📝 Sample: {corr.sample_size} events ({corr.confidence} confidence)")
            print()
        
        # Show worst correlations
        worst = sorted(correlations, key=lambda x: x.success_rate)[:3]
        print("\n⚠️  Bottom 3 Correlations (Least Likely to Rebound):\n")
        for i, corr in enumerate(worst, 1):
            print(f"{i}. {corr.category} / {corr.sentiment}")
            print(f"   ❌ {corr.success_rate*100:.1f}% rebound rate")
            print(f"   📊 Avg change: {corr.avg_rebound_pct:+.1f}%")
            print(f"   📝 Sample: {corr.sample_size} events ({corr.confidence} confidence)")
            print()
    
    print("✅ Update complete!")


if __name__ == '__main__':
    main()

