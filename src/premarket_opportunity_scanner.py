"""
Pre-Market Opportunity Scanner
Scans for BUY opportunities based on gaps (both gap downs and gap ups)
"""

import yfinance as yf
from typing import Dict, List, Optional
from datetime import datetime
import pytz


class PreMarketOpportunityScanner:
    """Scan stocks for gap-based buying opportunities"""
    
    def __init__(self, symbols_to_scan: List[str] = None):
        """
        Initialize scanner
        
        Args:
            symbols_to_scan: List of symbols to scan (default: None = scan S&P 500)
        """
        self.symbols_to_scan = symbols_to_scan or []
        self.et_tz = pytz.timezone('America/New_York')
    
    def get_gap_data(self, symbol: str) -> Optional[Dict]:
        """
        Get gap data for a symbol
        
        Returns:
        {
            'symbol': 'AAPL',
            'current_price': 220.50,
            'previous_close': 230.00,
            'gap_pct': -4.13,
            'gap_dollars': -9.50,
            'volume': 125000  # pre-market volume
        }
        """
        try:
            ticker = yf.Ticker(symbol)
            
            # Get pre-market data
            data = ticker.history(period='1d', interval='1m', prepost=True)
            
            if data.empty:
                return None
            
            current_price = data['Close'].iloc[-1]
            
            # Get previous close
            info = ticker.info
            previous_close = info.get('previousClose') or info.get('regularMarketPreviousClose')
            
            if not previous_close:
                return None
            
            # Calculate gap
            gap_dollars = current_price - previous_close
            gap_pct = (gap_dollars / previous_close) * 100
            
            # Pre-market volume
            now_et = datetime.now(self.et_tz)
            market_open = now_et.replace(hour=9, minute=30, second=0, microsecond=0)
            premarket_data = data[data.index < market_open]
            volume = int(premarket_data['Volume'].sum()) if not premarket_data.empty else 0
            
            return {
                'symbol': symbol,
                'current_price': round(float(current_price), 2),
                'previous_close': round(float(previous_close), 2),
                'gap_pct': round(float(gap_pct), 2),
                'gap_dollars': round(float(gap_dollars), 2),
                'volume': volume
            }
        
        except Exception as e:
            print(f"   ⚠️  Error fetching {symbol}: {e}")
            return None
    
    def get_fundamentals_quick(self, symbol: str) -> Optional[Dict]:
        """
        Get quick fundamental check
        
        Returns:
        {
            'pe_ratio': 25.3,
            'market_cap': 2500000000000,
            'profit_margins': 0.25,
            'analyst_rating': 'buy'
        }
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            return {
                'pe_ratio': info.get('trailingPE'),
                'forward_pe': info.get('forwardPE'),
                'market_cap': info.get('marketCap'),
                'profit_margins': info.get('profitMargins'),
                'revenue_growth': info.get('revenueGrowth'),
                'recommendation': info.get('recommendationKey'),
                '52w_high': info.get('fiftyTwoWeekHigh'),
                '52w_low': info.get('fiftyTwoWeekLow')
            }
        
        except Exception as e:
            return None
    
    def score_gap_down_opportunity(self, gap_data: Dict, fundamentals: Dict) -> Dict:
        """
        Score a gap down as a potential buying opportunity
        
        Criteria:
        - Gap down 2-10% (oversold but not disaster)
        - Strong fundamentals
        - Not at 52W low (catching falling knife)
        - Decent volume (liquidity)
        
        Returns:
        {
            'opportunity_type': 'GAP_DOWN_OVERSOLD',
            'score': 75,
            'confidence': 'HIGH',
            'entry': 220.00,
            'stop': 215.00,
            'target': 230.00,
            'risk_reward': 2.0,
            'reason': 'Oversold on temporary news...'
        }
        """
        score = 0
        reasons = []
        
        gap_pct = abs(gap_data['gap_pct'])
        current = gap_data['current_price']
        prev_close = gap_data['previous_close']
        
        # Gap size (2-10% is ideal)
        if 2 <= gap_pct <= 4:
            score += 25
            reasons.append(f"Ideal gap down ({gap_pct:.1f}%)")
        elif 4 < gap_pct <= 7:
            score += 20
            reasons.append(f"Moderate gap down ({gap_pct:.1f}%)")
        elif 7 < gap_pct <= 10:
            score += 15
            reasons.append(f"Large gap down ({gap_pct:.1f}%)")
        elif gap_pct > 10:
            score += 5
            reasons.append(f"Very large gap ({gap_pct:.1f}%) - risky")
        
        # Fundamentals check
        if fundamentals:
            # Profit margins
            if fundamentals.get('profit_margins') and fundamentals['profit_margins'] > 0.15:
                score += 15
                reasons.append("Strong profit margins")
            elif fundamentals.get('profit_margins') and fundamentals['profit_margins'] > 0.08:
                score += 10
            
            # P/E ratio (not too expensive)
            pe = fundamentals.get('pe_ratio') or fundamentals.get('forward_pe')
            if pe and 10 < pe < 30:
                score += 15
                reasons.append("Reasonable valuation")
            elif pe and pe < 50:
                score += 8
            
            # Revenue growth
            if fundamentals.get('revenue_growth') and fundamentals['revenue_growth'] > 0.1:
                score += 10
                reasons.append("Growing revenue")
            
            # Analyst recommendation
            rec = fundamentals.get('recommendation')
            if rec in ['strong_buy', 'buy']:
                score += 15
                reasons.append(f"Analysts say {rec.replace('_', ' ')}")
            elif rec == 'hold':
                score += 5
            
            # Distance from 52W low (avoid catching falling knife)
            low_52w = fundamentals.get('52w_low')
            if low_52w and current > low_52w * 1.2:  # At least 20% above 52W low
                score += 10
                reasons.append("Well above 52W low")
            elif low_52w and current <= low_52w * 1.1:  # Within 10% of 52W low
                score -= 10
                reasons.append("Near 52W low (risky)")
        
        # Volume (liquidity check)
        if gap_data['volume'] > 50000:
            score += 10
            reasons.append("Good pre-market volume")
        
        # Calculate entry/stop/target
        entry = current
        stop = current * 0.97  # 3% stop
        target = prev_close  # Gap fill target
        
        risk = entry - stop
        reward = target - entry
        risk_reward = reward / risk if risk > 0 else 0
        
        # Determine confidence
        if score >= 70:
            confidence = 'HIGH'
        elif score >= 50:
            confidence = 'MEDIUM'
        else:
            confidence = 'LOW'
        
        return {
            'opportunity_type': 'GAP_DOWN_OVERSOLD',
            'score': min(score, 100),
            'confidence': confidence,
            'entry': round(entry, 2),
            'stop': round(stop, 2),
            'target': round(target, 2),
            'risk_reward': round(risk_reward, 2),
            'gap_pct': gap_pct,
            'reasons': reasons
        }
    
    def score_gap_up_opportunity(self, gap_data: Dict, fundamentals: Dict) -> Dict:
        """
        Score a gap up as a potential breakout/continuation buy
        
        Criteria:
        - Gap up 3-8% (strong move but not parabolic)
        - Strong fundamentals
        - High volume (conviction)
        - Not at 52W high (room to run)
        
        Returns similar to score_gap_down_opportunity
        """
        score = 0
        reasons = []
        
        gap_pct = gap_data['gap_pct']
        current = gap_data['current_price']
        prev_close = gap_data['previous_close']
        
        # Gap size (3-8% is ideal for continuation)
        if 3 <= gap_pct <= 5:
            score += 25
            reasons.append(f"Strong gap up ({gap_pct:.1f}%)")
        elif 5 < gap_pct <= 8:
            score += 20
            reasons.append(f"Very strong gap up ({gap_pct:.1f}%)")
        elif gap_pct > 8:
            score += 10
            reasons.append(f"Parabolic gap ({gap_pct:.1f}%) - risky")
        elif 1 <= gap_pct < 3:
            score += 15
            reasons.append(f"Moderate gap up ({gap_pct:.1f}%)")
        
        # Fundamentals
        if fundamentals:
            # Strong fundamentals = more likely to continue
            if fundamentals.get('profit_margins') and fundamentals['profit_margins'] > 0.15:
                score += 15
                reasons.append("Strong margins support move")
            
            # Revenue growth
            if fundamentals.get('revenue_growth') and fundamentals['revenue_growth'] > 0.15:
                score += 15
                reasons.append("Strong revenue growth")
            
            # Analyst recommendation
            rec = fundamentals.get('recommendation')
            if rec in ['strong_buy', 'buy']:
                score += 15
                reasons.append("Analyst support")
            
            # Room to run (not at 52W high)
            high_52w = fundamentals.get('52w_high')
            if high_52w:
                distance_from_high = ((high_52w - current) / high_52w) * 100
                if distance_from_high > 10:  # More than 10% below 52W high
                    score += 15
                    reasons.append(f"{distance_from_high:.1f}% below 52W high")
                elif distance_from_high < 3:  # Within 3% of 52W high
                    score += 5
                    reasons.append("Near 52W high (limited upside)")
        
        # Volume (high volume = conviction)
        if gap_data['volume'] > 100000:
            score += 15
            reasons.append("Strong volume conviction")
        elif gap_data['volume'] > 50000:
            score += 10
        
        # Calculate entry/stop/target (for gap up continuation)
        entry = current
        stop = prev_close  # Stop below gap
        target = current * 1.08  # 8% upside target
        
        risk = entry - stop
        reward = target - entry
        risk_reward = reward / risk if risk > 0 else 0
        
        # Determine confidence
        if score >= 70:
            confidence = 'HIGH'
        elif score >= 50:
            confidence = 'MEDIUM'
        else:
            confidence = 'LOW'
        
        return {
            'opportunity_type': 'GAP_UP_BREAKOUT',
            'score': min(score, 100),
            'confidence': confidence,
            'entry': round(entry, 2),
            'stop': round(stop, 2),
            'target': round(target, 2),
            'risk_reward': round(risk_reward, 2),
            'gap_pct': gap_pct,
            'reasons': reasons
        }
    
    def scan_for_opportunities(self, min_gap_pct: float = 2.0, 
                              max_symbols: int = 10) -> List[Dict]:
        """
        Scan symbols for gap opportunities
        
        Args:
            min_gap_pct: Minimum gap percentage to consider (default 2%)
            max_symbols: Maximum opportunities to return
        
        Returns:
            List of opportunities sorted by score
        """
        opportunities = []
        
        print(f"\n🔍 Scanning {len(self.symbols_to_scan)} symbols for gap opportunities...")
        print(f"   (Looking for gaps >= {min_gap_pct}%)")
        
        for symbol in self.symbols_to_scan:
            # Get gap data
            gap_data = self.get_gap_data(symbol)
            
            if not gap_data:
                continue
            
            abs_gap = abs(gap_data['gap_pct'])
            
            # Skip small gaps
            if abs_gap < min_gap_pct:
                continue
            
            print(f"   Found: {symbol} gap {gap_data['gap_pct']:+.2f}%")
            
            # Get fundamentals
            fundamentals = self.get_fundamentals_quick(symbol)
            
            # Score based on gap direction
            if gap_data['gap_pct'] < 0:  # Gap down
                analysis = self.score_gap_down_opportunity(gap_data, fundamentals)
            else:  # Gap up
                analysis = self.score_gap_up_opportunity(gap_data, fundamentals)
            
            # Combine data
            opportunity = {
                **gap_data,
                **analysis,
                'fundamentals': fundamentals
            }
            
            opportunities.append(opportunity)
        
        # Sort by score (highest first)
        opportunities.sort(key=lambda x: x['score'], reverse=True)
        
        # Return top N
        return opportunities[:max_symbols]


# Example usage and testing
if __name__ == '__main__':
    print("="*80)
    print("PRE-MARKET OPPORTUNITY SCANNER TEST")
    print("="*80)
    
    # Test with a few symbols (you'd use full S&P 500 list in production)
    test_symbols = ['AAPL', 'MSFT', 'NVDA', 'TSLA', 'GOOGL', 'AMZN', 'META', 'NFLX']
    
    scanner = PreMarketOpportunityScanner(test_symbols)
    opportunities = scanner.scan_for_opportunities(min_gap_pct=1.0, max_symbols=5)
    
    print("\n" + "="*80)
    print("TOP OPPORTUNITIES")
    print("="*80)
    
    if not opportunities:
        print("\n✅ No significant gaps found (all stocks trading normally)")
    else:
        for i, opp in enumerate(opportunities, 1):
            print(f"\n{i}. {opp['symbol']} - Score: {opp['score']}/100")
            print(f"   Type: {opp['opportunity_type']}")
            print(f"   Gap: {opp['gap_pct']:+.2f}% (${opp['previous_close']:.2f} → ${opp['current_price']:.2f})")
            print(f"   Confidence: {opp['confidence']}")
            print(f"   Entry: ${opp['entry']:.2f}")
            print(f"   Stop: ${opp['stop']:.2f}")
            print(f"   Target: ${opp['target']:.2f}")
            print(f"   Risk/Reward: 1:{opp['risk_reward']:.1f}")
            print(f"   Reasons:")
            for reason in opp['reasons']:
                print(f"     • {reason}")
    
    print("\n" + "="*80)
    print("Test complete!")

