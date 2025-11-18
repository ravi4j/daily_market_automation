"""
Fetch initial historical data for all symbols (organized by sector)
Run this ONCE, then daily updates are incremental (fast!)
"""

import os
import sys
import pandas as pd
import yfinance as yf
from pathlib import Path
from datetime import datetime, timedelta

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

METADATA_FILE = PROJECT_ROOT / 'data' / 'metadata' / 'symbol_metadata.csv'
DATA_DIR = PROJECT_ROOT / 'data' / 'market_data'


def load_metadata() -> pd.DataFrame:
    """Load symbol metadata"""
    if not METADATA_FILE.exists():
        print(f"❌ Metadata file not found: {METADATA_FILE}")
        print("   Run first: python scripts/fetch_symbol_metadata.py")
        sys.exit(1)
    
    df = pd.read_csv(METADATA_FILE)
    print(f"✅ Loaded metadata for {len(df)} symbols")
    return df


def fetch_initial_data(symbol: str, period: str = '2y') -> bool:
    """
    Fetch initial historical data for a symbol
    
    Args:
        symbol: Ticker symbol
        period: yfinance period ('1y', '2y', '5y', etc.)
    
    Returns:
        True if successful, False otherwise
    """
    csv_file = DATA_DIR / f'{symbol}.csv'
    
    # Skip if already exists
    if csv_file.exists():
        df = pd.read_csv(csv_file)
        print(f"   ⏭️  {symbol}: Already exists ({len(df)} rows)")
        return True
    
    try:
        print(f"   📥 {symbol}: Fetching {period} of data...")
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period)
        
        if df.empty:
            print(f"   ⚠️  {symbol}: No data available")
            return False
        
        # Save to CSV
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        df.to_csv(csv_file)
        print(f"   ✅ {symbol}: Saved {len(df)} rows")
        return True
    
    except Exception as e:
        print(f"   ❌ {symbol}: Error - {e}")
        return False


def fetch_by_sector(metadata_df: pd.DataFrame, period: str = '2y'):
    """Fetch data organized by sector"""
    
    sectors = metadata_df['sector'].unique()
    
    print(f"\n📊 Found {len(sectors)} sectors")
    print("="*80)
    
    total_success = 0
    total_failed = 0
    
    for sector in sorted(sectors):
        if sector == 'Unknown':
            continue
        
        symbols_in_sector = metadata_df[metadata_df['sector'] == sector]['symbol'].tolist()
        
        print(f"\n🏢 {sector} ({len(symbols_in_sector)} symbols)")
        print("-" * 60)
        
        for symbol in symbols_in_sector:
            success = fetch_initial_data(symbol, period)
            if success:
                total_success += 1
            else:
                total_failed += 1
    
    # Handle Unknown sector
    unknown_symbols = metadata_df[metadata_df['sector'] == 'Unknown']['symbol'].tolist()
    if unknown_symbols:
        print(f"\n❓ Unknown Sector ({len(unknown_symbols)} symbols)")
        print("-" * 60)
        for symbol in unknown_symbols:
            success = fetch_initial_data(symbol, period)
            if success:
                total_success += 1
            else:
                total_failed += 1
    
    return total_success, total_failed


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Fetch initial historical data')
    parser.add_argument('--period', default='2y', help='Period to fetch (default: 2y)')
    parser.add_argument('--force', action='store_true', help='Re-fetch even if exists')
    
    args = parser.parse_args()
    
    print("="*80)
    print("INITIAL SECTOR DATA FETCHER")
    print("="*80)
    
    # Load metadata
    print("\n📋 Loading symbol metadata...")
    metadata_df = load_metadata()
    
    # Fetch data by sector
    print(f"\n🔍 Fetching {args.period} of historical data...")
    success, failed = fetch_by_sector(metadata_df, args.period)
    
    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"✅ Successfully fetched: {success} symbols")
    print(f"❌ Failed: {failed} symbols")
    print(f"\nData directory: {DATA_DIR}")
    
    print("\n✅ INITIAL DATA FETCH COMPLETE!")
    print("\nNext steps:")
    print("1. Run daily updates: python src/fetch_daily_prices.py")
    print("2. Generate charts: python src/visualize_breakouts.py")
    print("3. Scan opportunities: python scripts/scan_by_sector.py")


if __name__ == '__main__':
    main()

