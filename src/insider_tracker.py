#!/usr/bin/env python3
"""
Insider Trading Tracker using Finnhub API
Analyzes insider transactions to identify smart money movements
"""

import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

try:
    import finnhub
    FINNHUB_AVAILABLE = True
except ImportError:
    FINNHUB_AVAILABLE = False


@dataclass
class InsiderTransaction:
    """Represents a single insider transaction"""
    name: str
    change: int  # shares bought/sold (positive = buy, negative = sell)
    filing_date: str
    transaction_date: str
    share_price: float
    transaction_value: float  # dollar value of transaction


class RateLimiter:
    """Rate limiter to stay within API limits (50 calls/min, buffer for 60 limit)"""
    
    def __init__(self, max_calls_per_minute: int = 50):
        self.max_calls = max_calls_per_minute
        self.call_times: List[datetime] = []
    
    def wait_if_needed(self):
        """Wait if we're approaching rate limit"""
        now = datetime.now()
        
        # Remove calls older than 1 minute
        self.call_times = [t for t in self.call_times if (now - t).total_seconds() < 60]
        
        # If we're at the limit, wait
        if len(self.call_times) >= self.max_calls:
            oldest_call = self.call_times[0]
            sleep_time = 60 - (now - oldest_call).total_seconds()
            if sleep_time > 0:
                print(f"⏸️  Rate limit reached, waiting {sleep_time:.1f}s...")
                time.sleep(sleep_time + 0.5)  # Add buffer
                self.call_times = []  # Reset after waiting
        
        self.call_times.append(now)


class InsiderTracker:
    """Track insider trading activity using Finnhub API"""
    
    def __init__(self, api_key: Optional[str] = None, rate_limit: int = 50):
        """
        Initialize insider tracker
        
        Args:
            api_key: Finnhub API key (defaults to FINNHUB_API_KEY env var)
            rate_limit: Max API calls per minute (default 50 for 60 limit buffer)
        """
        if not FINNHUB_AVAILABLE:
            raise ImportError("finnhub-python not installed. Run: pip install finnhub-python")
        
        self.api_key = api_key or os.getenv('FINNHUB_API_KEY')
        if not self.api_key:
            raise ValueError("Finnhub API key not found. Set FINNHUB_API_KEY environment variable.")
        
        self.client = finnhub.Client(api_key=self.api_key)
        self.rate_limiter = RateLimiter(max_calls_per_minute=rate_limit)
    
    def get_insider_activity(self, symbol: str, days: int = 30) -> Optional[Dict]:
        """
        Get insider trading activity for a symbol
        
        Args:
            symbol: Stock ticker symbol
            days: Lookback period in days (default 30)
        
        Returns:
            Dict with insider analysis or None if no data/error
        """
        try:
            # Rate limit before API call
            self.rate_limiter.wait_if_needed()
            
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Fetch insider transactions
            response = self.client.stock_insider_transactions(
                symbol,
                start_date.strftime('%Y-%m-%d'),
                end_date.strftime('%Y-%m-%d')
            )
            
            if not response or 'data' not in response:
                return None
            
            transactions = response['data']
            if not transactions:
                return None
            
            # Parse transactions
            parsed_txns = []
            for txn in transactions:
                try:
                    change = txn.get('change', 0)
                    share_price = txn.get('transactionPrice', 0) or 0
                    
                    if change == 0 or share_price == 0:
                        continue
                    
                    parsed_txns.append(InsiderTransaction(
                        name=txn.get('name', 'Unknown'),
                        change=change,
                        filing_date=txn.get('filingDate', ''),
                        transaction_date=txn.get('transactionDate', ''),
                        share_price=share_price,
                        transaction_value=change * share_price
                    ))
                except (KeyError, TypeError, ValueError):
                    continue
            
            if not parsed_txns:
                return None
            
            # Analyze insider activity
            analysis = self._analyze_transactions(parsed_txns, symbol)
            return analysis
        
        except Exception as e:
            print(f"⚠️  Error fetching insider data for {symbol}: {e}")
            return None
    
    def _analyze_transactions(self, transactions: List[InsiderTransaction], symbol: str) -> Dict:
        """Analyze insider transactions and determine sentiment"""
        
        # Separate buys and sells
        buys = [t for t in transactions if t.change > 0]
        sells = [t for t in transactions if t.change < 0]
        
        # Calculate totals
        total_buy_value = sum(t.transaction_value for t in buys)
        total_sell_value = sum(abs(t.transaction_value) for t in sells)
        net_value = total_buy_value - total_sell_value
        
        total_buy_shares = sum(t.change for t in buys)
        total_sell_shares = sum(abs(t.change) for t in sells)
        
        # Calculate sentiment
        sentiment, score_adjustment = self._calculate_sentiment(
            net_value=net_value,
            num_buys=len(buys),
            num_sells=len(sells),
            total_buy_value=total_buy_value,
            total_sell_value=total_sell_value
        )
        
        # Find largest transactions
        largest_buy = max(buys, key=lambda t: t.transaction_value) if buys else None
        largest_sell = max(sells, key=lambda t: abs(t.transaction_value)) if sells else None
        
        return {
            'symbol': symbol,
            'period_days': (datetime.now() - datetime.strptime(transactions[-1].transaction_date, '%Y-%m-%d')).days,
            'num_buys': len(buys),
            'num_sells': len(sells),
            'total_buy_value': total_buy_value,
            'total_sell_value': total_sell_value,
            'net_value': net_value,
            'total_buy_shares': total_buy_shares,
            'total_sell_shares': total_sell_shares,
            'sentiment': sentiment,
            'score_adjustment': score_adjustment,
            'largest_buy': {
                'name': largest_buy.name,
                'shares': largest_buy.change,
                'value': largest_buy.transaction_value,
                'date': largest_buy.transaction_date
            } if largest_buy else None,
            'largest_sell': {
                'name': largest_sell.name,
                'shares': abs(largest_sell.change),
                'value': abs(largest_sell.transaction_value),
                'date': largest_sell.transaction_date
            } if largest_sell else None,
            'all_transactions': transactions
        }
    
    def _calculate_sentiment(
        self,
        net_value: float,
        num_buys: int,
        num_sells: int,
        total_buy_value: float,
        total_sell_value: float
    ) -> Tuple[str, int]:
        """
        Calculate insider sentiment and score adjustment
        
        Returns:
            Tuple of (sentiment_string, score_adjustment)
            sentiment: STRONG_BUY, BUY, NEUTRAL, SELL, STRONG_SELL
            adjustment: +15, +8, 0, -8, -15
        """
        
        # If no activity, neutral
        if num_buys == 0 and num_sells == 0:
            return "NEUTRAL", 0
        
        # Calculate buy/sell ratio
        if total_sell_value == 0:
            buy_ratio = 1.0  # All buys
        elif total_buy_value == 0:
            buy_ratio = 0.0  # All sells
        else:
            buy_ratio = total_buy_value / (total_buy_value + total_sell_value)
        
        # Calculate transaction count ratio
        total_txns = num_buys + num_sells
        buy_count_ratio = num_buys / total_txns if total_txns > 0 else 0
        
        # Sentiment thresholds
        if buy_ratio >= 0.75 and buy_count_ratio >= 0.7:
            # Heavy buying (75%+ by value, 70%+ by count)
            return "STRONG_BUY", 15
        elif buy_ratio >= 0.60 and buy_count_ratio >= 0.55:
            # Moderate buying (60%+ by value, 55%+ by count)
            return "BUY", 8
        elif buy_ratio <= 0.25 and buy_count_ratio <= 0.3:
            # Heavy selling (25% or less buys by value, 30% or less by count)
            return "STRONG_SELL", -15
        elif buy_ratio <= 0.40 and buy_count_ratio <= 0.45:
            # Moderate selling (40% or less buys by value, 45% or less by count)
            return "SELL", -8
        else:
            # Mixed or balanced activity
            return "NEUTRAL", 0
    
    def format_for_telegram(self, insider_data: Dict) -> str:
        """Format insider data for Telegram alert"""
        
        sentiment = insider_data['sentiment']
        net_value = insider_data['net_value']
        num_buys = insider_data['num_buys']
        num_sells = insider_data['num_sells']
        
        # Emoji for sentiment
        sentiment_emoji = {
            'STRONG_BUY': '🟢🟢',
            'BUY': '🟢',
            'NEUTRAL': '⚪',
            'SELL': '🔴',
            'STRONG_SELL': '🔴🔴'
        }
        emoji = sentiment_emoji.get(sentiment, '⚪')
        
        message = f"\n💼 *Insider Activity*\n"
        message += f"{emoji} Sentiment: *{sentiment}* "
        
        adj = insider_data['score_adjustment']
        if adj > 0:
            message += f"(+{adj} boost)\n"
        elif adj < 0:
            message += f"({adj} penalty)\n"
        else:
            message += "\n"
        
        message += f"📊 {num_buys} buys, {num_sells} sells\n"
        message += f"💰 Net: ${net_value:,.0f} "
        
        if net_value > 0:
            message += "(buying)"
        elif net_value < 0:
            message += "(selling)"
        else:
            message += "(neutral)"
        
        # Show largest transaction
        if insider_data['largest_buy']:
            buy = insider_data['largest_buy']
            message += f"\n🏆 Largest Buy: ${buy['value']:,.0f} ({buy['shares']:,} shares)"
        
        if insider_data['largest_sell']:
            sell = insider_data['largest_sell']
            message += f"\n🏆 Largest Sell: ${sell['value']:,.0f} ({sell['shares']:,} shares)"
        
        return message


def main():
    """Test insider tracker"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python src/insider_tracker.py SYMBOL [SYMBOL...]")
        print("Example: python src/insider_tracker.py AAPL NVDA MSFT")
        sys.exit(1)
    
    symbols = sys.argv[1:]
    
    try:
        tracker = InsiderTracker()
        print(f"✅ Connected to Finnhub API")
        print(f"📊 Analyzing insider activity for {len(symbols)} symbol(s)...\n")
        
        for symbol in symbols:
            print(f"{'='*60}")
            print(f"Symbol: {symbol}")
            print(f"{'='*60}")
            
            data = tracker.get_insider_activity(symbol, days=30)
            
            if data:
                print(f"Sentiment: {data['sentiment']}")
                print(f"Score Adjustment: {data['score_adjustment']:+d}")
                print(f"Buys: {data['num_buys']}, Sells: {data['num_sells']}")
                print(f"Net Value: ${data['net_value']:,.2f}")
                print(f"Buy Value: ${data['total_buy_value']:,.2f}")
                print(f"Sell Value: ${data['total_sell_value']:,.2f}")
                
                if data['largest_buy']:
                    buy = data['largest_buy']
                    print(f"\nLargest Buy:")
                    print(f"  {buy['name']}: {buy['shares']:,} shares @ ${buy['value']:,.2f}")
                    print(f"  Date: {buy['date']}")
                
                if data['largest_sell']:
                    sell = data['largest_sell']
                    print(f"\nLargest Sell:")
                    print(f"  {sell['name']}: {sell['shares']:,} shares @ ${sell['value']:,.2f}")
                    print(f"  Date: {sell['date']}")
                
                print("\nTelegram Format:")
                print(tracker.format_for_telegram(data))
            else:
                print("❌ No insider data found")
            
            print()
    
    except ValueError as e:
        print(f"❌ Error: {e}")
        print("\n💡 Set your Finnhub API key:")
        print("   export FINNHUB_API_KEY='your_key_here'")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

