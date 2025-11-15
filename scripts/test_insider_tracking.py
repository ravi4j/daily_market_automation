#!/usr/bin/env python3
"""
Test script for insider tracking integration
Tests all components: InsiderTracker, FinnhubClient, and integration with news scanner
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


def test_finnhub_connection():
    """Test 1: Finnhub API connection"""
    print("=" * 70)
    print("TEST 1: Finnhub API Connection")
    print("=" * 70)
    
    try:
        from src.finnhub_data import FinnhubClient
        
        client = FinnhubClient()
        print("✅ Successfully connected to Finnhub API")
        return True
    except ValueError as e:
        print(f"❌ API key error: {e}")
        print("\n💡 To enable insider tracking:")
        print("   1. Get free API key: https://finnhub.io/register")
        print("   2. Set environment variable:")
        print("      export FINNHUB_API_KEY='your_key_here'")
        return False
    except ImportError:
        print("❌ finnhub-python not installed")
        print("\n💡 Install: pip install finnhub-python")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_insider_tracker():
    """Test 2: Insider Tracker functionality"""
    print("\n" + "=" * 70)
    print("TEST 2: Insider Tracker Functionality")
    print("=" * 70)
    
    try:
        from src.insider_tracker import InsiderTracker
        
        tracker = InsiderTracker()
        print("✅ InsiderTracker initialized")
        
        # Test with known stocks that often have insider activity
        test_symbols = ['AAPL', 'NVDA', 'MSFT']
        print(f"\n📊 Testing insider data for: {', '.join(test_symbols)}")
        print("   (This will take ~10 seconds due to rate limiting)\n")
        
        for symbol in test_symbols:
            print(f"{symbol}:")
            data = tracker.get_insider_activity(symbol, days=30)
            
            if data:
                print(f"  ✅ Found insider data")
                print(f"     Sentiment: {data['sentiment']}")
                print(f"     Score Adjustment: {data['score_adjustment']:+d}")
                print(f"     Buys: {data['num_buys']}, Sells: {data['num_sells']}")
                print(f"     Net Value: ${data['net_value']:,.0f}")
            else:
                print(f"  ⚪ No insider activity in last 30 days")
            print()
        
        return True
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_sp500_list_fetch():
    """Test 3: S&P 500 list fetching with Finnhub fallback"""
    print("=" * 70)
    print("TEST 3: S&P 500 List Fetching (Finnhub → Wikipedia → File)")
    print("=" * 70)
    
    try:
        # Import the fetch function
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
        from fetch_sp500_list import fetch_sp500_symbols
        
        sp500_data, source = fetch_sp500_symbols()
        
        if sp500_data:
            print(f"✅ Successfully fetched {len(sp500_data)} stocks")
            print(f"   Source: {source}")
            
            # Show sample
            print(f"\n   Sample (first 5):")
            for item in sp500_data[:5]:
                print(f"   - {item['symbol']:6s} {item['company'][:40]}")
            
            return True
        else:
            print("❌ Failed to fetch S&P 500 list")
            return False
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_integration():
    """Test 4: Full integration test (news scanner + insider tracking)"""
    print("\n" + "=" * 70)
    print("TEST 4: Integration Test (News Scanner + Insider Tracking)")
    print("=" * 70)
    
    try:
        from src.news_monitor import NewsMonitor
        from src.insider_tracker import InsiderTracker
        
        # Initialize both
        monitor = NewsMonitor()
        tracker = InsiderTracker()
        
        print("✅ Both modules initialized")
        
        # Test with a small set of symbols
        test_symbols = ['AAPL', 'TSLA']
        print(f"\n📊 Testing integration with: {', '.join(test_symbols)}")
        print("   (Looking for opportunities and insider data)\n")
        
        # Scan for opportunities
        opportunities = monitor.identify_opportunities(test_symbols, min_drop=0.0)
        
        if opportunities:
            print(f"✅ Found {len(opportunities)} opportunities")
            
            # Add insider data
            for opp in opportunities:
                symbol = opp['symbol']
                print(f"\n{symbol}:")
                print(f"  Base Score: {opp['opportunity_score']}")
                
                insider_data = tracker.get_insider_activity(symbol, days=30)
                if insider_data:
                    adjustment = insider_data['score_adjustment']
                    new_score = max(0, min(100, opp['opportunity_score'] + adjustment))
                    
                    print(f"  Insider Sentiment: {insider_data['sentiment']}")
                    print(f"  Score Adjustment: {adjustment:+d}")
                    print(f"  Adjusted Score: {new_score}")
                    print(f"  ✅ Integration working!")
                else:
                    print(f"  ⚪ No insider activity")
        else:
            print("⚪ No opportunities found (symbols may be stable/rising)")
            print("   This is expected - insider tracking would work if opportunities existed")
        
        return True
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 15 + "INSIDER TRACKING TEST SUITE" + " " * 25 + "║")
    print("╚" + "=" * 68 + "╝")
    print()
    
    results = {}
    
    # Test 1: Finnhub Connection
    results['connection'] = test_finnhub_connection()
    
    # Only continue if connection works
    if results['connection']:
        results['tracker'] = test_insider_tracker()
        results['sp500_fetch'] = test_sp500_list_fetch()
        results['integration'] = test_integration()
    else:
        print("\n⚠️  Skipping remaining tests (Finnhub API not configured)")
        results['tracker'] = None
        results['sp500_fetch'] = None
        results['integration'] = None
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else ("⏭️  SKIP" if result is None else "❌ FAIL")
        print(f"{test_name.replace('_', ' ').title():30s} {status}")
    
    passed = sum(1 for r in results.values() if r is True)
    failed = sum(1 for r in results.values() if r is False)
    skipped = sum(1 for r in results.values() if r is None)
    
    print()
    print(f"Total: {passed} passed, {failed} failed, {skipped} skipped")
    
    if failed == 0 and passed > 0:
        print("\n🎉 All tests passed! Insider tracking is ready to use.")
        print("\n📚 Next steps:")
        print("   1. Run: python scripts/scan_sp500_news.py --top 10")
        print("   2. Check signals/sp500_opportunities.json for insider data")
        print("   3. Add FINNHUB_API_KEY to GitHub Secrets for automation")
    elif results['connection'] is False:
        print("\n💡 Set up Finnhub API key to enable insider tracking:")
        print("   1. Register: https://finnhub.io/register")
        print("   2. Get your API key")
        print("   3. Set: export FINNHUB_API_KEY='your_key_here'")
        print("   4. Re-run this test")
    else:
        print("\n⚠️  Some tests failed. Check errors above for details.")
    
    print()
    sys.exit(0 if failed == 0 else 1)


if __name__ == '__main__':
    main()

