"""
Daily Sector Trade Selector
Identifies the BEST 1-2 trades per sector using multiple signals
Combines: News sentiment, Technical indicators, Fundamentals, Insider activity
"""

import os
import sys
import pandas as pd
import yfinance as yf
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime, timedelta

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.news_monitor import NewsMonitor
from src.indicators import TechnicalIndicators
from src.insider_tracker import InsiderTracker

METADATA_FILE = PROJECT_ROOT / 'data' / 'metadata' / 'symbol_metadata.csv'


def load_metadata() -> pd.DataFrame:
    """Load symbol metadata"""
    if not METADATA_FILE.exists():
        print(f"❌ Metadata file not found: {METADATA_FILE}")
        print("   Run first: python scripts/fetch_symbol_metadata.py")
        sys.exit(1)

    return pd.read_csv(METADATA_FILE)


def load_price_data(symbol: str) -> Optional[pd.DataFrame]:
    """Load historical price data for a symbol"""
    csv_file = PROJECT_ROOT / 'data' / 'market_data' / f'{symbol}.csv'

    if not csv_file.exists():
        return None

    try:
        df = pd.read_csv(csv_file, index_col=0, parse_dates=True)
        df = df.sort_index()
        return df
    except Exception as e:
        print(f"   ⚠️  Error loading {symbol}: {e}")
        return None


def calculate_technical_score(df: pd.DataFrame, symbol: str) -> Dict:
    """
    Calculate technical analysis score (0-100)

    Checks:
    - RSI (oversold = good)
    - MACD (bullish crossover = good)
    - Bollinger Bands (near lower band = good)
    - Volume (increasing = good)
    - Trend (uptrend = good)
    """
    if df is None or len(df) < 50:
        return {'score': 0, 'signals': [], 'confidence': 'LOW'}

    try:
        # Add technical indicators
        tech = TechnicalIndicators(df)
        df_tech = tech.add_all_indicators()

        if df_tech.empty or len(df_tech) < 2:
            return {'score': 0, 'signals': [], 'confidence': 'LOW'}

        latest = df_tech.iloc[-1]
        prev = df_tech.iloc[-2]

        score = 0
        signals = []

        # 1. RSI (20 points) - Oversold is good
        rsi = latest.get('RSI_14', 50)
        if rsi < 30:
            score += 20
            signals.append(f"RSI oversold ({rsi:.1f})")
        elif rsi < 40:
            score += 15
            signals.append(f"RSI low ({rsi:.1f})")
        elif rsi < 50:
            score += 10
            signals.append(f"RSI neutral-low ({rsi:.1f})")

        # 2. MACD (20 points) - Bullish crossover
        macd = latest.get('MACD_12_26_9', 0)
        macd_signal = latest.get('MACDs_12_26_9', 0)
        prev_macd = prev.get('MACD_12_26_9', 0)
        prev_signal = prev.get('MACDs_12_26_9', 0)

        if macd > macd_signal and prev_macd <= prev_signal:
            score += 20
            signals.append("MACD bullish crossover")
        elif macd > macd_signal:
            score += 10
            signals.append("MACD bullish")

        # 3. Bollinger Bands (20 points) - Near lower band
        bb_lower = latest.get('BBL_20_2.0', 0)
        bb_upper = latest.get('BBU_20_2.0', 0)
        close = latest.get('Close', 0)

        if bb_lower > 0 and bb_upper > 0:
            bb_position = (close - bb_lower) / (bb_upper - bb_lower)
            if bb_position < 0.2:
                score += 20
                signals.append(f"Near BB lower band ({bb_position*100:.0f}%)")
            elif bb_position < 0.4:
                score += 15
                signals.append(f"Below BB middle ({bb_position*100:.0f}%)")

        # 4. Volume (15 points) - Increasing volume
        volume = latest.get('Volume', 0)
        avg_volume = df_tech['Volume'].tail(20).mean()

        if volume > avg_volume * 1.5:
            score += 15
            signals.append("High volume (1.5x avg)")
        elif volume > avg_volume * 1.2:
            score += 10
            signals.append("Above avg volume")

        # 5. Trend (15 points) - Price above moving averages
        sma_20 = latest.get('SMA_20', 0)
        sma_50 = latest.get('SMA_50', 0)

        if close > sma_20 > sma_50:
            score += 15
            signals.append("Strong uptrend (above SMAs)")
        elif close > sma_20:
            score += 10
            signals.append("Above SMA20")

        # 6. ADX (10 points) - Trend strength
        adx = latest.get('ADX_14', 0)
        if adx > 25:
            score += 10
            signals.append(f"Strong trend (ADX {adx:.0f})")
        elif adx > 20:
            score += 5
            signals.append(f"Moderate trend (ADX {adx:.0f})")

        # Determine confidence
        if score >= 70:
            confidence = 'HIGH'
        elif score >= 50:
            confidence = 'MEDIUM'
        else:
            confidence = 'LOW'

        return {
            'score': min(score, 100),
            'signals': signals,
            'confidence': confidence,
            'rsi': round(float(rsi), 1),
            'macd_bullish': macd > macd_signal,
            'bb_position': round(bb_position * 100, 1) if bb_lower > 0 else None,
            'volume_ratio': round(volume / avg_volume, 2) if avg_volume > 0 else 1.0
        }

    except Exception as e:
        print(f"   ⚠️  Error calculating technical score for {symbol}: {e}")
        return {'score': 0, 'signals': [], 'confidence': 'LOW'}


def calculate_composite_score(symbol: str, sector: str,
                              news_monitor: NewsMonitor,
                              insider_tracker: InsiderTracker) -> Optional[Dict]:
    """
    Calculate composite score from multiple signals

    Components:
    - News sentiment (30%)
    - Technical analysis (40%)
    - Fundamentals (20%)
    - Insider activity (10%)

    Returns:
    {
        'symbol': 'AAPL',
        'sector': 'Technology',
        'total_score': 85,
        'confidence': 'HIGH',
        'news_score': 75,
        'technical_score': 88,
        'fundamental_score': 90,
        'insider_score': 80,
        'signals': [...],
        'recommendation': 'STRONG BUY',
        'entry': 220.00,
        'stop': 215.00,
        'target': 235.00
    }
    """
    print(f"   Analyzing {symbol}...")

    # Load price data
    df = load_price_data(symbol)
    if df is None or len(df) < 50:
        print(f"      ⚠️  Insufficient data")
        return None

    # Get latest price
    latest_price = float(df['Close'].iloc[-1])

    # 1. News Sentiment (30%)
    news_opps = news_monitor.identify_opportunities([symbol], min_drop=1.0)
    news_score = 0
    news_reason = "No recent news"

    if news_opps:
        news_score = news_opps[0].get('score', 0)
        news_reason = news_opps[0].get('news_reason', 'Price drop')
    else:
        # No news, give neutral score based on price change
        price_5d_ago = float(df['Close'].iloc[-6]) if len(df) >= 6 else latest_price
        change_5d = ((latest_price - price_5d_ago) / price_5d_ago) * 100

        if change_5d < -3:
            news_score = 60  # Moderate opportunity (no specific news)
            news_reason = f"5-day drop: {change_5d:.1f}%"
        elif change_5d < 0:
            news_score = 40
            news_reason = f"Minor decline: {change_5d:.1f}%"
        else:
            news_score = 20
            news_reason = f"No decline ({change_5d:.1f}%)"

    # 2. Technical Analysis (40%)
    tech_analysis = calculate_technical_score(df, symbol)
    tech_score = tech_analysis['score']
    tech_signals = tech_analysis['signals']

    # 3. Fundamentals (20%)
    fundamentals = news_monitor.get_stock_fundamentals(symbol)
    fundamental_score = 0
    fundamental_signals = []

    if fundamentals:
        # P/E ratio
        pe = fundamentals.get('pe_ratio')
        if pe and 10 < pe < 30:
            fundamental_score += 5
            fundamental_signals.append(f"Good P/E ({pe:.1f})")

        # Profit margins
        margins = fundamentals.get('profit_margins')
        if margins and margins > 0.15:
            fundamental_score += 5
            fundamental_signals.append(f"Strong margins ({margins*100:.1f}%)")

        # Analyst recommendation
        rec = fundamentals.get('recommendation', 'none')
        if rec in ['strong_buy', 'buy']:
            fundamental_score += 5
            fundamental_signals.append(f"Analysts: {rec.replace('_', ' ')}")

        # Distance from 52W high
        distance = fundamentals.get('distance_from_52w_high', 100)
        if distance > 20:
            fundamental_score += 5
            fundamental_signals.append(f"{distance:.0f}% below 52W high")

    # Normalize to 100
    fundamental_score = min(fundamental_score * 5, 100)

    # 4. Insider Activity (10%)
    insider_data = insider_tracker.get_insider_sentiment(symbol)
    insider_score = 50  # Neutral default
    insider_signal = "No insider data"

    if insider_data:
        sentiment = insider_data.get('sentiment', 'NEUTRAL')
        if sentiment == 'STRONG_BUY':
            insider_score = 100
            insider_signal = "Strong insider buying"
        elif sentiment == 'BUY':
            insider_score = 75
            insider_signal = "Insider buying"
        elif sentiment == 'NEUTRAL':
            insider_score = 50
            insider_signal = "Neutral insider activity"
        elif sentiment == 'SELL':
            insider_score = 25
            insider_signal = "Insider selling"
        elif sentiment == 'STRONG_SELL':
            insider_score = 0
            insider_signal = "Heavy insider selling"

    # Calculate weighted composite score
    composite_score = (
        news_score * 0.30 +
        tech_score * 0.40 +
        fundamental_score * 0.20 +
        insider_score * 0.10
    )

    # Determine overall confidence
    if composite_score >= 75 and tech_analysis['confidence'] == 'HIGH':
        confidence = 'HIGH'
        recommendation = 'STRONG BUY'
    elif composite_score >= 60:
        confidence = 'MEDIUM'
        recommendation = 'BUY'
    elif composite_score >= 40:
        confidence = 'LOW'
        recommendation = 'WATCH'
    else:
        confidence = 'VERY_LOW'
        recommendation = 'SKIP'

    # Calculate entry/stop/target
    atr = df['Close'].tail(14).std()  # Approximate ATR
    entry = latest_price
    stop = entry - (atr * 2)  # 2 ATR stop
    target = entry + (atr * 4)  # 2:1 risk/reward

    # Collect all signals
    all_signals = []
    all_signals.append(f"📰 News: {news_reason}")
    all_signals.extend([f"📊 {s}" for s in tech_signals[:3]])  # Top 3
    all_signals.extend([f"💼 {s}" for s in fundamental_signals[:2]])  # Top 2
    all_signals.append(f"🏢 {insider_signal}")

    return {
        'symbol': symbol,
        'sector': sector,
        'company_name': fundamentals.get('company_name', symbol) if fundamentals else symbol,
        'total_score': round(composite_score, 1),
        'confidence': confidence,
        'recommendation': recommendation,

        # Component scores
        'news_score': round(news_score, 1),
        'technical_score': round(tech_score, 1),
        'fundamental_score': round(fundamental_score, 1),
        'insider_score': round(insider_score, 1),

        # Signals
        'signals': all_signals,
        'top_signal': all_signals[0] if all_signals else 'No signals',

        # Price info
        'current_price': round(latest_price, 2),
        'entry': round(entry, 2),
        'stop': round(stop, 2),
        'target': round(target, 2),
        'risk_reward': round((target - entry) / (entry - stop), 2) if (entry - stop) > 0 else 0,

        # Technical details
        'rsi': tech_analysis.get('rsi'),
        'macd_bullish': tech_analysis.get('macd_bullish'),
        'volume_ratio': tech_analysis.get('volume_ratio'),

        'timestamp': datetime.now().isoformat()
    }


def scan_sector_for_best_trades(sector: str, symbols: List[str],
                                max_trades: int = 2) -> List[Dict]:
    """
    Scan a sector and return the BEST 1-2 trades

    Args:
        sector: Sector name
        symbols: List of symbols in sector
        max_trades: Maximum trades to return (default: 2)

    Returns:
        List of best trades sorted by composite score
    """
    print(f"\n🔍 Scanning {sector} ({len(symbols)} symbols)...")

    news_monitor = NewsMonitor()
    insider_tracker = InsiderTracker()

    trades = []

    for symbol in symbols:
        trade = calculate_composite_score(symbol, sector, news_monitor, insider_tracker)
        if trade and trade['total_score'] >= 40:  # Minimum threshold
            trades.append(trade)

    # Sort by total score (highest first)
    trades.sort(key=lambda x: x['total_score'], reverse=True)

    # Return top N
    best_trades = trades[:max_trades]

    if best_trades:
        print(f"   ✅ Found {len(best_trades)} trade(s):")
        for trade in best_trades:
            print(f"      • {trade['symbol']}: {trade['total_score']:.0f}/100 - {trade['recommendation']}")
    else:
        print(f"   ℹ️  No qualified trades found")

    return best_trades


def scan_all_sectors(metadata_df: pd.DataFrame, max_per_sector: int = 2) -> Dict[str, List]:
    """Scan all sectors for best daily trades"""

    sectors = metadata_df['sector'].unique()
    sectors = [s for s in sectors if s != 'Unknown']

    print(f"\n📊 Scanning {len(sectors)} sectors for best daily trades...")
    print("="*80)

    results = {}

    for sector in sorted(sectors):
        symbols = metadata_df[metadata_df['sector'] == sector]['symbol'].tolist()

        # Skip sectors with too few stocks
        if len(symbols) < 3:
            print(f"\n⏭️  Skipping {sector} (only {len(symbols)} stocks)")
            continue

        best_trades = scan_sector_for_best_trades(sector, symbols, max_per_sector)

        if best_trades:
            results[sector] = best_trades

    return results


def format_telegram_message(results: Dict[str, List]) -> str:
    """Format results as Telegram message"""

    if not results:
        return "ℹ️ No qualified trades found today across all sectors"

    message = "<b>🎯 DAILY SECTOR TRADES</b>\n"
    message += f"<i>{datetime.now().strftime('%B %d, %Y')}</i>\n\n"

    total_trades = sum(len(trades) for trades in results.values())
    message += f"<b>{total_trades} trades across {len(results)} sectors</b>\n"
    message += "━━━━━━━━━━━━━━━━━━━━\n\n"

    for sector, trades in sorted(results.items()):
        message += f"<b>🏢 {sector}</b>\n\n"

        for i, trade in enumerate(trades, 1):
            # Emoji based on confidence
            if trade['confidence'] == 'HIGH':
                emoji = "⭐⭐⭐"
            elif trade['confidence'] == 'MEDIUM':
                emoji = "⭐⭐"
            else:
                emoji = "⭐"

            message += f"{i}. <b>{trade['symbol']}</b> - {trade['company_name']} {emoji}\n"
            message += f"   Score: <b>{trade['total_score']:.0f}/100</b> | {trade['recommendation']}\n"
            message += f"   Price: ${trade['current_price']:.2f}\n\n"

            message += f"   <b>Signals:</b>\n"
            message += f"   {trade['top_signal']}\n"

            # Technical summary
            tech_info = []
            if trade.get('rsi'):
                tech_info.append(f"RSI {trade['rsi']:.0f}")
            if trade.get('macd_bullish'):
                tech_info.append("MACD ✓")
            if trade.get('volume_ratio') and trade['volume_ratio'] > 1.2:
                tech_info.append(f"Vol {trade['volume_ratio']:.1f}x")

            if tech_info:
                message += f"   📊 {' | '.join(tech_info)}\n"

            message += f"\n   <b>Trade Setup:</b>\n"
            message += f"   Entry: ${trade['entry']:.2f}\n"
            message += f"   Stop: ${trade['stop']:.2f}\n"
            message += f"   Target: ${trade['target']:.2f}\n"
            message += f"   R:R = 1:{trade['risk_reward']:.1f}\n\n"

        message += "━━━━━━━━━━━━━━━━━━━━\n\n"

    message += "<b>💡 Daily Trading Strategy:</b>\n"
    message += "• Review top 1-2 from each sector\n"
    message += "• Focus on HIGH confidence (⭐⭐⭐)\n"
    message += "• Diversify across sectors\n"
    message += "• Set stop losses immediately\n"

    return message


def save_results(results: Dict[str, List]):
    """Save results to JSON"""
    import json

    output_file = PROJECT_ROOT / 'signals' / 'daily_sector_trades.json'
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Flatten for JSON
    flat_results = []
    for sector, trades in results.items():
        flat_results.extend(trades)

    output = {
        'date': datetime.now().strftime('%Y-%m-%d'),
        'timestamp': datetime.now().isoformat(),
        'total_trades': len(flat_results),
        'sectors_covered': len(results),
        'trades': flat_results
    }

    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\n✅ Saved results to: {output_file}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Daily sector trade selector')
    parser.add_argument('--max-per-sector', type=int, default=2,
                       help='Max trades per sector (default: 2)')
    parser.add_argument('--min-score', type=int, default=60,
                       help='Minimum composite score (default: 60)')
    parser.add_argument('--sectors', nargs='+',
                       help='Specific sectors to scan (default: all)')

    args = parser.parse_args()

    print("="*80)
    print("DAILY SECTOR TRADE SELECTOR")
    print("="*80)
    print(f"Date: {datetime.now().strftime('%B %d, %Y')}")

    # Load metadata
    print("\n📋 Loading symbol metadata...")
    metadata_df = load_metadata()

    # Filter by sectors if specified
    if args.sectors:
        metadata_df = metadata_df[metadata_df['sector'].isin(args.sectors)]
        print(f"   Filtering to: {', '.join(args.sectors)}")

    # Scan all sectors
    results = scan_all_sectors(metadata_df, args.max_per_sector)

    # Save results
    if results:
        save_results(results)

    # Format for Telegram
    message = format_telegram_message(results)

    # Send to Telegram
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')

    if bot_token and chat_id:
        print("\n📱 Sending to Telegram...")
        import requests
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "HTML"
        }
        response = requests.post(url, json=payload, timeout=10)

        if response.status_code == 200:
            print("✅ Sent to Telegram!")
        else:
            print(f"❌ Telegram error: {response.status_code}")
    else:
        print("\n📱 Message preview:")
        print("="*80)
        console_msg = message.replace('<b>', '').replace('</b>', '')
        console_msg = console_msg.replace('<i>', '').replace('</i>', '')
        print(console_msg)

    print("\n✅ DAILY TRADE SELECTION COMPLETE!")


if __name__ == '__main__':
    main()
