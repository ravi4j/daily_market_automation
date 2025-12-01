"""
Pre-Market Opportunity Scanner
Scans for BUY opportunities based on gaps (both gap downs and gap ups)
"""

import yfinance as yf
from typing import Dict, List, Optional
from datetime import datetime
import pytz
from pathlib import Path


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

    def get_gap_data(self, symbol: str, debug: bool = False) -> Optional[Dict]:
        """
        Get gap data for a symbol
        
        FIXED: Uses daily OHLC data instead of 1-minute candles
        Gap = Today's Open - Yesterday's Close (the true gap definition)

        Returns:
        {
            'symbol': 'AAPL',
            'current_price': 220.50,    # Today's latest price
            'previous_close': 230.00,   # Yesterday's actual close
            'today_open': 225.00,       # Today's open (where gap occurred)
            'gap_pct': -2.17,           # (today_open - yesterday_close) / yesterday_close
            'gap_dollars': -5.00,
            'volume': 1250000           # Today's volume
        }
        """
        try:
            ticker = yf.Ticker(symbol)

            # Get last 5 days of DAILY data (handles weekends/holidays)
            data = ticker.history(period='5d', interval='1d')

            if data.empty or len(data) < 2:
                if debug:
                    print(f"   ⚠️  {symbol}: Insufficient data (need at least 2 days)")
                return None

            # Get yesterday's ACTUAL close (last complete trading day)
            previous_close = data['Close'].iloc[-2]
            previous_date = data.index[-2].strftime('%Y-%m-%d')

            # Get today's open and current price
            today_open = data['Open'].iloc[-1]
            today_high = data['High'].iloc[-1]
            today_low = data['Low'].iloc[-1]
            current_price = data['Close'].iloc[-1]
            today_volume = data['Volume'].iloc[-1]
            today_date = data.index[-1].strftime('%Y-%m-%d')

            # Calculate gap (TODAY'S OPEN vs YESTERDAY'S CLOSE)
            # This is the true definition of a gap!
            gap_dollars = today_open - previous_close
            gap_pct = (gap_dollars / previous_close) * 100

            # Calculate intraday movement (current vs open)
            intraday_change = current_price - today_open
            intraday_pct = (intraday_change / today_open) * 100

            # DEBUG LOGGING
            if debug or abs(gap_pct) >= 2.0:
                print(f"\n   📊 GAP DATA FOR {symbol}:")
                print(f"      Data Source: Daily OHLC (period='5d', interval='1d')")
                print(f"      Yesterday ({previous_date}):")
                print(f"        - Close: ${previous_close:.2f}")
                print(f"      Today ({today_date}):")
                print(f"        - Open:  ${today_open:.2f}")
                print(f"        - High:  ${today_high:.2f}")
                print(f"        - Low:   ${today_low:.2f}")
                print(f"        - Close: ${current_price:.2f}")
                print(f"        - Volume: {today_volume:,}")
                print(f"      Gap Calculation:")
                print(f"        - Gap $: ${gap_dollars:+.2f}")
                print(f"        - Gap %: {gap_pct:+.2f}%")
                print(f"        - Formula: (${today_open:.2f} - ${previous_close:.2f}) / ${previous_close:.2f} × 100")
                print(f"      Intraday Move:")
                print(f"        - Change: ${intraday_change:+.2f} ({intraday_pct:+.2f}%)")

            return {
                'symbol': symbol,
                'current_price': round(float(current_price), 2),
                'previous_close': round(float(previous_close), 2),
                'today_open': round(float(today_open), 2),
                'today_high': round(float(today_high), 2),
                'today_low': round(float(today_low), 2),
                'gap_pct': round(float(gap_pct), 2),
                'gap_dollars': round(float(gap_dollars), 2),
                'intraday_pct': round(float(intraday_pct), 2),
                'volume': int(today_volume),
                'previous_date': previous_date,
                'today_date': today_date
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
        today_open = gap_data['today_open']  # Entry point is the gap open
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
        # Entry is where the gap opened (today's open), not current price
        entry = today_open
        stop = today_open * 0.97  # 3% stop below entry
        target = prev_close  # Gap fill target (yesterday's close)

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
        today_open = gap_data['today_open']  # Entry point is the gap open
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
        # Entry is where the gap opened (today's open), not current price
        entry = today_open
        stop = prev_close  # Stop below gap (yesterday's close)
        target = today_open * 1.08  # 8% upside target from gap open

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

    def scan_for_opportunities(self, symbols: List[str] = None, min_gap_pct: float = 2.0,
                              max_opportunities: int = 10, debug: bool = True) -> List[Dict]:
        """
        Scan symbols for gap opportunities

        Args:
            symbols: List of symbols to scan (overrides self.symbols_to_scan if provided)
            min_gap_pct: Minimum gap percentage to consider (default 2%)
            max_opportunities: Maximum opportunities to return
            debug: Enable detailed logging (default True)

        Returns:
            List of opportunities sorted by score
        """
        # Use provided symbols or fall back to initialized list
        scan_symbols = symbols if symbols is not None else self.symbols_to_scan
        opportunities = []

        print(f"\n🔍 Scanning {len(scan_symbols)} symbols for gap opportunities...")
        print(f"   (Looking for gaps >= {min_gap_pct}%)")
        if debug:
            print(f"   📝 Debug logging: ENABLED (will show gap calculation details)")

        for symbol in scan_symbols:
            # Get gap data (with debug logging)
            gap_data = self.get_gap_data(symbol, debug=debug)

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

        print(f"✅ Found {len(opportunities)} opportunities (returning top {max_opportunities})")

        # Save gap data log to file
        if opportunities and debug:
            self._save_gap_log(opportunities[:max_opportunities])

        # Return top N
        return opportunities[:max_opportunities]
    
    def _save_gap_log(self, opportunities: List[Dict]):
        """Save detailed gap calculation log to file for verification"""
        try:
            log_dir = Path(__file__).parent.parent / 'logs'
            log_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            log_file = log_dir / f'gap_calculation_{timestamp}.log'
            
            with open(log_file, 'w') as f:
                f.write("="*80 + "\n")
                f.write("GAP CALCULATION VERIFICATION LOG\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("="*80 + "\n\n")
                
                for i, opp in enumerate(opportunities, 1):
                    f.write(f"{i}. {opp['symbol']} - {opp.get('opportunity_type', 'UNKNOWN')}\n")
                    f.write(f"   {'='*70}\n")
                    f.write(f"   Data Source: Daily OHLC (period='5d', interval='1d')\n")
                    f.write(f"   \n")
                    f.write(f"   Previous Day ({opp.get('previous_date', 'N/A')}):\n")
                    f.write(f"     Close: ${opp.get('previous_close', 0):.2f}\n")
                    f.write(f"   \n")
                    f.write(f"   Today ({opp.get('today_date', 'N/A')}):\n")
                    f.write(f"     Open:  ${opp.get('today_open', 0):.2f}\n")
                    f.write(f"     High:  ${opp.get('today_high', 0):.2f}\n")
                    f.write(f"     Low:   ${opp.get('today_low', 0):.2f}\n")
                    f.write(f"     Close: ${opp.get('current_price', 0):.2f}\n")
                    f.write(f"     Volume: {opp.get('volume', 0):,}\n")
                    f.write(f"   \n")
                    f.write(f"   Gap Calculation:\n")
                    prev_close = opp.get('previous_close', 0)
                    today_open = opp.get('today_open', 0)
                    gap_pct = opp.get('gap_pct', 0)
                    f.write(f"     Formula: (Today_Open - Yesterday_Close) / Yesterday_Close × 100\n")
                    f.write(f"     Formula: (${today_open:.2f} - ${prev_close:.2f}) / ${prev_close:.2f} × 100\n")
                    f.write(f"     Gap $: ${opp.get('gap_dollars', 0):+.2f}\n")
                    f.write(f"     Gap %: {gap_pct:+.2f}%\n")
                    f.write(f"   \n")
                    f.write(f"   Trade Setup:\n")
                    f.write(f"     Entry:  ${opp.get('entry', 0):.2f} (gap open price)\n")
                    f.write(f"     Target: ${opp.get('target', 0):.2f}\n")
                    f.write(f"     Stop:   ${opp.get('stop', 0):.2f}\n")
                    f.write(f"     Score:  {opp.get('score', 0):.0f}/100\n")
                    f.write(f"     R/R:    {opp.get('risk_reward', 0):.2f}:1\n")
                    f.write(f"\n")
                
                f.write("="*80 + "\n")
                f.write("END OF LOG\n")
                f.write("="*80 + "\n")
            
            print(f"\n📝 Gap calculation log saved to: {log_file}")
            
        except Exception as e:
            print(f"   ⚠️  Could not save gap log: {e}")


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
