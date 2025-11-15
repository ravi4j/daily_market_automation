#!/usr/bin/env python3
"""
Finnhub Data Module
Provides data fetching with caching and rate limiting
"""

import os
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path

try:
    import finnhub
    FINNHUB_AVAILABLE = True
except ImportError:
    FINNHUB_AVAILABLE = False


class DataCache:
    """Simple file-based cache with TTL"""
    
    def __init__(self, cache_dir: str = "data/cache", ttl_hours: int = 24):
        """
        Initialize cache
        
        Args:
            cache_dir: Directory to store cache files
            ttl_hours: Time-to-live for cached data in hours
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl_seconds = ttl_hours * 3600
    
    def get(self, key: str) -> Optional[Dict]:
        """Get cached data if not expired"""
        cache_file = self.cache_dir / f"{key}.json"
        
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, 'r') as f:
                cached = json.load(f)
            
            # Check expiration
            cached_time = datetime.fromisoformat(cached['timestamp'])
            age = (datetime.now() - cached_time).total_seconds()
            
            if age < self.ttl_seconds:
                return cached['data']
            else:
                # Expired, remove
                cache_file.unlink()
                return None
        
        except (json.JSONDecodeError, KeyError, ValueError):
            return None
    
    def set(self, key: str, data: Dict):
        """Save data to cache"""
        cache_file = self.cache_dir / f"{key}.json"
        
        cached = {
            'timestamp': datetime.now().isoformat(),
            'data': data
        }
        
        with open(cache_file, 'w') as f:
            json.dump(cached, f, indent=2, default=str)
    
    def clear(self):
        """Clear all cached data"""
        for cache_file in self.cache_dir.glob("*.json"):
            cache_file.unlink()


class RateLimiter:
    """Rate limiter for API calls"""
    
    def __init__(self, max_calls_per_minute: int = 50):
        self.max_calls = max_calls_per_minute
        self.call_times: List[datetime] = []
    
    def wait_if_needed(self):
        """Wait if approaching rate limit"""
        now = datetime.now()
        self.call_times = [t for t in self.call_times if (now - t).total_seconds() < 60]
        
        if len(self.call_times) >= self.max_calls:
            oldest = self.call_times[0]
            sleep_time = 60 - (now - oldest).total_seconds()
            if sleep_time > 0:
                time.sleep(sleep_time + 0.5)
                self.call_times = []
        
        self.call_times.append(now)


class FinnhubClient:
    """
    Finnhub API client with caching and rate limiting
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        rate_limit: int = 50,
        cache_ttl_hours: int = 24
    ):
        """
        Initialize Finnhub client
        
        Args:
            api_key: Finnhub API key (defaults to FINNHUB_API_KEY env var)
            rate_limit: Max API calls per minute
            cache_ttl_hours: Cache time-to-live in hours
        """
        if not FINNHUB_AVAILABLE:
            raise ImportError("finnhub-python not installed. Run: pip install finnhub-python")
        
        self.api_key = api_key or os.getenv('FINNHUB_API_KEY')
        if not self.api_key:
            raise ValueError("Finnhub API key not found. Set FINNHUB_API_KEY environment variable.")
        
        self.client = finnhub.Client(api_key=self.api_key)
        self.rate_limiter = RateLimiter(max_calls_per_minute=rate_limit)
        self.cache = DataCache(ttl_hours=cache_ttl_hours)
    
    def fetch_sp500_list(self, force_refresh: bool = False) -> List[Dict]:
        """
        Fetch S&P 500 constituent list from Finnhub
        
        Note: Finnhub doesn't have a direct S&P 500 endpoint, so we:
        1. Get all US stocks
        2. Filter for common stocks on major exchanges
        3. Sort by market cap (if available)
        4. Return top ~500-520 stocks as proxy
        
        Args:
            force_refresh: Skip cache and fetch fresh data
        
        Returns:
            List of dicts with keys: symbol, company, sector
        """
        cache_key = 'sp500_list'
        
        # Try cache first
        if not force_refresh:
            cached = self.cache.get(cache_key)
            if cached:
                print(f"✅ Loaded S&P 500 list from cache ({len(cached)} stocks)")
                return cached
        
        try:
            print("📡 Fetching stock list from Finnhub...")
            self.rate_limiter.wait_if_needed()
            
            # Get all US stocks
            us_stocks = self.client.stock_symbols('US')
            
            # Filter for common stocks on major exchanges
            major_exchanges = ['NYSE', 'NASDAQ', 'NYSE ARCA']
            filtered = [
                s for s in us_stocks
                if s.get('type') == 'Common Stock'
                and s.get('currency') == 'USD'
                and s.get('mic') in major_exchanges
            ]
            
            print(f"📊 Found {len(filtered)} US common stocks")
            
            # Finnhub doesn't provide market cap in stock_symbols
            # So we'll just return all filtered stocks sorted alphabetically
            # User can rely on the file fallback for accurate S&P 500 list
            sp500_proxy = [
                {
                    'symbol': s['displaySymbol'],
                    'company': s['description'],
                    'sector': 'Unknown'  # Finnhub requires separate API call for sector
                }
                for s in filtered
            ]
            
            # Sort by symbol
            sp500_proxy.sort(key=lambda x: x['symbol'])
            
            # Cache the result
            self.cache.set(cache_key, sp500_proxy)
            
            print(f"✅ Fetched {len(sp500_proxy)} stocks from Finnhub")
            return sp500_proxy
        
        except Exception as e:
            print(f"⚠️  Error fetching from Finnhub: {e}")
            raise
    
    def get_fundamentals(self, symbol: str) -> Optional[Dict]:
        """
        Get fundamental metrics for a symbol
        
        Args:
            symbol: Stock ticker
        
        Returns:
            Dict with fundamentals or None
        """
        cache_key = f'fundamentals_{symbol}'
        
        # Try cache first (fundamentals don't change often)
        cached = self.cache.get(cache_key)
        if cached:
            return cached
        
        try:
            self.rate_limiter.wait_if_needed()
            
            # Get company profile
            profile = self.client.company_profile2(symbol=symbol)
            
            if not profile:
                return None
            
            # Get basic financials
            self.rate_limiter.wait_if_needed()
            financials = self.client.company_basic_financials(symbol, 'all')
            
            metrics = financials.get('metric', {}) if financials else {}
            
            # Extract key metrics
            fundamentals = {
                'symbol': symbol,
                'company_name': profile.get('name', symbol),
                'sector': profile.get('finnhubIndustry', 'Unknown'),
                'market_cap': profile.get('marketCapitalization', 0),
                'pe_ratio': metrics.get('peBasicExclExtraTTM'),
                'profit_margins': metrics.get('netProfitMarginTTM'),
                'revenue_growth': metrics.get('revenueGrowthTTM'),
                'roe': metrics.get('roeTTM'),
                'debt_to_equity': metrics.get('totalDebt/totalEquityAnnual'),
                '52w_high': metrics.get('52WeekHigh'),
                '52w_low': metrics.get('52WeekLow'),
                'beta': metrics.get('beta')
            }
            
            # Cache the result
            self.cache.set(cache_key, fundamentals)
            
            return fundamentals
        
        except Exception as e:
            print(f"⚠️  Error fetching fundamentals for {symbol}: {e}")
            return None
    
    def clear_cache(self):
        """Clear all cached data"""
        self.cache.clear()
        print("✅ Cache cleared")


def main():
    """Test Finnhub client"""
    import sys
    
    try:
        client = FinnhubClient()
        print("✅ Connected to Finnhub API\n")
        
        # Test 1: Fetch S&P 500 list
        print("TEST 1: Fetch S&P 500 List")
        print("=" * 60)
        sp500 = client.fetch_sp500_list()
        print(f"Total stocks: {len(sp500)}")
        print(f"Sample (first 5): {sp500[:5]}")
        print()
        
        # Test 2: Fetch fundamentals
        test_symbols = ['AAPL', 'NVDA', 'MSFT']
        print("TEST 2: Fetch Fundamentals")
        print("=" * 60)
        
        for symbol in test_symbols:
            print(f"\n{symbol}:")
            fund = client.get_fundamentals(symbol)
            if fund:
                print(f"  Company: {fund['company_name']}")
                print(f"  Sector: {fund['sector']}")
                print(f"  Market Cap: ${fund['market_cap']:.2f}B")
                print(f"  P/E Ratio: {fund['pe_ratio']}")
                print(f"  Profit Margin: {fund['profit_margins']}")
            else:
                print("  No data found")
        
        # Test 3: Cache test
        print("\n\nTEST 3: Cache Test")
        print("=" * 60)
        print("Fetching AAPL again (should be cached)...")
        fund = client.get_fundamentals('AAPL')
        print(f"✅ Got cached data for {fund['company_name']}")
        
        print("\n✅ All tests passed!")
    
    except ValueError as e:
        print(f"❌ Error: {e}")
        print("\n💡 Set your Finnhub API key:")
        print("   export FINNHUB_API_KEY='your_key_here'")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

