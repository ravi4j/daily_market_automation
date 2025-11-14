#!/usr/bin/env python3
"""
Add symbol to config/symbols.yaml
"""

import sys
import argparse
import yaml
from pathlib import Path


def add_symbol(symbol: str):
    """Add symbol to config if not already there"""
    
    symbol = symbol.upper()
    config_path = Path('config/symbols.yaml')
    
    if not config_path.exists():
        print(f"❌ Config file not found: {config_path}")
        return 1
    
    # Load config
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    symbols = config.get('symbols', {})
    
    # Check if already exists
    if symbol in symbols:
        print(f"ℹ️  {symbol} already in config")
        return 0
    
    # Check for special indices
    if symbol.startswith('^'):
        # Index symbol, keep as-is
        key = symbol.replace('^', '').upper()
        symbols[key] = symbol
    else:
        # Regular symbol
        symbols[symbol] = symbol
    
    config['symbols'] = symbols
    
    # Save with nice formatting
    with open(config_path, 'w') as f:
        # Write header comments
        f.write("# Portfolio Symbols Configuration\n")
        f.write("# Add or remove symbols here to track your positions\n")
        f.write("# Format: symbol_key: ticker_symbol\n")
        f.write("\n")
        f.write("symbols:\n")
        for key, value in symbols.items():
            f.write(f"  {key}: {value}\n")
    
    print(f"✅ Added {symbol} to config/symbols.yaml")
    return 0


def main():
    parser = argparse.ArgumentParser(description='Add symbol to config')
    parser.add_argument('--symbol', required=True, help='Symbol to add')
    args = parser.parse_args()
    
    return add_symbol(args.symbol)


if __name__ == "__main__":
    sys.exit(main())

