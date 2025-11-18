"""
Pre-Market Gap Monitor
Detects gaps and provides actionable alerts before market open
"""

import yfinance as yf
from datetime import datetime, time
import pytz
from typing import Dict, List, Optional
import pandas as pd


class PreMarketMonitor:
    """Monitor pre-market prices and detect gaps"""
    
    def __init__(self, positions: Dict = None):
        """
        Initialize with your current positions
        
        positions = {
            'ETN': {
                'shares': 20,
                'avg_entry': 341.485,
                'stop_loss': 340.00,
                'target1': 365.00,
                'target2': 380.00
            }
        }
        """
        self.positions = positions or {}
        self.et_tz = pytz.timezone('America/New_York')
    
    def is_premarket_hours(self) -> bool:
        """Check if currently in pre-market hours (4 AM - 9:30 AM ET)"""
        now_et = datetime.now(self.et_tz)
        current_time = now_et.time()
        
        premarket_start = time(4, 0)  # 4:00 AM ET
        premarket_end = time(9, 30)    # 9:30 AM ET
        
        # Also check if it's a weekday
        if now_et.weekday() >= 5:  # Saturday = 5, Sunday = 6
            return False
        
        return premarket_start <= current_time < premarket_end
    
    def get_premarket_price(self, symbol: str) -> Optional[Dict]:
        """
        Get pre-market price for a symbol
        
        Returns:
        {
            'symbol': 'ETN',
            'premarket_price': 340.33,
            'previous_close': 342.76,
            'change': -2.43,
            'change_pct': -0.71,
            'time': '2025-11-18 08:00:00 ET',
            'volume': 1234  # pre-market volume
        }
        """
        try:
            ticker = yf.Ticker(symbol)
            
            # Get intraday data with pre/post market
            data = ticker.history(period='1d', interval='1m', prepost=True)
            
            if data.empty:
                print(f"⚠️  No data for {symbol}")
                return None
            
            # Latest price (includes pre-market if available)
            current_price = data['Close'].iloc[-1]
            
            # Pre-market volume (sum of all pre-market trades)
            now_et = datetime.now(self.et_tz)
            market_open_today = now_et.replace(hour=9, minute=30, second=0, microsecond=0)
            
            # Filter for pre-market only
            premarket_data = data[data.index < market_open_today]
            premarket_volume = int(premarket_data['Volume'].sum()) if not premarket_data.empty else 0
            
            # Get previous close
            info = ticker.info
            previous_close = info.get('previousClose') or info.get('regularMarketPreviousClose')
            
            if not previous_close:
                print(f"⚠️  No previous close for {symbol}")
                return None
            
            # Calculate gap
            change = current_price - previous_close
            change_pct = (change / previous_close) * 100
            
            return {
                'symbol': symbol,
                'premarket_price': round(float(current_price), 2),
                'previous_close': round(float(previous_close), 2),
                'change': round(float(change), 2),
                'change_pct': round(float(change_pct), 2),
                'time': datetime.now(self.et_tz).strftime('%Y-%m-%d %I:%M %p ET'),
                'volume': premarket_volume
            }
            
        except Exception as e:
            print(f"❌ Error fetching pre-market for {symbol}: {e}")
            return None
    
    def analyze_gap(self, symbol: str, gap_data: Dict) -> Dict:
        """
        Analyze gap and provide recommendation
        
        Returns:
        {
            'gap_type': 'gap_down',
            'gap_category': 'common',  # common/breakaway/runaway/exhaustion
            'severity': 'warning',
            'near_stop': True,
            'below_stop': False,
            'distance_from_stop_pct': 0.10,
            'distance_from_stop_dollars': 0.33,
            'recommendation': 'WATCH CLOSELY - Consider exit at open',
            'action': 'PREPARE_TO_EXIT',  # HOLD/WATCH/PREPARE_TO_EXIT/EXIT_NOW
            'risk_level': 'HIGH'
        }
        """
        change_pct = gap_data['change_pct']
        premarket = gap_data['premarket_price']
        
        position = self.positions.get(symbol, {})
        stop_loss = position.get('stop_loss')
        entry = position.get('avg_entry')
        shares = position.get('shares', 0)
        
        # Determine gap type
        if abs(change_pct) < 0.5:
            gap_type = 'no_gap'
            gap_category = 'none'
        elif change_pct > 0:
            gap_type = 'gap_up'
            # Categorize gap
            if abs(change_pct) > 5:
                gap_category = 'breakaway'  # Major move
            elif abs(change_pct) > 2:
                gap_category = 'runaway'    # Continuation
            else:
                gap_category = 'common'      # Small gap
        else:
            gap_type = 'gap_down'
            if abs(change_pct) > 5:
                gap_category = 'breakaway'
            elif abs(change_pct) > 2:
                gap_category = 'runaway'
            else:
                gap_category = 'common'
        
        # Determine severity
        abs_change = abs(change_pct)
        if abs_change > 5:
            severity = 'critical'
        elif abs_change > 2:
            severity = 'high'
        elif abs_change > 1:
            severity = 'warning'
        elif abs_change > 0.5:
            severity = 'moderate'
        else:
            severity = 'low'
        
        # Check position against stop loss
        near_stop = False
        below_stop = False
        distance_from_stop_pct = None
        distance_from_stop_dollars = None
        potential_loss = None
        
        if stop_loss:
            distance_from_stop_dollars = premarket - stop_loss
            distance_from_stop_pct = (distance_from_stop_dollars / stop_loss) * 100
            
            below_stop = distance_from_stop_dollars < 0
            near_stop = abs(distance_from_stop_pct) < 1.0  # Within 1% of stop
            
            # Calculate potential loss if stopped
            if entry:
                loss_per_share = stop_loss - entry
                potential_loss = loss_per_share * shares
        
        # Generate recommendation and action
        recommendation, action = self._generate_recommendation(
            gap_type, gap_category, severity, near_stop, below_stop, 
            distance_from_stop_pct, position
        )
        
        # Assess risk level
        risk_level = self._assess_risk(severity, near_stop, below_stop, gap_type)
        
        return {
            'gap_type': gap_type,
            'gap_category': gap_category,
            'severity': severity,
            'near_stop': near_stop,
            'below_stop': below_stop,
            'distance_from_stop_pct': round(distance_from_stop_pct, 2) if distance_from_stop_pct else None,
            'distance_from_stop_dollars': round(distance_from_stop_dollars, 2) if distance_from_stop_dollars else None,
            'potential_loss': round(potential_loss, 2) if potential_loss else None,
            'recommendation': recommendation,
            'action': action,
            'risk_level': risk_level
        }
    
    def _generate_recommendation(self, gap_type, gap_category, severity, 
                                 near_stop, below_stop, distance_from_stop_pct, 
                                 position):
        """
        Generate actionable recommendation
        
        Returns: (recommendation_text, action_code)
        """
        
        # No gap - normal monitoring
        if gap_type == 'no_gap':
            return "✅ No significant gap. Monitor normally.", "HOLD"
        
        # Gap UP scenarios
        if gap_type == 'gap_up':
            if gap_category == 'breakaway':
                return ("🚀 STRONG BREAKAWAY GAP UP! Consider taking partial profits at open. "
                       "This gap likely won't fill."), "TAKE_PROFIT"
            elif severity == 'high':
                return ("📈 Nice gap up. Consider moving stop to breakeven or taking partial profits."), "CONSIDER_PROFIT"
            elif severity == 'warning':
                return "📈 Small gap up. Hold and let it run. Monitor for continuation.", "HOLD"
            else:
                return "✅ Tiny gap up. Continue normal monitoring.", "HOLD"
        
        # Gap DOWN scenarios
        if not position:
            return f"📉 Gap down detected ({gap_category}). No position tracked.", "NONE"
        
        # Below stop loss - immediate action needed
        if below_stop:
            loss_dollars = abs(distance_from_stop_pct * position.get('stop_loss', 0) / 100 * position.get('shares', 0))
            return (f"🚨 BELOW YOUR STOP LOSS! Exit immediately at market open. "
                   f"Expected additional loss: ~${loss_dollars:.2f}"), "EXIT_NOW"
        
        # Very near stop loss
        if near_stop:
            if distance_from_stop_pct and distance_from_stop_pct < 0.3:
                return ("🚨 EXTREMELY CLOSE TO STOP! Be at your computer at 9:25 AM. "
                       "Prepare to sell at market open."), "PREPARE_TO_EXIT"
            else:
                return ("⚠️  APPROACHING STOP LOSS! Watch closely. "
                       "Be ready to exit at open if breaks lower."), "WATCH_CLOSELY"
        
        # Significant gap down but not near stop
        if gap_category == 'breakaway':
            return ("🚨 MAJOR BREAKAWAY GAP DOWN! Support likely broken. "
                   "Consider exiting before regular stop is hit."), "CONSIDER_EXIT"
        elif severity == 'high':
            return ("⚠️  Significant gap down. Monitor closely. "
                   "Your stop will protect you if it continues lower."), "WATCH_CLOSELY"
        elif severity == 'warning':
            return ("📉 Moderate gap down. Your stop is safely below. "
                   "Monitor and let stop loss work if needed."), "MONITOR"
        else:
            return "📉 Small gap down. Stop loss protects you. Continue monitoring.", "HOLD"
    
    def _assess_risk(self, severity, near_stop, below_stop, gap_type):
        """Assess overall risk level"""
        
        if below_stop:
            return 'CRITICAL'
        
        if gap_type == 'gap_down':
            if near_stop and severity in ['critical', 'high']:
                return 'CRITICAL'
            elif near_stop or severity == 'critical':
                return 'HIGH'
            elif severity in ['high', 'warning']:
                return 'MEDIUM'
            else:
                return 'LOW'
        else:  # gap_up or no_gap
            return 'LOW'
    
    def monitor_all_positions(self) -> List[Dict]:
        """
        Monitor all positions and return alerts
        
        Returns list of alerts for Telegram
        """
        alerts = []
        
        print(f"📊 Monitoring {len(self.positions)} position(s)...")
        
        for symbol in self.positions.keys():
            print(f"   Fetching {symbol}...")
            gap_data = self.get_premarket_price(symbol)
            
            if not gap_data:
                print(f"   ⚠️  Skipping {symbol} (no data)")
                continue
            
            analysis = self.analyze_gap(symbol, gap_data)
            
            # Combine data and analysis
            alert = {**gap_data, **analysis}
            alert['position'] = self.positions[symbol]
            
            alerts.append(alert)
            print(f"   ✅ {symbol}: {gap_data['change_pct']:+.2f}% - {analysis['risk_level']}")
        
        return alerts


# Example usage and testing
if __name__ == '__main__':
    print("="*80)
    print("PRE-MARKET MONITOR TEST")
    print("="*80)
    
    # Sample positions (update with your actual trades)
    test_positions = {
        'AAPL': {
            'shares': 10,
            'avg_entry': 230.00,
            'stop_loss': 225.00,
            'target1': 240.00,
            'target2': 250.00
        },
        'MSFT': {
            'shares': 5,
            'avg_entry': 420.00,
            'stop_loss': 410.00,
            'target1': 440.00
        }
    }
    
    monitor = PreMarketMonitor(test_positions)
    
    # Check if we're in pre-market hours
    if not monitor.is_premarket_hours():
        print("\n⚠️  Not currently in pre-market hours (4-9:30 AM ET, Mon-Fri)")
        print("Running test anyway with latest available data...\n")
    
    # Monitor all positions
    alerts = monitor.monitor_all_positions()
    
    # Display results
    print("\n" + "="*80)
    print("ALERTS")
    print("="*80)
    
    if not alerts:
        print("No alerts generated.")
    else:
        for alert in alerts:
            print(f"\n{alert['symbol']}:")
            print(f"  Pre-Market: ${alert['premarket_price']} ({alert['change_pct']:+.2f}%)")
            print(f"  Previous Close: ${alert['previous_close']}")
            print(f"  Gap Type: {alert['gap_type']} ({alert['gap_category']})")
            print(f"  Risk Level: {alert['risk_level']}")
            
            if alert['distance_from_stop_pct'] is not None:
                print(f"  Distance from Stop: {alert['distance_from_stop_pct']:+.2f}%")
            
            print(f"  📋 {alert['recommendation']}")
    
    print("\n" + "="*80)
    print("Test complete!")

