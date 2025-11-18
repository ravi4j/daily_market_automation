"""
Market Futures Monitor
Monitor S&P 500, Nasdaq, and Dow futures for market sentiment
"""

import yfinance as yf
from typing import Dict
from datetime import datetime
import pytz


class FuturesMonitor:
    """Monitor major market futures for overall sentiment"""
    
    # Futures symbols (using index proxies for simplicity)
    FUTURES_SYMBOLS = {
        'S&P 500': '^GSPC',    # S&P 500 Index (or 'ES=F' for actual futures)
        'Nasdaq': '^IXIC',     # Nasdaq Composite (or 'NQ=F' for actual futures)
        'Dow Jones': '^DJI'    # Dow Jones (or 'YM=F' for actual futures)
    }
    
    def __init__(self):
        self.et_tz = pytz.timezone('America/New_York')
    
    def get_futures_sentiment(self) -> Dict:
        """
        Get overall market sentiment from futures
        
        Returns:
        {
            'S&P 500': {
                'current': 4500.25,
                'previous_close': 4530.10,
                'change': -29.85,
                'change_pct': -0.66
            },
            'Nasdaq': {...},
            'Dow Jones': {...},
            'overall_sentiment': 'BEARISH',
            'sentiment_emoji': '🔴',
            'recommendation': 'Market likely opens RED',
            'avg_change': -0.75,
            'time': '2025-11-18 07:00:00 ET'
        }
        """
        futures_data = {}
        
        print("📊 Fetching market futures...")
        
        for name, symbol in self.FUTURES_SYMBOLS.items():
            try:
                print(f"   Fetching {name}...")
                ticker = yf.Ticker(symbol)
                
                # Get latest data with pre-market
                data = ticker.history(period='1d', interval='1m', prepost=True)
                
                if data.empty:
                    print(f"   ⚠️  No data for {name}")
                    continue
                
                # Current price
                current = data['Close'].iloc[-1]
                
                # Previous close
                info = ticker.info
                previous = info.get('previousClose') or info.get('regularMarketPreviousClose')
                
                if not previous:
                    print(f"   ⚠️  No previous close for {name}")
                    continue
                
                # Calculate change
                change = current - previous
                change_pct = (change / previous) * 100
                
                futures_data[name] = {
                    'current': round(float(current), 2),
                    'previous_close': round(float(previous), 2),
                    'change': round(float(change), 2),
                    'change_pct': round(float(change_pct), 2)
                }
                
                print(f"   ✅ {name}: {change_pct:+.2f}%")
            
            except Exception as e:
                print(f"   ❌ Error fetching {name}: {e}")
        
        # Calculate overall sentiment
        if futures_data:
            avg_change = sum(f['change_pct'] for f in futures_data.values()) / len(futures_data)
            
            # Determine sentiment
            if avg_change > 1.5:
                sentiment = 'VERY BULLISH'
                emoji = '🟢🟢'
                rec = 'Market likely opens STRONG GREEN'
            elif avg_change > 0.5:
                sentiment = 'BULLISH'
                emoji = '🟢'
                rec = 'Market likely opens green'
            elif avg_change > -0.3:
                sentiment = 'NEUTRAL'
                emoji = '🟡'
                rec = 'Market likely opens flat'
            elif avg_change > -1.0:
                sentiment = 'BEARISH'
                emoji = '🔴'
                rec = 'Market likely opens red'
            else:
                sentiment = 'VERY BEARISH'
                emoji = '🔴🔴'
                rec = 'Market likely opens STRONG RED'
            
            futures_data['overall_sentiment'] = sentiment
            futures_data['sentiment_emoji'] = emoji
            futures_data['recommendation'] = rec
            futures_data['avg_change'] = round(avg_change, 2)
            futures_data['time'] = datetime.now(self.et_tz).strftime('%Y-%m-%d %I:%M %p ET')
            
            print(f"\n   📈 Overall: {sentiment} ({avg_change:+.2f}%)")
        else:
            print("\n   ⚠️  Could not fetch futures data")
        
        return futures_data
    
    def get_sector_futures(self) -> Dict:
        """
        Get sector-specific futures/ETFs
        
        Returns sentiment for major sectors:
        - Technology (QQQ)
        - Financials (XLF)
        - Energy (XLE)
        - Healthcare (XLV)
        etc.
        """
        sector_etfs = {
            'Technology': 'QQQ',
            'Financials': 'XLF',
            'Energy': 'XLE',
            'Healthcare': 'XLV',
            'Consumer': 'XLY',
            'Industrials': 'XLI'
        }
        
        sector_data = {}
        
        print("\n📊 Fetching sector ETFs...")
        
        for sector, etf in sector_etfs.items():
            try:
                ticker = yf.Ticker(etf)
                data = ticker.history(period='1d', interval='1m', prepost=True)
                
                if data.empty:
                    continue
                
                current = data['Close'].iloc[-1]
                info = ticker.info
                previous = info.get('previousClose')
                
                if previous:
                    change_pct = ((current - previous) / previous) * 100
                    sector_data[sector] = {
                        'etf': etf,
                        'current': round(float(current), 2),
                        'change_pct': round(float(change_pct), 2)
                    }
                    
                    print(f"   {sector} ({etf}): {change_pct:+.2f}%")
            
            except Exception as e:
                print(f"   ⚠️  Error fetching {sector}: {e}")
        
        return sector_data
    
    def get_vix_sentiment(self) -> Dict:
        """
        Get VIX (fear index) for volatility assessment
        
        VIX levels:
        < 12: Very low volatility (complacent)
        12-20: Normal volatility
        20-30: Elevated volatility (caution)
        30+: High volatility (fear/panic)
        """
        try:
            print("\n📊 Fetching VIX (Volatility Index)...")
            vix = yf.Ticker('^VIX')
            data = vix.history(period='1d', interval='1m', prepost=True)
            
            if data.empty:
                return {}
            
            current_vix = data['Close'].iloc[-1]
            
            # Interpret VIX level
            if current_vix < 12:
                level = 'VERY LOW'
                interpretation = 'Market complacent, watch for reversals'
                emoji = '😴'
            elif current_vix < 20:
                level = 'NORMAL'
                interpretation = 'Normal market conditions'
                emoji = '✅'
            elif current_vix < 30:
                level = 'ELEVATED'
                interpretation = 'Market caution, expect volatility'
                emoji = '⚠️'
            else:
                level = 'HIGH'
                interpretation = 'Market fear/panic, high risk'
                emoji = '🚨'
            
            print(f"   VIX: {current_vix:.2f} - {level} {emoji}")
            
            return {
                'vix': round(float(current_vix), 2),
                'level': level,
                'interpretation': interpretation,
                'emoji': emoji
            }
        
        except Exception as e:
            print(f"   ⚠️  Error fetching VIX: {e}")
            return {}


# Example usage and testing
if __name__ == '__main__':
    print("="*80)
    print("FUTURES MONITOR TEST")
    print("="*80 + "\n")
    
    monitor = FuturesMonitor()
    
    # Get main futures
    futures = monitor.get_futures_sentiment()
    
    # Get sector data
    sectors = monitor.get_sector_futures()
    
    # Get VIX
    vix = monitor.get_vix_sentiment()
    
    # Display results
    print("\n" + "="*80)
    print("MARKET SENTIMENT SUMMARY")
    print("="*80)
    
    if futures:
        print(f"\n{futures['sentiment_emoji']} Overall: {futures['overall_sentiment']}")
        print(f"Average Change: {futures['avg_change']:+.2f}%")
        print(f"Recommendation: {futures['recommendation']}")
        
        print("\nIndices:")
        for name in ['S&P 500', 'Nasdaq', 'Dow Jones']:
            if name in futures:
                data = futures[name]
                emoji = "🟢" if data['change_pct'] > 0 else "🔴"
                print(f"  {emoji} {name}: {data['change_pct']:+.2f}%")
    
    if vix:
        print(f"\nVolatility:")
        print(f"  {vix['emoji']} VIX: {vix['vix']} ({vix['level']})")
        print(f"  {vix['interpretation']}")
    
    if sectors:
        print(f"\nSector Leaders:")
        # Sort by change_pct
        sorted_sectors = sorted(sectors.items(), key=lambda x: x[1]['change_pct'], reverse=True)
        for sector, data in sorted_sectors[:3]:
            emoji = "🟢" if data['change_pct'] > 0 else "🔴"
            print(f"  {emoji} {sector}: {data['change_pct']:+.2f}%")
    
    print("\n" + "="*80)
    print("Test complete!")

