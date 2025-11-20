#!/usr/bin/env python3
"""
Sort all US symbols by trading volume for intelligent selection.

This creates a volume-sorted list so major stocks (NVDA, ORCL, AAPL, etc.)
are prioritized in the daily scanner.

Strategy:
1. Load existing CSVs → calculate avg volume
2. For symbols without CSVs → fetch 1 day data to get volume
3. Sort all by volume → save to all_us_symbols.csv

This runs ONCE to create a properly sorted symbol universe.
"""

import pandas as pd
import yfinance as yf
from pathlib import Path
from tqdm import tqdm
import time

def get_volume_from_csv(csv_path: Path) -> float:
    """Get average volume from existing CSV."""
    try:
        df = pd.read_csv(csv_path)
        if 'Volume' in df.columns:
            return df['Volume'].mean()
    except:
        pass
    return 0

def get_volume_from_yahoo(symbol: str) -> float:
    """Fetch 1 day data from Yahoo to get volume."""
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period='5d')  # 5 days to ensure we get data
        if not hist.empty and 'Volume' in hist.columns:
            return hist['Volume'].mean()
    except:
        pass
    return 0

def main():
    print("📊 Sorting all US symbols by trading volume...\n")
    
    # Load current symbol list
    symbols_file = Path('data/metadata/all_us_symbols.csv')
    df_symbols = pd.read_csv(symbols_file)
    
    print(f"✅ Loaded {len(df_symbols)} symbols\n")
    
    # Add volume column
    df_symbols['avg_volume'] = 0.0
    
    # Step 1: Get volumes from existing CSVs (fast)
    print("Step 1: Getting volumes from existing CSVs...")
    stock_dir = Path('data/market_data/stocks')
    etf_dir = Path('data/market_data/etfs')
    
    csv_volumes = {}
    for csv_file in list(stock_dir.glob('*.csv')) + list(etf_dir.glob('*.csv')):
        symbol = csv_file.stem
        volume = get_volume_from_csv(csv_file)
        if volume > 0:
            csv_volumes[symbol] = volume
    
    print(f"   ✅ Found volumes for {len(csv_volumes)} symbols from CSVs\n")
    
    # Update dataframe with CSV volumes
    for symbol, volume in csv_volumes.items():
        df_symbols.loc[df_symbols['symbol'] == symbol, 'avg_volume'] = volume
    
    # Step 2: Fetch volumes for symbols without CSVs (slow, with rate limiting)
    symbols_without_volume = df_symbols[df_symbols['avg_volume'] == 0]['symbol'].tolist()
    
    print(f"Step 2: Fetching volumes for {len(symbols_without_volume)} remaining symbols...")
    print(f"   (This will take ~{len(symbols_without_volume) // 60} minutes with rate limiting)\n")
    
    # Fetch in batches with progress bar
    for i, symbol in enumerate(tqdm(symbols_without_volume, desc="   Fetching", unit="symbol", ncols=100)):
        volume = get_volume_from_yahoo(symbol)
        df_symbols.loc[df_symbols['symbol'] == symbol, 'avg_volume'] = volume
        
        # Rate limiting: 1 call per second (safe for Yahoo)
        if (i + 1) % 60 == 0:
            time.sleep(1)
    
    print(f"\n✅ Fetched volumes for all symbols\n")
    
    # Step 3: Sort by volume (descending)
    print("Step 3: Sorting by volume...")
    df_symbols = df_symbols.sort_values('avg_volume', ascending=False)
    
    # Step 4: Save sorted list
    print("Step 4: Saving sorted symbol list...")
    df_symbols.to_csv(symbols_file, index=False)
    
    print(f"\n✅ All done! Symbols sorted by volume\n")
    print("Top 20 symbols by volume:")
    print(df_symbols[['symbol', 'name', 'type', 'avg_volume']].head(20).to_string(index=False))
    
    print(f"\n🎯 Major stocks now prioritized:")
    for sym in ['NVDA', 'ORCL', 'AAPL', 'TSLA', 'MSFT', 'AMZN']:
        row = df_symbols[df_symbols['symbol'] == sym]
        if not row.empty:
            pos = df_symbols.index.get_loc(row.index[0]) + 1
            volume = row['avg_volume'].values[0]
            print(f"   {sym}: Position #{pos} (avg volume: {volume:,.0f})")

if __name__ == '__main__':
    main()

