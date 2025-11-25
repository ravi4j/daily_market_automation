#!/usr/bin/env python3
"""
NIGHTLY SYMBOL RANKING
Fetch and rank all US stocks and ETFs by volume and market cap
Runs once per night, saves to CSV for fast daily access
"""

import yfinance as yf
import pandas as pd
import finnhub
import os
import time
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Load environment
load_dotenv()
PROJECT_ROOT = Path(__file__).parent.parent
METADATA_DIR = PROJECT_ROOT / 'data' / 'metadata'
METADATA_DIR.mkdir(parents=True, exist_ok=True)

def get_all_us_symbols():
    """
    Get ALL US symbols from Finnhub
    No limits - we'll rank all ~23,000 symbols using 1-day data (fast!)
    """
    stocks = []
    etfs = []

    api_key = os.getenv('FINNHUB_API_KEY')
    if not api_key:
        print("❌ FINNHUB_API_KEY not found in .env")
        return [], []

    try:
        client = finnhub.Client(api_key=api_key)
        print("📡 Fetching ALL US symbols from Finnhub...", flush=True)
        us_symbols = client.stock_symbols('US')

        for sym in us_symbols:
            symbol = sym.get('displaySymbol', sym.get('symbol'))
            sym_type = sym.get('type', '')
            exchange = sym.get('mic', '')

            # Filter for major exchanges only
            if exchange not in ['XNAS', 'XNYS', 'XASE', 'ARCX']:
                continue

            # Collect all stocks and ETFs (no limits!)
            if sym_type == 'Common Stock':
                stocks.append(symbol)
            elif sym_type in ['ETP', 'ETF']:
                etfs.append(symbol)

        print(f"   ✅ Found {len(stocks)} stocks, {len(etfs)} ETFs from major exchanges")
        print(f"   Total to rank: {len(stocks) + len(etfs)} symbols")
    except Exception as e:
        print(f"   ❌ Finnhub fetch failed: {e}")
        return [], []

    return stocks, etfs

def rank_symbols(symbols, output_file, symbol_type='Stock'):
    """
    Fetch volume and market cap for symbols, rank them

    Args:
        symbols: List of ticker symbols
        output_file: Path to save CSV
        symbol_type: 'Stock' or 'ETF'
    """
    print(f"\n📊 Ranking {len(symbols)} {symbol_type}s...", flush=True)
    est_minutes = len(symbols) // 60
    print(f"   Estimated time: ~{est_minutes} minutes (using 1-day data for speed)", flush=True)
    print(f"   Rate limit: 60 symbols/min (Yahoo Finance free tier)", flush=True)

    results = []
    failed = 0
    start_time = time.time()

    for i, symbol in enumerate(symbols, 1):
        # Rate limit: ~1 per second (conservative)
        if i > 1:
            time.sleep(1.0)

        # Progress (every 100 symbols)
        if i % 100 == 0:
            elapsed = time.time() - start_time
            rate = i / elapsed * 60  # symbols per minute
            remaining = (len(symbols) - i) / rate
            print(f"   Progress: {i}/{len(symbols)} ({i*100//len(symbols)}%) | "
                  f"Rate: {rate:.1f}/min | ETA: {remaining:.1f} min | Failed: {failed}", flush=True)

        try:
            ticker = yf.Ticker(symbol)

            # Get TODAY's data only (1d = MUCH faster than 5d)
            hist = ticker.history(period='1d')
            if hist.empty:
                failed += 1
                continue

            # Get info (for market cap)
            info = ticker.info

            results.append({
                'symbol': symbol,
                'volume': int(hist['Volume'].iloc[-1]),
                'avg_volume': int(info.get('averageVolume', 0)),
                'market_cap': float(info.get('marketCap', 0)),
                'price': float(hist['Close'].iloc[-1])
            })

        except Exception as e:
            failed += 1
            if 'Rate limited' in str(e):
                print(f"   ⚠️  Rate limited at symbol {i}, sleeping 60s...")
                time.sleep(60)
                # Retry this symbol
                try:
                    ticker = yf.Ticker(symbol)
                    hist = ticker.history(period='5d')
                    if not hist.empty:
                        info = ticker.info
                        results.append({
                            'symbol': symbol,
                            'volume': int(hist['Volume'].iloc[-1]),
                            'avg_volume': int(info.get('averageVolume', 0)),
                            'market_cap': float(info.get('marketCap', 0)),
                            'price': float(hist['Close'].iloc[-1])
                        })
                        failed -= 1
                except:
                    pass
            continue

    # Create DataFrame
    if not results:
        print(f"   ❌ No data fetched for {symbol_type}s")
        return

    df = pd.DataFrame(results)

    # Sort by volume (primary), then market cap (secondary)
    df = df.sort_values(['volume', 'market_cap'], ascending=[False, False])
    df['rank'] = range(1, len(df) + 1)

    # Save
    df.to_csv(output_file, index=False)

    # Final stats
    total_time = time.time() - start_time
    actual_rate = len(df) / total_time * 60

    print(f"\n✅ Ranked {len(df)} {symbol_type}s")
    print(f"   Failed: {failed}")
    print(f"   Time: {total_time/60:.1f} minutes")
    print(f"   Rate: {actual_rate:.1f} symbols/min")
    print(f"   Saved to: {output_file}")
    print(f"\n   Top 10 {symbol_type}s by volume:")
    print(df.head(10)[['rank', 'symbol', 'volume', 'market_cap']].to_string(index=False))

def main():
    """Main entry point"""
    import sys

    print("="*80)
    print("NIGHTLY SYMBOL RANKING")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)

    # Check for test mode
    test_mode = '--test' in sys.argv
    if test_mode:
        print("🧪 TEST MODE: Processing only 20 stocks and 10 ETFs")

    # Get symbols
    stocks, etfs = get_all_us_symbols()

    if not stocks and not etfs:
        print("❌ No symbols fetched, exiting")
        return

    # Limit for test mode
    if test_mode:
        stocks = stocks[:20]
        etfs = etfs[:10]

    # Rank stocks
    stock_file = METADATA_DIR / 'ranked_stocks.csv'
    if stocks:
        rank_symbols(stocks, stock_file, 'Stock')

    # Rank ETFs
    etf_file = METADATA_DIR / 'ranked_etfs.csv'
    if etfs:
        rank_symbols(etfs, etf_file, 'ETF')

    print("\n" + "="*80)
    print("RANKING COMPLETE")
    print(f"Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    print("\n📁 Output files:")
    print(f"   Stocks: {stock_file}")
    print(f"   ETFs:   {etf_file}")

    # Show that files exist and have data
    if stock_file.exists():
        df = pd.read_csv(stock_file)
        print(f"   ✅ Stocks: {len(df)} symbols ranked")
    if etf_file.exists():
        df = pd.read_csv(etf_file)
        print(f"   ✅ ETFs: {len(df)} symbols ranked")

if __name__ == '__main__':
    main()
