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
    python scripts/initial_bulk_fetch.py [--resume] [--workers N]
"""

import pandas as pd
import yfinance as yf
from pathlib import Path
from tqdm import tqdm
import time
import argparse
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

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

def fetch_and_save(symbol: str, asset_type: str, max_retries: int = 3, stats: dict = None) -> tuple:
    """
    Fetch 2 years of data for a symbol and save to CSV.
    Returns (success: bool, result_type: str, attempt_count: int, duration: float)
    Includes retry logic with exponential backoff.
    
    result_type: 'skipped', 'success', 'empty', 'rate_limit', 'error'
    """
    start_time = time.time()
    csv_path = get_csv_path(symbol, asset_type)
    
    # Skip if already exists (for resume functionality)
    if csv_path.exists():
        duration = time.time() - start_time
        return (True, 'skipped', 0, duration)
    
    # Retry logic with exponential backoff
    last_error = None
    for attempt in range(max_retries):
        try:
            # Add small delay to avoid rate limiting
            if attempt > 0:
                time.sleep(2 ** attempt)  # 2s, 4s, 8s
            
            # Fetch 2 years of data
            ticker = yf.Ticker(symbol)
            df = ticker.history(period='2y')
            
            if df.empty:
                # Empty data is not a retry-able error
                duration = time.time() - start_time
                return (False, 'empty', attempt + 1, duration)
            
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
            
            duration = time.time() - start_time
            return (True, 'success', attempt + 1, duration)
            
        except Exception as e:
            last_error = str(e)
            # Check if it's a rate limit error
            if 'Too Many Requests' in str(e) or '429' in str(e) or 'Rate limit' in str(e):
                result_type = 'rate_limit'
            else:
                result_type = 'error'
            
            # If it's the last attempt, return failure
            if attempt == max_retries - 1:
                duration = time.time() - start_time
                return (False, result_type, attempt + 1, duration)
            # Otherwise, continue to next retry
            continue
    
    duration = time.time() - start_time
    return (False, 'error', max_retries, duration)

def main():
    parser = argparse.ArgumentParser(description='Initial bulk fetch of all US symbols')
    parser.add_argument('--resume', action='store_true', 
                       help='Skip symbols that already have CSVs')
    parser.add_argument('--no-prompt', action='store_true',
                       help='Skip confirmation prompt (for CI/automation)')
    parser.add_argument('--workers', type=int, default=10,
                       help='Number of parallel workers (default: 10, max recommended: 20)')
    args = parser.parse_args()
    
    print("=" * 80)
    print("INITIAL BULK FETCH - ALL US SYMBOLS (PARALLEL)")
    print("=" * 80)
    print()
    print(f"📥 This will download 2 years of data for ~23,888 symbols")
    print(f"⚡ Using {args.workers} parallel workers")
    print(f"⏱️  Estimated time: 30-60 minutes (with parallel processing)")
    print(f"💾 Disk space needed: ~500 MB")
    print()
    
    if args.resume:
        print("🔄 RESUME MODE: Skipping symbols that already have CSVs\n")
    else:
        print("🆕 FRESH START: Downloading all symbols\n")
    
    # Skip prompt in CI/automation
    if not args.no_prompt:
        input("Press ENTER to start (or Ctrl+C to cancel)...")
    print()
    
    # Load symbol list
    symbols_file = METADATA_DIR / 'all_us_symbols.csv'
    df_symbols = pd.read_csv(symbols_file)
    
    print(f"✅ Loaded {len(df_symbols)} symbols\n")
    
    # Track progress and statistics (thread-safe)
    lock = threading.Lock()
    stats = {
        'success': 0,
        'skipped': 0,
        'empty': 0,
        'rate_limit': 0,
        'error': 0,
        'total_retries': 0,
        'total_duration': 0.0,
        'fetch_times': []
    }
    
    # Create progress file for resuming
    progress_file = METADATA_DIR / 'bulk_fetch_progress.txt'
    
    # Prepare symbols to fetch
    symbols_to_fetch = []
    for _, row in df_symbols.iterrows():
        symbol = row['symbol']
        asset_type = row['type']
        symbols_to_fetch.append((symbol, asset_type))
    
    print(f"📊 Symbols to process: {len(symbols_to_fetch)}\n")
    
    # Fetch symbols in parallel with progress bar
    def fetch_wrapper(symbol_info):
        symbol, asset_type = symbol_info
        success, result_type, attempts, duration = fetch_and_save(symbol, asset_type, stats=stats)
        return success, result_type, attempts, duration
    
    # Use ThreadPoolExecutor for parallel downloads
    start_time = time.time()
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        # Submit all tasks
        futures = {executor.submit(fetch_wrapper, sym_info): sym_info for sym_info in symbols_to_fetch}
        
        # Process results with progress bar
        with tqdm(total=len(futures), desc="Fetching", unit="symbol", ncols=100) as pbar:
            for i, future in enumerate(as_completed(futures)):
                symbol_info = futures[future]
                try:
                    success, result_type, attempts, duration = future.result()
                    
                    with lock:
                        # Update stats
                        stats[result_type] = stats.get(result_type, 0) + 1
                        stats['total_retries'] += (attempts - 1) if attempts > 0 else 0
                        stats['total_duration'] += duration
                        
                        # Track fetch times for rate calculation
                        if result_type in ['success', 'empty', 'rate_limit', 'error']:
                            stats['fetch_times'].append(duration)
                        
                        # Update progress bar with current stats
                        pbar.set_postfix({
                            'success': stats['success'],
                            'rate_limit': stats['rate_limit'],
                            'errors': stats['error']
                        })
                        
                except Exception as e:
                    with lock:
                        stats['error'] = stats.get('error', 0) + 1
                
                pbar.update(1)
                
                # Save progress every 500 symbols
                if (i + 1) % 500 == 0:
                    with lock:
                        elapsed = time.time() - start_time
                        avg_time_per_symbol = elapsed / (i + 1) if i > 0 else 0
                        remaining_symbols = len(futures) - i - 1
                        estimated_remaining = avg_time_per_symbol * remaining_symbols
                        
                        with open(progress_file, 'w') as f:
                            f.write(f"Timestamp: {datetime.now()}\n")
                            f.write(f"Progress: {i+1}/{len(futures)} ({100*(i+1)/len(futures):.1f}%)\n")
                            f.write(f"Success: {stats['success']}\n")
                            f.write(f"Skipped: {stats['skipped']}\n")
                            f.write(f"Empty: {stats['empty']}\n")
                            f.write(f"Rate Limited: {stats['rate_limit']}\n")
                            f.write(f"Errors: {stats['error']}\n")
                            f.write(f"Total Retries: {stats['total_retries']}\n")
                            f.write(f"Avg Time/Symbol: {avg_time_per_symbol:.2f}s\n")
                            f.write(f"Estimated Remaining: {estimated_remaining/60:.1f} minutes\n")
    
    # Calculate final statistics
    total_time = time.time() - start_time
    total_processed = len(symbols_to_fetch)
    total_csvs = stats['success'] + stats['skipped']
    avg_fetch_time = sum(stats['fetch_times']) / len(stats['fetch_times']) if stats['fetch_times'] else 0
    symbols_per_minute = (total_processed / total_time) * 60 if total_time > 0 else 0
    retry_rate = (stats['total_retries'] / total_processed) * 100 if total_processed > 0 else 0
    success_rate = (stats['success'] / (total_processed - stats['skipped'])) * 100 if (total_processed - stats['skipped']) > 0 else 0
    
    # Final summary
    print("\n" + "=" * 80)
    print("BULK FETCH COMPLETE!")
    print("=" * 80)
    print()
    print("📊 RESULTS:")
    print(f"   ✅ Successfully fetched: {stats['success']}")
    print(f"   ⏭️  Skipped (existing):  {stats['skipped']}")
    print(f"   📭 Empty data:           {stats['empty']}")
    print(f"   🚫 Rate limited:         {stats['rate_limit']}")
    print(f"   ❌ Other errors:         {stats['error']}")
    print(f"   📁 Total CSVs:           {total_csvs}")
    print()
    print("⚡ PERFORMANCE:")
    print(f"   ⏱️  Total time:           {total_time/60:.1f} minutes")
    print(f"   📈 Symbols/minute:       {symbols_per_minute:.1f}")
    print(f"   ⏲️  Avg fetch time:       {avg_fetch_time:.2f}s")
    print(f"   🔄 Total retries:        {stats['total_retries']}")
    print(f"   📊 Retry rate:           {retry_rate:.1f}%")
    print(f"   ✅ Success rate:         {success_rate:.1f}%")
    print()
    print("🎯 YAHOO FINANCE RATE LIMIT ANALYSIS:")
    if stats['rate_limit'] > 0:
        print(f"   ⚠️  Rate limit hits:     {stats['rate_limit']} ({stats['rate_limit']/total_processed*100:.1f}%)")
        print(f"   💡 Recommendation:       Reduce workers or add delays")
    else:
        print(f"   ✅ No rate limit issues detected")
        print(f"   💡 Performance:          {args.workers} workers working well")
    print()
    
    if stats['success'] > 0:
        print("Next steps:")
        print("1. Run master scanner: python scripts/master_daily_scan.py --mode daily")
        print("2. System will now sort by volume from CSVs automatically")
        print("3. Daily updates will be FAST (incremental fetching)")
    else:
        print("⚠️  No symbols were successfully fetched. Check:")
        print("1. Internet connection")
        print("2. Yahoo Finance service status")
        print("3. Try running with fewer workers: --workers 5")
    print()
    
    # Clean up progress file
    if progress_file.exists():
        progress_file.unlink()

if __name__ == '__main__':
    main()

