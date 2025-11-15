#!/usr/bin/env python3
"""
Fetch current S&P 500 constituents list
Priority: Finnhub API -> Wikipedia -> File fallback
"""

import pandas as pd
import json
import os
import sys
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


def fetch_from_finnhub():
    """Fetch S&P 500 list from Finnhub API"""
    try:
        from src.finnhub_data import FinnhubClient

        print("📡 Trying Finnhub API (primary source)...")
        client = FinnhubClient()
        sp500_data = client.fetch_sp500_list()

        print(f"✅ Fetched {len(sp500_data)} stocks from Finnhub")
        return sp500_data, 'finnhub'

    except ImportError:
        print("⚠️  finnhub-python not installed")
        return None, None
    except ValueError as e:
        print(f"⚠️  Finnhub API key not found: {e}")
        return None, None
    except Exception as e:
        print(f"⚠️  Finnhub API failed: {e}")
        return None, None


def fetch_from_wikipedia():
    """Fetch S&P 500 symbols from Wikipedia"""
    try:
        print("📡 Trying Wikipedia (secondary source)...")
        import requests
        from io import StringIO

        url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        response = requests.get(url, headers=headers)
        response.raise_for_status()

        tables = pd.read_html(StringIO(response.text))
        sp500_table = tables[0]

        # Extract symbols and company names
        symbols = sp500_table['Symbol'].tolist()
        companies = sp500_table['Security'].tolist()
        sectors = sp500_table['GICS Sector'].tolist()

        # Create a dict mapping symbol to company info
        sp500_data = []
        for symbol, company, sector in zip(symbols, companies, sectors):
            # Clean up symbol (some have dots which need to be replaced)
            clean_symbol = symbol.replace('.', '-')
            sp500_data.append({
                'symbol': clean_symbol,
                'company': company,
                'sector': sector
            })

        print(f"✅ Fetched {len(sp500_data)} S&P 500 symbols from Wikipedia")
        return sp500_data, 'wikipedia'

    except Exception as e:
        print(f"⚠️  Could not fetch from Wikipedia: {e}")
        return None, None


def fetch_sp500_symbols():
    """
    Fetch S&P 500 symbols with priority fallback:
    1. Finnhub API (most comprehensive, but not exact S&P 500)
    2. Wikipedia (accurate S&P 500 list)
    3. File fallback (static comprehensive list)
    """
    # Try Finnhub first
    sp500_data, source = fetch_from_finnhub()
    if sp500_data:
        return sp500_data, source

    # Try Wikipedia second
    sp500_data, source = fetch_from_wikipedia()
    if sp500_data:
        return sp500_data, source

    # Fall back to file
    print("📦 Using comprehensive fallback list (file)...")
    sp500_data = load_comprehensive_list()
    return sp500_data, 'file'


def load_comprehensive_list():
    """Load comprehensive S&P 500 list from file"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    comprehensive_file = os.path.join(project_root, 'data', 'sp500_comprehensive.txt')

    if os.path.exists(comprehensive_file):
        sp500_data = []
        with open(comprehensive_file, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                parts = line.split(',')
                if len(parts) >= 3:
                    sp500_data.append({
                        'symbol': parts[0].strip(),
                        'company': parts[1].strip(),
                        'sector': parts[2].strip()
                    })
        print(f"✅ Loaded {len(sp500_data)} stocks from comprehensive list")
        return sp500_data
    else:
        # Fallback to inline list if file doesn't exist
        return get_inline_fallback_list()


def get_inline_fallback_list():
    """Inline fallback list if file is missing"""
    fallback_list = [
        # Information Technology
        {'symbol': 'AAPL', 'company': 'Apple Inc.', 'sector': 'Information Technology'},
        {'symbol': 'MSFT', 'company': 'Microsoft Corporation', 'sector': 'Information Technology'},
        {'symbol': 'NVDA', 'company': 'NVIDIA Corporation', 'sector': 'Information Technology'},
        {'symbol': 'AVGO', 'company': 'Broadcom Inc.', 'sector': 'Information Technology'},
        {'symbol': 'ORCL', 'company': 'Oracle Corporation', 'sector': 'Information Technology'},
        {'symbol': 'CSCO', 'company': 'Cisco Systems Inc.', 'sector': 'Information Technology'},
        {'symbol': 'ADBE', 'company': 'Adobe Inc.', 'sector': 'Information Technology'},
        {'symbol': 'CRM', 'company': 'Salesforce Inc.', 'sector': 'Information Technology'},
        {'symbol': 'AMD', 'company': 'Advanced Micro Devices Inc.', 'sector': 'Information Technology'},
        {'symbol': 'INTC', 'company': 'Intel Corporation', 'sector': 'Information Technology'},
        {'symbol': 'QCOM', 'company': 'QUALCOMM Incorporated', 'sector': 'Information Technology'},
        {'symbol': 'TXN', 'company': 'Texas Instruments Incorporated', 'sector': 'Information Technology'},
        {'symbol': 'NOW', 'company': 'ServiceNow Inc.', 'sector': 'Information Technology'},
        {'symbol': 'INTU', 'company': 'Intuit Inc.', 'sector': 'Information Technology'},
        {'symbol': 'AMAT', 'company': 'Applied Materials Inc.', 'sector': 'Information Technology'},
        {'symbol': 'MU', 'company': 'Micron Technology Inc.', 'sector': 'Information Technology'},
        {'symbol': 'LRCX', 'company': 'Lam Research Corporation', 'sector': 'Information Technology'},
        {'symbol': 'KLAC', 'company': 'KLA Corporation', 'sector': 'Information Technology'},
        {'symbol': 'SNPS', 'company': 'Synopsys Inc.', 'sector': 'Information Technology'},
        {'symbol': 'CDNS', 'company': 'Cadence Design Systems Inc.', 'sector': 'Information Technology'},
        {'symbol': 'PANW', 'company': 'Palo Alto Networks Inc.', 'sector': 'Information Technology'},
        {'symbol': 'ADSK', 'company': 'Autodesk Inc.', 'sector': 'Information Technology'},
        {'symbol': 'FTNT', 'company': 'Fortinet Inc.', 'sector': 'Information Technology'},
        {'symbol': 'ADP', 'company': 'Automatic Data Processing Inc.', 'sector': 'Information Technology'},

        # Communication Services
        {'symbol': 'GOOGL', 'company': 'Alphabet Inc. (Class A)', 'sector': 'Communication Services'},
        {'symbol': 'GOOG', 'company': 'Alphabet Inc. (Class C)', 'sector': 'Communication Services'},
        {'symbol': 'META', 'company': 'Meta Platforms Inc.', 'sector': 'Communication Services'},
        {'symbol': 'NFLX', 'company': 'Netflix Inc.', 'sector': 'Communication Services'},
        {'symbol': 'DIS', 'company': 'The Walt Disney Company', 'sector': 'Communication Services'},
        {'symbol': 'CMCSA', 'company': 'Comcast Corporation', 'sector': 'Communication Services'},
        {'symbol': 'T', 'company': 'AT&T Inc.', 'sector': 'Communication Services'},
        {'symbol': 'VZ', 'company': 'Verizon Communications Inc.', 'sector': 'Communication Services'},
        {'symbol': 'TMUS', 'company': 'T-Mobile US Inc.', 'sector': 'Communication Services'},

        # Consumer Discretionary
        {'symbol': 'AMZN', 'company': 'Amazon.com Inc.', 'sector': 'Consumer Discretionary'},
        {'symbol': 'TSLA', 'company': 'Tesla Inc.', 'sector': 'Consumer Discretionary'},
        {'symbol': 'HD', 'company': 'The Home Depot Inc.', 'sector': 'Consumer Discretionary'},
        {'symbol': 'MCD', 'company': "McDonald's Corporation", 'sector': 'Consumer Discretionary'},
        {'symbol': 'NKE', 'company': 'NIKE Inc.', 'sector': 'Consumer Discretionary'},
        {'symbol': 'SBUX', 'company': 'Starbucks Corporation', 'sector': 'Consumer Discretionary'},
        {'symbol': 'LOW', 'company': "Lowe's Companies Inc.", 'sector': 'Consumer Discretionary'},
        {'symbol': 'TJX', 'company': 'The TJX Companies Inc.', 'sector': 'Consumer Discretionary'},
        {'symbol': 'BKNG', 'company': 'Booking Holdings Inc.', 'sector': 'Consumer Discretionary'},
        {'symbol': 'ABNB', 'company': 'Airbnb Inc.', 'sector': 'Consumer Discretionary'},
        {'symbol': 'GM', 'company': 'General Motors Company', 'sector': 'Consumer Discretionary'},
        {'symbol': 'F', 'company': 'Ford Motor Company', 'sector': 'Consumer Discretionary'},

        # Financials
        {'symbol': 'BRK.B', 'company': 'Berkshire Hathaway Inc. (Class B)', 'sector': 'Financials'},
        {'symbol': 'JPM', 'company': 'JPMorgan Chase & Co.', 'sector': 'Financials'},
        {'symbol': 'V', 'company': 'Visa Inc.', 'sector': 'Financials'},
        {'symbol': 'MA', 'company': 'Mastercard Incorporated', 'sector': 'Financials'},
        {'symbol': 'BAC', 'company': 'Bank of America Corporation', 'sector': 'Financials'},
        {'symbol': 'WFC', 'company': 'Wells Fargo & Company', 'sector': 'Financials'},
        {'symbol': 'C', 'company': 'Citigroup Inc.', 'sector': 'Financials'},
        {'symbol': 'MS', 'company': 'Morgan Stanley', 'sector': 'Financials'},
        {'symbol': 'GS', 'company': 'The Goldman Sachs Group Inc.', 'sector': 'Financials'},
        {'symbol': 'BLK', 'company': 'BlackRock Inc.', 'sector': 'Financials'},
        {'symbol': 'SCHW', 'company': 'The Charles Schwab Corporation', 'sector': 'Financials'},
        {'symbol': 'AXP', 'company': 'American Express Company', 'sector': 'Financials'},
        {'symbol': 'SPGI', 'company': 'S&P Global Inc.', 'sector': 'Financials'},
        {'symbol': 'CB', 'company': 'Chubb Limited', 'sector': 'Financials'},

        # Health Care
        {'symbol': 'UNH', 'company': 'UnitedHealth Group Incorporated', 'sector': 'Health Care'},
        {'symbol': 'JNJ', 'company': 'Johnson & Johnson', 'sector': 'Health Care'},
        {'symbol': 'LLY', 'company': 'Eli Lilly and Company', 'sector': 'Health Care'},
        {'symbol': 'ABBV', 'company': 'AbbVie Inc.', 'sector': 'Health Care'},
        {'symbol': 'MRK', 'company': 'Merck & Co. Inc.', 'sector': 'Health Care'},
        {'symbol': 'PFE', 'company': 'Pfizer Inc.', 'sector': 'Health Care'},
        {'symbol': 'TMO', 'company': 'Thermo Fisher Scientific Inc.', 'sector': 'Health Care'},
        {'symbol': 'ABT', 'company': 'Abbott Laboratories', 'sector': 'Health Care'},
        {'symbol': 'DHR', 'company': 'Danaher Corporation', 'sector': 'Health Care'},
        {'symbol': 'BMY', 'company': 'Bristol-Myers Squibb Company', 'sector': 'Health Care'},
        {'symbol': 'AMGN', 'company': 'Amgen Inc.', 'sector': 'Health Care'},
        {'symbol': 'GILD', 'company': 'Gilead Sciences Inc.', 'sector': 'Health Care'},
        {'symbol': 'CVS', 'company': 'CVS Health Corporation', 'sector': 'Health Care'},
        {'symbol': 'CI', 'company': 'The Cigna Group', 'sector': 'Health Care'},

        # Consumer Staples
        {'symbol': 'WMT', 'company': 'Walmart Inc.', 'sector': 'Consumer Staples'},
        {'symbol': 'PG', 'company': 'The Procter & Gamble Company', 'sector': 'Consumer Staples'},
        {'symbol': 'KO', 'company': 'The Coca-Cola Company', 'sector': 'Consumer Staples'},
        {'symbol': 'PEP', 'company': 'PepsiCo Inc.', 'sector': 'Consumer Staples'},
        {'symbol': 'COST', 'company': 'Costco Wholesale Corporation', 'sector': 'Consumer Staples'},
        {'symbol': 'PM', 'company': 'Philip Morris International Inc.', 'sector': 'Consumer Staples'},
        {'symbol': 'MO', 'company': 'Altria Group Inc.', 'sector': 'Consumer Staples'},

        # Energy
        {'symbol': 'XOM', 'company': 'Exxon Mobil Corporation', 'sector': 'Energy'},
        {'symbol': 'CVX', 'company': 'Chevron Corporation', 'sector': 'Energy'},
        {'symbol': 'COP', 'company': 'ConocoPhillips', 'sector': 'Energy'},
        {'symbol': 'SLB', 'company': 'Schlumberger Limited', 'sector': 'Energy'},
        {'symbol': 'EOG', 'company': 'EOG Resources Inc.', 'sector': 'Energy'},
        {'symbol': 'PSX', 'company': 'Phillips 66', 'sector': 'Energy'},
        {'symbol': 'MPC', 'company': 'Marathon Petroleum Corporation', 'sector': 'Energy'},

        # Industrials
        {'symbol': 'BA', 'company': 'The Boeing Company', 'sector': 'Industrials'},
        {'symbol': 'CAT', 'company': 'Caterpillar Inc.', 'sector': 'Industrials'},
        {'symbol': 'GE', 'company': 'General Electric Company', 'sector': 'Industrials'},
        {'symbol': 'UPS', 'company': 'United Parcel Service Inc.', 'sector': 'Industrials'},
        {'symbol': 'RTX', 'company': 'RTX Corporation', 'sector': 'Industrials'},
        {'symbol': 'HON', 'company': 'Honeywell International Inc.', 'sector': 'Industrials'},
        {'symbol': 'UNP', 'company': 'Union Pacific Corporation', 'sector': 'Industrials'},
        {'symbol': 'DE', 'company': 'Deere & Company', 'sector': 'Industrials'},
        {'symbol': 'LMT', 'company': 'Lockheed Martin Corporation', 'sector': 'Industrials'},

        # Utilities
        {'symbol': 'NEE', 'company': 'NextEra Energy Inc.', 'sector': 'Utilities'},
        {'symbol': 'DUK', 'company': 'Duke Energy Corporation', 'sector': 'Utilities'},
        {'symbol': 'SO', 'company': 'The Southern Company', 'sector': 'Utilities'},
        {'symbol': 'D', 'company': 'Dominion Energy Inc.', 'sector': 'Utilities'},

        # Real Estate
        {'symbol': 'AMT', 'company': 'American Tower Corporation', 'sector': 'Real Estate'},
        {'symbol': 'PLD', 'company': 'Prologis Inc.', 'sector': 'Real Estate'},
        {'symbol': 'CCI', 'company': 'Crown Castle Inc.', 'sector': 'Real Estate'},
        {'symbol': 'EQIX', 'company': 'Equinix Inc.', 'sector': 'Real Estate'},

        # Materials
        {'symbol': 'LIN', 'company': 'Linde plc', 'sector': 'Materials'},
        {'symbol': 'APD', 'company': 'Air Products and Chemicals Inc.', 'sector': 'Materials'},
        {'symbol': 'SHW', 'company': 'The Sherwin-Williams Company', 'sector': 'Materials'},
        {'symbol': 'FCX', 'company': 'Freeport-McMoRan Inc.', 'sector': 'Materials'},
        {'symbol': 'NEM', 'company': 'Newmont Corporation', 'sector': 'Materials'},
    ]

    print(f"✅ Loaded {len(fallback_list)} major S&P 500 stocks from fallback list")
    return fallback_list

def save_sp500_list(sp500_data, output_dir='data'):
    """Save S&P 500 list to JSON file"""
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'sp500_symbols.json')

    output = {
        'last_updated': datetime.now().isoformat(),
        'count': len(sp500_data),
        'symbols': sp500_data
    }

    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"💾 Saved to {output_file}")
    return output_file

def load_sp500_list(data_dir='data'):
    """Load S&P 500 list from JSON file"""
    json_file = os.path.join(data_dir, 'sp500_symbols.json')

    if not os.path.exists(json_file):
        print(f"⚠️  S&P 500 list not found at {json_file}")
        print("   Run this script first to fetch the list")
        return None

    with open(json_file, 'r') as f:
        data = json.load(f)

    return [item['symbol'] for item in data['symbols']]

def get_symbols_by_sector(sector_name=None, data_dir='data'):
    """Get symbols filtered by sector"""
    json_file = os.path.join(data_dir, 'sp500_symbols.json')

    if not os.path.exists(json_file):
        return []

    with open(json_file, 'r') as f:
        data = json.load(f)

    if sector_name:
        return [
            item['symbol'] for item in data['symbols']
            if item['sector'].lower() == sector_name.lower()
        ]
    else:
        return [item['symbol'] for item in data['symbols']]

def main():
    """Fetch and save S&P 500 list"""
    print("📊 Fetching S&P 500 constituent list...")
    print("   Priority: Finnhub API -> Wikipedia -> File fallback\n")

    sp500_data, source = fetch_sp500_symbols()

    if sp500_data:
        save_sp500_list(sp500_data)

        # Print source info
        source_names = {
            'finnhub': '📡 Finnhub API',
            'wikipedia': '🌐 Wikipedia',
            'file': '📦 File fallback'
        }
        print(f"\n✨ Source: {source_names.get(source, source)}")

        # Print sector breakdown
        sectors = {}
        for item in sp500_data:
            sector = item['sector']
            sectors[sector] = sectors.get(sector, 0) + 1

        print("\n📊 Sector Breakdown:")
        for sector, count in sorted(sectors.items(), key=lambda x: x[1], reverse=True):
            print(f"   {sector}: {count} companies")

        print(f"\n✅ Ready to scan {len(sp500_data)} stocks!")
        print("   Use: python scripts/scan_sp500_news.py")
    else:
        print("❌ Failed to fetch S&P 500 list")

if __name__ == '__main__':
    main()
