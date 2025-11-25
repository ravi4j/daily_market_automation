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
    Get symbols to rank
    Strategy: Use base universe (major stocks/ETFs) + add more from Finnhub
    This ensures we always include NVDA, AAPL, etc.
    """

    # Load base universe (curated list of important symbols)
    base_file = METADATA_DIR / 'base_universe.txt'
    stocks = []
    etfs = []

    if base_file.exists():
        print("📋 Loading base universe...", flush=True)
        with open(base_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    if '|' in line:
                        symbol, sym_type = line.split('|')
                        if sym_type == 'stock':
                            stocks.append(symbol)
                        elif sym_type == 'etf':
                            etfs.append(symbol)
        print(f"   Base: {len(stocks)} stocks, {len(etfs)} ETFs")

    # Add more symbols from Finnhub (up to 500 total each)
    api_key = os.getenv('FINNHUB_API_KEY')
    if api_key:
        try:
            client = finnhub.Client(api_key=api_key)
            print("📡 Fetching additional symbols from Finnhub...", flush=True)
            us_symbols = client.stock_symbols('US')

            for sym in us_symbols:
                symbol = sym.get('displaySymbol', sym.get('symbol'))
                sym_type = sym.get('type', '')
                exchange = sym.get('mic', '')

                # Filter for major exchanges
                if exchange not in ['XNAS', 'XNYS', 'XASE', 'ARCX']:
                    continue

                # Add if not already in base list and under limit
                if sym_type == 'Common Stock' and symbol not in stocks and len(stocks) < 500:
                    stocks.append(symbol)
                elif sym_type in ['ETP', 'ETF'] and symbol not in etfs and len(etfs) < 200:
                    etfs.append(symbol)

            print(f"   Added from Finnhub: {len(stocks)} stocks, {len(etfs)} ETFs total")
        except Exception as e:
            print(f"   ⚠️  Finnhub fetch failed: {e}")

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
    print(f"   This will take ~{len(symbols)//60} minutes (rate limited to 60/min)", flush=True)

    results = []
    failed = 0

    for i, symbol in enumerate(symbols, 1):
        # Rate limit: ~1 per second
        if i > 1:
            time.sleep(1.1)

        # Progress
        if i % 100 == 0:
            print(f"   Progress: {i}/{len(symbols)} ({i*100//len(symbols)}%)")

        try:
            ticker = yf.Ticker(symbol)

            # Get recent volume
            hist = ticker.history(period='5d')
            if hist.empty:
                failed += 1
                continue

            # Get info
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

    print(f"\n✅ Ranked {len(df)} {symbol_type}s")
    print(f"   Failed: {failed}")
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
