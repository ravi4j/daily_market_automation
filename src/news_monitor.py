#!/usr/bin/env python3
"""
Yahoo Finance News Monitor - Identifies buying opportunities from market news
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import re
import os
import sys

# Import correlation tracker (optional - degrades gracefully if not available)
try:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from src.news_correlation import NewsCorrelationTracker
    CORRELATION_AVAILABLE = True
except ImportError:
    CORRELATION_AVAILABLE = False

# Import FinBERT sentiment analyzer (optional - falls back to keywords)
try:
    from src.finbert_sentiment import get_sentiment_analyzer
    FINBERT_AVAILABLE = True
except ImportError:
    FINBERT_AVAILABLE = False

class NewsMonitor:
    """Monitor Yahoo Finance news for trading opportunities"""

    def __init__(self, enable_correlation: bool = True, use_finbert: bool = True):
        # Keywords indicating potential buying opportunities
        self.opportunity_keywords = [
            'falls', 'drops', 'plunges', 'tumbles', 'declines', 'selloff', 'sell-off',
            'misses', 'miss', 'disappoints', 'downgrade', 'concern', 'worry',
            'slump', 'slide', 'tank', 'crash', 'correction', 'pullback'
        ]

        # Keywords to filter out (avoid catching knives)
        self.avoid_keywords = [
            'bankruptcy', 'fraud', 'scandal', 'investigation', 'lawsuit',
            'delisting', 'sec investigation', 'accounting issues', 'chapter 11'
        ]

        # Initialize correlation tracker (optional)
        self.correlation_tracker = None
        if enable_correlation and CORRELATION_AVAILABLE:
            try:
                self.correlation_tracker = NewsCorrelationTracker()
            except Exception as e:
                print(f"⚠️  Correlation tracking disabled: {e}")

        # Initialize FinBERT sentiment analyzer (optional)
        self.use_finbert = use_finbert and FINBERT_AVAILABLE
        self.sentiment_analyzer = None

        if self.use_finbert:
            try:
                print("🤖 Initializing FinBERT sentiment analyzer...")
                self.sentiment_analyzer = get_sentiment_analyzer(use_finbert=True)
                print("✅ FinBERT ready")
            except Exception as e:
                print(f"⚠️  FinBERT initialization failed: {e}")
                print("   Using keyword-based sentiment")
                self.use_finbert = False

    def fetch_news(self, symbol: str) -> List[Dict]:
        """Fetch recent news for a symbol"""
        try:
            ticker = yf.Ticker(symbol)
            news = ticker.news  # Returns list of news articles

            if not news:
                return []

            # Parse and structure news
            articles = []
            for article in news[:10]:  # Get last 10 articles
                articles.append({
                    'symbol': symbol,
                    'title': article.get('title', ''),
                    'publisher': article.get('publisher', ''),
                    'link': article.get('link', ''),
                    'published': datetime.fromtimestamp(article.get('providerPublishTime', 0)),
                    'type': article.get('type', 'STORY'),
                })

            return articles
        except Exception as e:
            print(f"Error fetching news for {symbol}: {e}")
            return []

    def analyze_sentiment(self, article: Dict) -> Dict:
        """Analyze if article indicates a buying opportunity"""
        title = article['title']
        title_lower = title.lower()

        # Use FinBERT if available, otherwise fall back to keywords
        if self.use_finbert and self.sentiment_analyzer:
            return self._analyze_with_finbert(article)
        else:
            return self._analyze_with_keywords(article)

    def _analyze_with_finbert(self, article: Dict) -> Dict:
        """Analyze sentiment using FinBERT ML model"""
        title = article['title']
        title_lower = title.lower()

        try:
            # Get ML-based sentiment
            sentiment_result = self.sentiment_analyzer.analyze(title)

            # Check if it's negative sentiment (potential buying opportunity)
            is_negative = sentiment_result['sentiment'] == 'negative'
            confidence = sentiment_result['confidence']

            # Still filter out serious issues with keywords
            has_serious_issue = any(
                keyword in title_lower for keyword in self.avoid_keywords
            )

            if has_serious_issue:
                return {
                    'is_opportunity': False,
                    'reason': 'Serious issue detected',
                    'sentiment': 'very_negative',
                    'sentiment_score': -50,
                    'confidence': confidence,
                    'method': 'finbert',
                    'probabilities': sentiment_result['probabilities']
                }

            # Negative sentiment = buying opportunity
            if is_negative and confidence > 0.60:  # High confidence negative
                sentiment_score = int(-25 - (confidence * 25))  # -25 to -50
                return {
                    'is_opportunity': True,
                    'reason': 'ML-detected negative sentiment (high confidence)',
                    'sentiment': 'negative',
                    'sentiment_score': sentiment_score,
                    'confidence': confidence,
                    'method': 'finbert',
                    'probabilities': sentiment_result['probabilities']
                }
            elif is_negative:  # Medium confidence negative
                sentiment_score = int(-25 - (confidence * 25))
                return {
                    'is_opportunity': True,
                    'reason': 'ML-detected negative sentiment',
                    'sentiment': 'negative',
                    'sentiment_score': sentiment_score,
                    'confidence': confidence,
                    'method': 'finbert',
                    'probabilities': sentiment_result['probabilities']
                }
            else:
                # Not negative = not an opportunity
                sentiment_score = self.sentiment_analyzer.get_sentiment_score(title)
                return {
                    'is_opportunity': False,
                    'reason': f"Sentiment: {sentiment_result['sentiment']}",
                    'sentiment': sentiment_result['sentiment'],
                    'sentiment_score': sentiment_score,
                    'confidence': confidence,
                    'method': 'finbert',
                    'probabilities': sentiment_result['probabilities']
                }

        except Exception as e:
            print(f"⚠️  FinBERT analysis failed for '{title}': {e}")
            print("   Falling back to keyword analysis")
            return self._analyze_with_keywords(article)

    def _analyze_with_keywords(self, article: Dict) -> Dict:
        """Analyze sentiment using keyword matching (fallback)"""
        title_lower = article['title'].lower()

        # Check if it's negative news (potential dip)
        has_opportunity_signal = any(
            keyword in title_lower for keyword in self.opportunity_keywords
        )

        # Check if it's something to avoid
        has_red_flag = any(
            keyword in title_lower for keyword in self.avoid_keywords
        )

        # Extract percentage drops from title (e.g., "Stock falls 15%")
        drop_match = re.search(r'(\d+(?:\.\d+)?)\s*%', title_lower)
        drop_percentage = float(drop_match.group(1)) if drop_match else None

        # Determine reason
        if has_red_flag:
            reason = "Serious issue - avoid"
        elif has_opportunity_signal:
            reason = "Negative keyword detected"
        else:
            reason = "No opportunity signal"

        return {
            'is_opportunity': has_opportunity_signal and not has_red_flag,
            'reason': reason,
            'sentiment': 'negative' if has_opportunity_signal else 'neutral',
            'sentiment_score': self._calculate_sentiment_score(title_lower, drop_percentage),
            'confidence': 0.75 if has_opportunity_signal else 0.50,
            'method': 'keyword',
            'probabilities': None,
            'has_red_flag': has_red_flag,
            'drop_percentage': drop_percentage
        }

    def _calculate_sentiment_score(self, title: str, drop_pct: float = None) -> int:
        """Score from -100 (very negative) to 100 (very positive)"""
        score = 0

        # Negative keywords impact
        for keyword in self.opportunity_keywords:
            if keyword in title:
                score -= 10

        # Red flags are very negative
        for keyword in self.avoid_keywords:
            if keyword in title:
                score -= 50

        # Larger drops = more negative sentiment
        if drop_pct:
            score -= int(drop_pct * 2)  # 10% drop = -20 points

        return max(-100, min(100, score))

    def get_stock_fundamentals(self, symbol: str) -> Dict:
        """Get key fundamentals to assess if dip is a buying opportunity"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            hist = ticker.history(period='6mo')

            if hist.empty:
                return None

            current_price = hist['Close'].iloc[-1]
            week_high_52 = info.get('fiftyTwoWeekHigh', current_price)
            week_low_52 = info.get('fiftyTwoWeekLow', current_price)

            # Calculate how far from 52-week high
            distance_from_high = ((week_high_52 - current_price) / week_high_52) * 100 if week_high_52 else 0

            # Recent price change (5 days)
            price_5d_ago = hist['Close'].iloc[-5] if len(hist) >= 5 else current_price
            change_5d = ((current_price - price_5d_ago) / price_5d_ago) * 100 if price_5d_ago else 0

            return {
                'symbol': symbol,
                'company_name': info.get('longName', info.get('shortName', symbol)),
                'current_price': round(float(current_price), 2),
                'market_cap': info.get('marketCap', 0),
                'pe_ratio': info.get('trailingPE', None),
                'forward_pe': info.get('forwardPE', None),
                'peg_ratio': info.get('pegRatio', None),
                'profit_margins': info.get('profitMargins', None),
                'revenue_growth': info.get('revenueGrowth', None),
                '52w_high': round(float(week_high_52), 2) if week_high_52 else None,
                '52w_low': round(float(week_low_52), 2) if week_low_52 else None,
                'distance_from_52w_high': round(distance_from_high, 2),
                '5d_change': round(change_5d, 2),
                'analyst_target': info.get('targetMeanPrice', None),
                'recommendation': info.get('recommendationKey', 'none'),
            }
        except Exception as e:
            print(f"Error getting fundamentals for {symbol}: {e}")
            return None

    def identify_opportunities(self, symbols: List[str], min_drop: float = 5.0) -> List[Dict]:
        """
        Scan symbols for buying opportunities

        Args:
            symbols: List of symbols to scan
            min_drop: Minimum 5-day drop percentage to consider

        Returns:
            List of opportunities with news, fundamentals, and scores
        """
        opportunities = []

        for symbol in symbols:
            print(f"🔍 Scanning {symbol}...")

            # Get fundamentals first
            fundamentals = self.get_stock_fundamentals(symbol)
            if not fundamentals:
                continue

            # Check if there's a significant drop
            if fundamentals['5d_change'] >= -min_drop:
                continue  # Not enough of a dip

            # Fetch news
            articles = self.fetch_news(symbol)

            # Analyze news sentiment
            opportunity_articles = []
            if articles:
                for article in articles:
                    sentiment = self.analyze_sentiment(article)
                    if sentiment['is_opportunity'] or not articles:
                        article['sentiment'] = sentiment
                        opportunity_articles.append(article)

            # If no opportunity articles but still a dip, add generic news flag
            if not opportunity_articles and articles:
                # Take first article as context
                articles[0]['sentiment'] = self.analyze_sentiment(articles[0])
                opportunity_articles = [articles[0]]
            elif not opportunity_articles:
                # No news at all but there's a dip
                opportunity_articles = [{
                    'title': 'Recent price decline without major news',
                    'sentiment': {'is_opportunity': True, 'has_red_flag': False, 'drop_percentage': None, 'sentiment_score': -20}
                }]

            # Calculate opportunity score
            score = self._calculate_opportunity_score(fundamentals, opportunity_articles)

            if score >= 50:  # Only flag if score is decent
                opportunities.append({
                    'symbol': symbol,
                    'fundamentals': fundamentals,
                    'news': opportunity_articles[:3],  # Top 3 articles
                    'opportunity_score': score,
                    'recommendation': self._get_recommendation(score, fundamentals)
                })

        # Sort by opportunity score (best first)
        opportunities.sort(key=lambda x: x['opportunity_score'], reverse=True)
        return opportunities

    def _calculate_opportunity_score(self, fundamentals: Dict, news: List[Dict]) -> int:
        """
        Calculate opportunity score (0-100)
        Higher = better buying opportunity
        """
        score = 50  # Start neutral

        # Price drop is good (5-15% ideal)
        drop = abs(fundamentals['5d_change'])
        if 5 <= drop <= 15:
            score += 20
        elif 15 < drop <= 25:
            score += 10  # Might be risky
        elif drop > 25:
            score -= 10  # Catching a falling knife?

        # Distance from 52-week high
        distance = fundamentals['distance_from_52w_high']
        if 10 <= distance <= 30:
            score += 15  # Good entry point
        elif distance > 40:
            score += 5  # Deep value or troubled?

        # Valuation metrics
        pe = fundamentals.get('pe_ratio')
        if pe and 10 <= pe <= 25:
            score += 10  # Reasonable valuation
        elif pe and pe < 10:
            score += 5  # Deep value

        # Growth metrics
        revenue_growth = fundamentals.get('revenue_growth')
        if revenue_growth and revenue_growth > 0.1:  # 10%+ growth
            score += 10

        # Profitability
        profit_margins = fundamentals.get('profit_margins')
        if profit_margins and profit_margins > 0.15:  # 15%+ margins
            score += 10

        # Analyst recommendation
        rec = fundamentals.get('recommendation', 'none')
        if rec in ['strong_buy', 'buy']:
            score += 10
        elif rec in ['hold']:
            score += 0
        else:
            score -= 5

        # News sentiment (negative sentiment can be good for buying dips)
        if news:
            has_red_flags = any(a.get('sentiment', {}).get('has_red_flag', False) for a in news)
            if has_red_flags:
                score -= 30  # Major red flag
            else:
                avg_sentiment = sum(a.get('sentiment', {}).get('sentiment_score', 0) for a in news) / len(news)
                # Negative sentiment can be good for buying dips (counterintuitive)
                if -50 <= avg_sentiment <= -20:
                    score += 10  # Fearful market = opportunity

        return max(0, min(100, score))

    def _get_recommendation(self, score: int, fundamentals: Dict) -> str:
        """Generate action recommendation"""
        if score >= 80:
            return "🟢 STRONG BUY - Excellent opportunity"
        elif score >= 65:
            return "🟢 BUY - Good entry point"
        elif score >= 50:
            return "🟡 WATCH - Monitor for better entry"
        else:
            return "🔴 AVOID - Risk too high"


def main():
    """Demo: Scan symbols for opportunities"""
    import yaml
    import os

    monitor = NewsMonitor()

    # Load symbols from config
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    config_path = os.path.join(project_root, "config", "symbols.yaml")

    symbols = []
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            symbols = list(config.get('symbols', {}).keys())
    else:
        symbols = ['AAPL', 'TQQQ', 'UBER']  # Fallback

    print(f"📰 Scanning {len(symbols)} symbols from config for opportunities...")
    opportunities = monitor.identify_opportunities(symbols, min_drop=3.0)

    print(f"\n✅ Found {len(opportunities)} opportunities\n")

    for opp in opportunities:
        fund = opp['fundamentals']
        print(f"{'='*60}")
        print(f"🎯 {opp['symbol']} - {fund['company_name']}")
        print(f"Score: {opp['opportunity_score']}/100")
        print(f"{opp['recommendation']}")
        print(f"\n📊 Metrics:")
        print(f"  • Current Price: ${fund['current_price']}")
        print(f"  • 5-Day Change: {fund['5d_change']:.2f}%")
        print(f"  • From 52W High: {fund['distance_from_52w_high']:.2f}%")
        if fund.get('pe_ratio'):
            print(f"  • P/E Ratio: {fund['pe_ratio']:.2f}")
        print(f"  • Analyst Rec: {fund['recommendation']}")

        if opp['news'] and opp['news'][0].get('title'):
            print(f"\n📰 Recent News:")
            for article in opp['news'][:2]:
                if article.get('title'):
                    print(f"  • {article['title'][:70]}")
        print()


if __name__ == '__main__':
    main()
