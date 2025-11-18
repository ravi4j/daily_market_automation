"""
Fetch symbol metadata (exchange, sector, industry) and store as CSV
Run this ONCE initially, then it updates incrementally
"""

import os
import sys
import pandas as pd
import yfinance as yf
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

DATA_DIR = PROJECT_ROOT / 'data' / 'metadata'
METADATA_FILE = DATA_DIR / 'symbol_metadata.csv'


def fetch_symbol_metadata(symbol: str) -> dict:
    """
    Fetch complete metadata for a symbol
    
    Returns:
    {
        'symbol': 'AAPL',
        'company_name': 'Apple Inc.',
        'exchange': 'NMS (NASDAQ)',
        'sector': 'Technology',
        'industry': 'Consumer Electronics',
        'market_cap': 2800000000000,
        'country': 'United States',
        'currency': 'USD',
        'last_updated': '2024-11-18'
    }
    """
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        return {
            'symbol': symbol,
            'company_name': info.get('longName', info.get('shortName', symbol)),
            'exchange': info.get('exchange', 'Unknown'),
            'exchange_full': info.get('fullExchangeName', 'Unknown'),
            'sector': info.get('sector', 'Unknown'),
            'industry': info.get('industry', 'Unknown'),
            'market_cap': info.get('marketCap', 0),
            'country': info.get('country', 'Unknown'),
            'currency': info.get('currency', 'USD'),
            'quote_type': info.get('quoteType', 'EQUITY'),  # EQUITY, ETF, INDEX
            'last_updated': datetime.now().strftime('%Y-%m-%d')
        }
    
    except Exception as e:
        print(f"   ⚠️  Error fetching {symbol}: {e}")
        return {
            'symbol': symbol,
            'company_name': symbol,
            'exchange': 'Unknown',
            'exchange_full': 'Unknown',
            'sector': 'Unknown',
            'industry': 'Unknown',
            'market_cap': 0,
            'country': 'Unknown',
            'currency': 'USD',
            'quote_type': 'EQUITY',
            'last_updated': datetime.now().strftime('%Y-%m-%d')
        }


def load_existing_metadata() -> pd.DataFrame:
    """Load existing metadata CSV if it exists"""
    if METADATA_FILE.exists():
        df = pd.read_csv(METADATA_FILE)
        print(f"✅ Loaded {len(df)} existing symbols from metadata")
        return df
    else:
        print("ℹ️  No existing metadata found, will create new")
        return pd.DataFrame()


def fetch_all_metadata(symbols: list, force_refresh: bool = False) -> pd.DataFrame:
    """
    Fetch metadata for all symbols
    
    Args:
        symbols: List of ticker symbols
        force_refresh: If True, re-fetch even if exists
    
    Returns:
        DataFrame with all metadata
    """
    existing_df = load_existing_metadata()
    
    metadata_list = []
    
    for symbol in symbols:
        # Skip if already exists and not forcing refresh
        if not force_refresh and not existing_df.empty:
            if symbol in existing_df['symbol'].values:
                print(f"   ⏭️  {symbol}: Using cached metadata")
                existing_row = existing_df[existing_df['symbol'] == symbol].iloc[0].to_dict()
                metadata_list.append(existing_row)
                continue
        
        print(f"   🔍 Fetching {symbol}...")
        metadata = fetch_symbol_metadata(symbol)
        metadata_list.append(metadata)
    
    df = pd.DataFrame(metadata_list)
    return df


def save_metadata(df: pd.DataFrame):
    """Save metadata to CSV"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(METADATA_FILE, index=False)
    print(f"\n✅ Saved {len(df)} symbols to {METADATA_FILE}")


def print_summary(df: pd.DataFrame):
    """Print summary by sector and exchange"""
    print("\n" + "="*80)
    print("SYMBOL METADATA SUMMARY")
    print("="*80)
    
    print(f"\nTotal Symbols: {len(df)}")
    
    # By Exchange
    print("\n📍 BY EXCHANGE:")
    exchange_counts = df['exchange'].value_counts()
    for exchange, count in exchange_counts.items():
        print(f"   {exchange}: {count} symbols")
    
    # By Sector
    print("\n🏢 BY SECTOR:")
    sector_counts = df['sector'].value_counts()
    for sector, count in sector_counts.items():
        symbols_in_sector = df[df['sector'] == sector]['symbol'].tolist()
        print(f"   {sector}: {count} symbols ({', '.join(symbols_in_sector[:5])}{'...' if count > 5 else ''})")
    
    # By Quote Type
    print("\n📊 BY TYPE:")
    type_counts = df['quote_type'].value_counts()
    for qtype, count in type_counts.items():
        print(f"   {qtype}: {count}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Fetch symbol metadata')
    parser.add_argument('--symbols', nargs='+', help='Symbols to fetch (default: load from config)')
    parser.add_argument('--force', action='store_true', help='Force refresh all metadata')
    parser.add_argument('--sp500', action='store_true', help='Fetch all S&P 500 symbols')
    
    args = parser.parse_args()
    
    print("="*80)
    print("SYMBOL METADATA FETCHER")
    print("="*80)
    
    # Determine which symbols to fetch
    if args.sp500:
        print("\n📊 Fetching S&P 500 symbols...")
        sp500_file = PROJECT_ROOT / 'data' / 'metadata' / 'sp500_symbols.json'
        if sp500_file.exists():
            import json
            with open(sp500_file) as f:
                sp500_data = json.load(f)
                symbols = [item['symbol'] for item in sp500_data.get('symbols', [])]
            print(f"   Loaded {len(symbols)} symbols from S&P 500 list")
        else:
            print("   ⚠️  S&P 500 list not found, run: python scripts/fetch_sp500_list.py")
            return
    
    elif args.symbols:
        symbols = args.symbols
        print(f"\n📊 Fetching metadata for: {', '.join(symbols)}")
    
    else:
        # Load from config/symbols.yaml
        import yaml
        config_file = PROJECT_ROOT / 'config' / 'symbols.yaml'
        if config_file.exists():
            with open(config_file) as f:
                config = yaml.safe_load(f)
                symbols = list(config.get('symbols', {}).values())
            print(f"\n📊 Fetching metadata for {len(symbols)} symbols from config")
        else:
            print("⚠️  No symbols specified. Use --symbols or --sp500")
            return
    
    # Fetch metadata
    print(f"\n🔍 Fetching metadata (force_refresh={args.force})...\n")
    df = fetch_all_metadata(symbols, force_refresh=args.force)
    
    # Save to CSV
    save_metadata(df)
    
    # Print summary
    print_summary(df)
    
    print("\n" + "="*80)
    print("✅ COMPLETE!")
    print("="*80)
    print(f"\nMetadata saved to: {METADATA_FILE}")
    print("\nNext steps:")
    print("1. Review: cat data/metadata/symbol_metadata.csv")
    print("2. Fetch initial data: python scripts/fetch_initial_sector_data.py")
    print("3. Run daily updates: python src/fetch_daily_prices.py")


if __name__ == '__main__':
    main()

