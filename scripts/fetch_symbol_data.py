#!/usr/bin/env python3
"""
Fetch historical data for a specific symbol
Creates or updates CSV file in data/market_data/
"""

import sys
import argparse
from pathlib import Path
import yfinance as yf
import pandas as pd


def fetch_symbol_data(symbol: str, period: str = '2y', force: bool = False):
    """
    Fetch and save historical data for a symbol
    
    Args:
        symbol: Stock symbol (e.g., 'NVDA', 'AAPL')
        period: Time period ('1y', '2y', '5y', 'max')
        force: Force re-download even if CSV exists
    
    Returns:
        Path to CSV file if successful, None otherwise
    """
    PROJECT_ROOT = Path(__file__).parent.parent
    data_dir = PROJECT_ROOT / "data" / "market_data"
    data_dir.mkdir(parents=True, exist_ok=True)
    
    csv_path = data_dir / f"{symbol}.csv"
    
    # Check if already exists
    if csv_path.exists() and not force:
        print(f"✅ {symbol}.csv already exists")
        print(f"   Use --force to re-download")
        return csv_path
    
    print(f"📥 Fetching {period} of data for {symbol}...")
    
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period)
        
        if df.empty:
            print(f"❌ No data found for {symbol}")
            print(f"   Check if symbol is valid")
            return None
        
        # Ensure standard column names
        df.columns = df.columns.str.title()
        df.index.name = 'Date'
        
        # Save to CSV
        df.to_csv(csv_path)
        
        print(f"✅ Saved {len(df)} days of data")
        print(f"   File: {csv_path}")
        print(f"   Date range: {df.index[0].date()} to {df.index[-1].date()}")
        
        return csv_path
        
    except Exception as e:
        print(f"❌ Error fetching data: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(
        description='Fetch historical data for a symbol',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/fetch_symbol_data.py NVDA
  python scripts/fetch_symbol_data.py AAPL --period 5y
  python scripts/fetch_symbol_data.py TSLA --force
        """
    )
    
    parser.add_argument(
        'symbol',
        type=str,
        help='Stock symbol (e.g., NVDA, AAPL, TSLA)'
    )
    
    parser.add_argument(
        '--period',
        type=str,
        default='2y',
        choices=['1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'max'],
        help='Time period to fetch (default: 2y)'
    )
    
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force re-download even if CSV exists'
    )
    
    args = parser.parse_args()
    
    # Fetch data
    result = fetch_symbol_data(
        symbol=args.symbol.upper(),
        period=args.period,
        force=args.force
    )
    
    if result:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()

