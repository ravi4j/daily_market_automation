#!/usr/bin/env python3
"""
Historical News Correlation Tracker

Tracks historical news events and their impact on stock prices to predict
which types of news typically lead to rebounds vs further declines.

Features:
- SQLite database for historical tracking
- Pattern analysis (e.g., "Earnings miss → 3-day rebound")
- Success rate calculation
- Correlation scoring for current opportunities
"""

import os
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class NewsEvent:
    """Represents a historical news event"""
    symbol: str
    date: str
    headline: str
    sentiment: str  # negative, neutral, positive
    category: str  # earnings, guidance, lawsuit, scandal, etc.
    drop_pct: float  # Initial price drop percentage


@dataclass
class PriceMovement:
    """Represents price movement after a news event"""
    days_after: int
    price_change_pct: float
    outcome: str  # rebound, decline, neutral


@dataclass
class Correlation:
    """Represents a correlation pattern"""
    category: str
    sentiment: str
    avg_rebound_pct: float
    success_rate: float  # 0-1, percentage of rebounds
    sample_size: int
    confidence: str  # HIGH, MEDIUM, LOW


class NewsCorrelationTracker:
    """Track and analyze historical news correlations"""

    def __init__(self, db_path: str = "data/metadata/news_correlation.db"):
        """Initialize tracker with SQLite database"""
        self.db_path = db_path

        # Ensure directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

        # Initialize database
        self._init_database()

    def _init_database(self):
        """Create database tables if they don't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # News events table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS news_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                date TEXT NOT NULL,
                headline TEXT,
                sentiment TEXT,
                category TEXT,
                drop_pct REAL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Price movements table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS price_movements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                news_event_id INTEGER,
                days_after INTEGER,
                price_change_pct REAL,
                outcome TEXT,
                recorded_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (news_event_id) REFERENCES news_events (id)
            )
        """)

        # Correlations cache table (updated periodically)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS correlations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT,
                sentiment TEXT,
                avg_rebound_pct REAL,
                success_rate REAL,
                sample_size INTEGER,
                confidence TEXT,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create indexes for faster queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_symbol_date
            ON news_events(symbol, date)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_category_sentiment
            ON correlations(category, sentiment)
        """)

        conn.commit()
        conn.close()

    def record_news_event(self, event: NewsEvent) -> int:
        """
        Record a news event in the database

        Returns:
            event_id: ID of the inserted event
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO news_events (symbol, date, headline, sentiment, category, drop_pct)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (event.symbol, event.date, event.headline, event.sentiment,
              event.category, event.drop_pct))

        event_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return event_id

    def record_price_movement(self, event_id: int, movement: PriceMovement):
        """Record price movement after a news event"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO price_movements (news_event_id, days_after, price_change_pct, outcome)
            VALUES (?, ?, ?, ?)
        """, (event_id, movement.days_after, movement.price_change_pct, movement.outcome))

        conn.commit()
        conn.close()

    def track_opportunity(self, symbol: str, headline: str, sentiment: str,
                         category: str, drop_pct: float) -> int:
        """
        Convenience method to track a new opportunity

        Returns:
            event_id for future price tracking
        """
        event = NewsEvent(
            symbol=symbol,
            date=datetime.now().strftime('%Y-%m-%d'),
            headline=headline,
            sentiment=sentiment,
            category=category,
            drop_pct=drop_pct
        )

        return self.record_news_event(event)

    def update_price_movements(self, symbol: str, days_back: int = 30):
        """
        Update price movements for recent news events

        Args:
            symbol: Stock symbol to update
            days_back: How many days back to check for events
        """
        import yfinance as yf

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get recent events without complete price tracking
        cutoff_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')

        cursor.execute("""
            SELECT id, symbol, date, drop_pct
            FROM news_events
            WHERE symbol = ? AND date >= ?
            AND id NOT IN (
                SELECT DISTINCT news_event_id
                FROM price_movements
                WHERE days_after >= 5
            )
        """, (symbol, cutoff_date))

        events = cursor.fetchall()

        if not events:
            return

        # Fetch price data
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period='2mo')

        for event_id, event_symbol, event_date, drop_pct in events:
            event_dt = pd.Timestamp(event_date)

            # Track price movements for 1, 3, 5, and 10 days
            for days in [1, 3, 5, 10]:
                target_date = event_dt + timedelta(days=days)

                if target_date not in hist.index:
                    continue

                # Calculate price change from event date
                if event_dt in hist.index:
                    event_price = hist.loc[event_dt, 'Close']
                    target_price = hist.loc[target_date, 'Close']

                    price_change_pct = ((target_price - event_price) / event_price) * 100

                    # Determine outcome
                    if price_change_pct >= 2:  # 2%+ gain = rebound
                        outcome = 'rebound'
                    elif price_change_pct <= -2:  # 2%+ loss = further decline
                        outcome = 'decline'
                    else:
                        outcome = 'neutral'

                    # Record movement
                    movement = PriceMovement(
                        days_after=days,
                        price_change_pct=price_change_pct,
                        outcome=outcome
                    )

                    self.record_price_movement(event_id, movement)

        conn.close()

    def calculate_correlations(self):
        """Calculate correlation statistics from historical data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Clear old correlations
        cursor.execute("DELETE FROM correlations")

        # Calculate correlations by category and sentiment
        cursor.execute("""
            SELECT
                ne.category,
                ne.sentiment,
                AVG(CASE WHEN pm.outcome = 'rebound' THEN pm.price_change_pct ELSE 0 END) as avg_rebound_pct,
                CAST(SUM(CASE WHEN pm.outcome = 'rebound' THEN 1 ELSE 0 END) AS REAL) /
                    COUNT(*) as success_rate,
                COUNT(*) as sample_size
            FROM news_events ne
            JOIN price_movements pm ON ne.id = pm.news_event_id
            WHERE pm.days_after = 5  -- Focus on 5-day outcomes
            GROUP BY ne.category, ne.sentiment
            HAVING COUNT(*) >= 3  -- Minimum 3 samples
        """)

        results = cursor.fetchall()

        for category, sentiment, avg_rebound, success_rate, sample_size in results:
            # Determine confidence based on sample size
            if sample_size >= 20:
                confidence = 'HIGH'
            elif sample_size >= 10:
                confidence = 'MEDIUM'
            else:
                confidence = 'LOW'

            cursor.execute("""
                INSERT INTO correlations
                (category, sentiment, avg_rebound_pct, success_rate, sample_size, confidence)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (category, sentiment, avg_rebound, success_rate, sample_size, confidence))

        conn.commit()
        conn.close()

    def get_correlation(self, category: str, sentiment: str) -> Optional[Correlation]:
        """Get correlation data for a category/sentiment combination"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT avg_rebound_pct, success_rate, sample_size, confidence
            FROM correlations
            WHERE category = ? AND sentiment = ?
        """, (category, sentiment))

        result = cursor.fetchone()
        conn.close()

        if not result:
            return None

        return Correlation(
            category=category,
            sentiment=sentiment,
            avg_rebound_pct=result[0],
            success_rate=result[1],
            sample_size=result[2],
            confidence=result[3]
        )

    def get_all_correlations(self) -> List[Correlation]:
        """Get all calculated correlations"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT category, sentiment, avg_rebound_pct, success_rate, sample_size, confidence
            FROM correlations
            ORDER BY success_rate DESC, sample_size DESC
        """)

        correlations = []
        for row in cursor.fetchall():
            correlations.append(Correlation(
                category=row[0],
                sentiment=row[1],
                avg_rebound_pct=row[2],
                success_rate=row[3],
                sample_size=row[4],
                confidence=row[5]
            ))

        conn.close()
        return correlations

    def predict_rebound_probability(self, category: str, sentiment: str) -> Dict:
        """
        Predict rebound probability based on historical correlations

        Returns:
            Dict with prediction, confidence, and reasoning
        """
        correlation = self.get_correlation(category, sentiment)

        if not correlation:
            return {
                'prediction': 'UNKNOWN',
                'probability': 0.5,
                'confidence': 'NONE',
                'reason': f'No historical data for {category}/{sentiment}',
                'sample_size': 0
            }

        # Interpret success rate
        if correlation.success_rate >= 0.70:
            prediction = 'HIGH_REBOUND'
        elif correlation.success_rate >= 0.55:
            prediction = 'MODERATE_REBOUND'
        elif correlation.success_rate >= 0.45:
            prediction = 'NEUTRAL'
        elif correlation.success_rate >= 0.30:
            prediction = 'MODERATE_DECLINE'
        else:
            prediction = 'HIGH_DECLINE'

        return {
            'prediction': prediction,
            'probability': correlation.success_rate,
            'confidence': correlation.confidence,
            'reason': f'Based on {correlation.sample_size} historical events: '
                     f'{correlation.success_rate*100:.0f}% rebound rate, '
                     f'avg {correlation.avg_rebound_pct:+.1f}% gain',
            'sample_size': correlation.sample_size,
            'avg_rebound_pct': correlation.avg_rebound_pct
        }

    def get_stats(self) -> Dict:
        """Get database statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM news_events")
        total_events = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM price_movements")
        total_movements = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM correlations")
        total_correlations = cursor.fetchone()[0]

        cursor.execute("""
            SELECT category, COUNT(*) as count
            FROM news_events
            GROUP BY category
            ORDER BY count DESC
            LIMIT 5
        """)
        top_categories = cursor.fetchall()

        conn.close()

        return {
            'total_events': total_events,
            'total_movements': total_movements,
            'total_correlations': total_correlations,
            'top_categories': top_categories
        }


def main():
    """Test the news correlation tracker"""
    tracker = NewsCorrelationTracker()

    print("📊 News Correlation Tracker - Test Mode\n")

    # Show stats
    stats = tracker.get_stats()
    print(f"Database Stats:")
    print(f"  Total Events: {stats['total_events']}")
    print(f"  Total Movements: {stats['total_movements']}")
    print(f"  Total Correlations: {stats['total_correlations']}")

    if stats['top_categories']:
        print(f"\n  Top Categories:")
        for category, count in stats['top_categories']:
            print(f"    - {category}: {count} events")

    # Show correlations
    correlations = tracker.get_all_correlations()

    if correlations:
        print(f"\n📈 Historical Correlations (Top 10):\n")
        for i, corr in enumerate(correlations[:10], 1):
            print(f"{i}. {corr.category} / {corr.sentiment}")
            print(f"   Success Rate: {corr.success_rate*100:.1f}%")
            print(f"   Avg Rebound: {corr.avg_rebound_pct:+.1f}%")
            print(f"   Sample Size: {corr.sample_size} ({corr.confidence} confidence)")
            print()
    else:
        print("\n⚠️  No correlations calculated yet.")
        print("   Run: python scripts/update_news_correlations.py")

    print("\n✅ Test complete!")


if __name__ == '__main__':
    main()
