#!/usr/bin/env python3
"""
ONE-TIME INITIAL BULK FETCH

Downloads 2 years of historical data for ALL 23,888 US symbols.
Run this ONCE overnight, then use incremental updates daily.

After this completes:
- All symbols will have CSVs with 2 years of data
- Master scanner can use volume from CSVs to sort intelligently
- Daily updates will be FAST (only fetch latest day)

Usage:
    python scripts/initial_bulk_fetch.py [--resume]
"""

import pandas as pd
import yfinance as yf
from pathlib import Path
from tqdm import tqdm
import time
import argparse
from datetime import datetime

# Directories
METADATA_DIR = Path('data/metadata')
STOCK_DIR = Path('data/market_data/stocks')
ETF_DIR = Path('data/market_data/etfs')

def get_csv_path(symbol: str, asset_type: str) -> Path:
    """Get CSV path for a symbol."""
    if asset_type.lower() == 'etf':
        return ETF_DIR / f"{symbol}.csv"
    else:
        return STOCK_DIR / f"{symbol}.csv"

def fetch_and_save(symbol: str, asset_type: str) -> bool:
    """
    Fetch 2 years of data for a symbol and save to CSV.
    Returns True if successful, False otherwise.
    """
    try:
        csv_path = get_csv_path(symbol, asset_type)
        
        # Skip if already exists (for resume functionality)
        if csv_path.exists():
            return True
        
        # Fetch 2 years of data
        ticker = yf.Ticker(symbol)
        df = ticker.history(period='2y')
        
        if df.empty:
            return False
        
        # Round to 2 decimals for prices, 0 for volume
        df = df.round({
            "Open": 2, "High": 2, "Low": 2, "Close": 2,
            "Volume": 0, "Dividends": 2, "Stock Splits": 2, "Capital Gains": 2
        })
        
        # Sort descending (newest first)
        df = df.sort_index(ascending=False)
        
        # Save
        csv_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(csv_path)
        
        return True
        
    except Exception as e:
        return False

def main():
    parser = argparse.ArgumentParser(description='Initial bulk fetch of all US symbols')
    parser.add_argument('--resume', action='store_true', 
                       help='Skip symbols that already have CSVs')
    args = parser.parse_args()
    
    print("=" * 80)
    print("INITIAL BULK FETCH - ALL US SYMBOLS")
    print("=" * 80)
    print()
    print("📥 This will download 2 years of data for ~23,888 symbols")
    print("⏱️  Estimated time: 6-8 hours (with rate limiting)")
    print("💾 Disk space needed: ~500 MB")
    print()
    
    if args.resume:
        print("🔄 RESUME MODE: Skipping symbols that already have CSVs\n")
    else:
        print("🆕 FRESH START: Downloading all symbols\n")
    
    input("Press ENTER to start (or Ctrl+C to cancel)...")
    print()
    
    # Load symbol list
    symbols_file = METADATA_DIR / 'all_us_symbols.csv'
    df_symbols = pd.read_csv(symbols_file)
    
    print(f"✅ Loaded {len(df_symbols)} symbols\n")
    
    # Track progress
    success_count = 0
    skip_count = 0
    fail_count = 0
    
    # Create progress file for resuming
    progress_file = METADATA_DIR / 'bulk_fetch_progress.txt'
    
    # Fetch all symbols with progress bar
    for i, row in enumerate(tqdm(df_symbols.itertuples(), 
                                  total=len(df_symbols), 
                                  desc="Fetching", 
                                  unit="symbol",
                                  ncols=100)):
        
        symbol = row.symbol
        asset_type = row.type
        
        # Check if already exists (for resume)
        csv_path = get_csv_path(symbol, asset_type)
        if args.resume and csv_path.exists():
            skip_count += 1
            continue
        
        # Fetch and save
        success = fetch_and_save(symbol, asset_type)
        
        if success:
            success_count += 1
        else:
            fail_count += 1
        
        # Rate limiting: 1 call per second (safe for Yahoo Finance)
        # This adds up to ~6.6 hours for 23,888 symbols
        if (i + 1) % 60 == 0:
            time.sleep(1)
            
            # Save progress every 100 symbols
            if (i + 1) % 100 == 0:
                with open(progress_file, 'w') as f:
                    f.write(f"Last processed: {symbol}\n")
                    f.write(f"Timestamp: {datetime.now()}\n")
                    f.write(f"Success: {success_count}\n")
                    f.write(f"Failed: {fail_count}\n")
                    f.write(f"Skipped: {skip_count}\n")
    
    # Final summary
    print("\n" + "=" * 80)
    print("BULK FETCH COMPLETE!")
    print("=" * 80)
    print(f"✅ Success: {success_count}")
    print(f"⏭️  Skipped: {skip_count}")
    print(f"❌ Failed: {fail_count}")
    print(f"📊 Total CSVs: {success_count + skip_count}")
    print()
    print("Next steps:")
    print("1. Run master scanner: python scripts/master_daily_scan.py --mode daily")
    print("2. System will now sort by volume from CSVs automatically")
    print("3. Daily updates will be FAST (incremental fetching)")
    print()
    
    # Clean up progress file
    if progress_file.exists():
        progress_file.unlink()

if __name__ == '__main__':
    main()

