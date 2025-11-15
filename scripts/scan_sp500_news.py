#!/usr/bin/env python3
"""
Scan S&P 500 stocks for news-based buying opportunities
Optimized for speed with batching and caching
"""

import os
import sys
import json
import requests
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from src.news_monitor import NewsMonitor
from scripts.fetch_sp500_list import load_sp500_list


def send_telegram_message(message: str, bot_token: str, chat_id: str):
    """Send message to Telegram"""
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'Markdown',
        'disable_web_page_preview': True
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"Error sending to Telegram: {e}")
        return False


def scan_symbol_batch(monitor, symbols_batch):
    """Scan a batch of symbols and return opportunities"""
    return monitor.identify_opportunities(symbols_batch, min_drop=3.0)


def group_by_sector(opportunities: list) -> dict:
    """Group opportunities by sector"""
    by_sector = {}
    for opp in opportunities:
        sector = opp.get('sector', 'Unknown')
        if sector not in by_sector:
            by_sector[sector] = []
        by_sector[sector].append(opp)
    return by_sector


def format_opportunity_message(opportunities: list, symbols_scanned: int, scan_type: str = "S&P 500") -> str:
    """Format opportunities as Telegram message with sector grouping"""
    message = f"📰 *{scan_type} News Scan*\n"
    message += f"_{datetime.now().strftime('%Y-%m-%d %H:%M')}_\n\n"
    message += f"Scanned: *{symbols_scanned}* stocks\n"

    if not opportunities:
        message += "\n✅ No significant buying opportunities found.\n"
        message += "Market is generally stable or rising.\n"
        return message

    message += f"Found: *{len(opportunities)}* opportunities\n\n"

    # Group by sector
    by_sector = group_by_sector(opportunities)
    message += "📊 *By Sector:*\n"
    for sector, opps in sorted(by_sector.items(), key=lambda x: len(x[1]), reverse=True):
        message += f"• {sector}: {len(opps)}\n"
    message += "\n━━━━━━━━━━━━━━━━━━━━\n\n"

    # Show top 10 opportunities
    for i, opp in enumerate(opportunities[:10], 1):
        fund = opp['fundamentals']
        score = opp['opportunity_score']

        # Emoji based on score
        if score >= 80:
            emoji = "🟢"
        elif score >= 65:
            emoji = "🟢"
        elif score >= 50:
            emoji = "🟡"
        else:
            emoji = "🔴"

        message += f"*{i}. {opp['symbol']}* {emoji}\n"
        company_name = fund['company_name'][:35]
        message += f"_{company_name}_\n"

        # Score with insider boost indicator
        insider_boost = opp.get('insider_boost', 0)
        if insider_boost != 0:
            message += f"Score: *{score}/100* "
            if insider_boost > 0:
                message += f"(+{insider_boost} insider 🟢)\n"
            else:
                message += f"({insider_boost} insider 🔴)\n"
        else:
            message += f"Score: *{score}/100*\n"

        message += f"• Price: ${fund['current_price']} ({fund['5d_change']:+.2f}%)\n"
        message += f"• From 52W High: {fund['distance_from_52w_high']:.1f}%\n"

        if fund.get('pe_ratio'):
            message += f"• P/E: {fund['pe_ratio']:.1f}\n"

        # Insider activity summary (if present)
        if 'insider_activity' in opp:
            insider = opp['insider_activity']
            sentiment_emoji = {'STRONG_BUY': '🟢🟢', 'BUY': '🟢', 'NEUTRAL': '⚪', 'SELL': '🔴', 'STRONG_SELL': '🔴🔴'}
            insider_emoji = sentiment_emoji.get(insider['sentiment'], '⚪')
            message += f"• Insider: {insider_emoji} {insider['sentiment']} "
            message += f"({insider['num_buys']}B/{insider['num_sells']}S)\n"

        # Add news headline if available
        if opp['news'] and opp['news'][0].get('title'):
            title = opp['news'][0]['title']
            if len(title) > 50:
                title = title[:50] + "..."
            message += f"📰 _{title}_\n"

        message += "\n"

    if len(opportunities) > 10:
        message += f"_...and {len(opportunities) - 10} more opportunities_\n\n"

    message += "━━━━━━━━━━━━━━━━━━━━\n\n"
    message += "💡 *Next Steps:*\n"
    message += "• Review top picks\n"
    message += "• Run technical analysis\n"
    message += "• Check charts & support levels\n\n"
    message += "⚠️ _Not financial advice. DYOR._"

    return message


def pre_filter_by_drop(symbols: list, min_drop: float = 5.0, period_days: int = 5) -> list:
    """
    Pre-filter symbols to only those with significant price drops
    This speeds up scanning by reducing unnecessary API calls

    Args:
        symbols: List of symbols to check
        min_drop: Minimum drop percentage (default 5.0%)
        period_days: Lookback period (default 5 days)

    Returns:
        List of symbols that dropped by min_drop% or more
    """
    import yfinance as yf

    dropped_symbols = []

    for symbol in tqdm(symbols, desc="Pre-filtering", unit="stock"):
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=f'{period_days}d')

            if len(hist) >= 2:
                first_close = hist['Close'].iloc[0]
                last_close = hist['Close'].iloc[-1]
                change_pct = ((last_close - first_close) / first_close) * 100

                if change_pct <= -min_drop:
                    dropped_symbols.append(symbol)
        except Exception:
            # Skip symbols that fail
            continue

    return dropped_symbols


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Scan S&P 500 for news opportunities with insider tracking')
    parser.add_argument('--sector', type=str, help='Filter by sector (e.g., "Information Technology")')
    parser.add_argument('--top', type=int, default=None, help='Scan only top N symbols alphabetically (for testing)')
    parser.add_argument('--batch-size', type=int, default=50, help='Batch size for parallel processing')
    parser.add_argument('--no-telegram', action='store_true', help='Skip Telegram notifications')
    parser.add_argument('--full-scan', action='store_true', help='Scan all stocks (skip pre-filtering by price drop)')
    parser.add_argument('--min-drop', type=float, default=5.0, help='Minimum price drop %% for pre-filter (default: 5.0)')
    parser.add_argument('--no-insider', action='store_true', help='Skip insider tracking (faster but less comprehensive)')

    args = parser.parse_args()

    # Get credentials
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')

    if not bot_token or not chat_id:
        print("⚠️  Telegram credentials not configured")
        args.no_telegram = True

    # Load S&P 500 symbols with sector info
    print("📊 Loading S&P 500 constituent list...")
    import json
    json_file = 'data/sp500_symbols.json'
    if not os.path.exists(json_file):
        print("❌ S&P 500 list not found!")
        print("   Run: python scripts/fetch_sp500_list.py")
        sys.exit(1)

    with open(json_file, 'r') as f:
        data = json.load(f)
        symbol_data = {item['symbol']: item for item in data['symbols']}

    symbols = list(symbol_data.keys())

    # Filter by sector if specified
    if args.sector:
        symbols = [s for s, info in symbol_data.items() if info['sector'] == args.sector]
        scan_type = f"{args.sector} Sector"
        print(f"🔍 Filtering by sector: {args.sector}")
    else:
        scan_type = "S&P 500"

    # Limit for testing
    if args.top:
        symbols = symbols[:args.top]
        print(f"🧪 Testing mode: scanning top {args.top} symbols")

    # Pre-filter by price drops (unless --full-scan specified)
    original_count = len(symbols)
    if not args.full_scan:
        print(f"\n🔍 Pre-filtering for stocks with {args.min_drop}%+ drops...")
        print(f"   (Use --full-scan to skip this step)")
        symbols = pre_filter_by_drop(symbols, min_drop=args.min_drop, period_days=5)
        print(f"✅ Found {len(symbols)} stocks with {args.min_drop}%+ drops (from {original_count} total)")

        if len(symbols) == 0:
            print("\n✅ No significant dips found!")
            print("   Market is generally stable")
            sys.exit(0)
    else:
        print(f"\n⚡ Full scan mode: scanning all {len(symbols)} stocks")

    print(f"\n📰 Scanning {len(symbols)} stocks for opportunities...")
    print(f"⏱️  This will take approximately {len(symbols) * 0.5 / 60:.1f} minutes")
    print()

    # Initialize monitor
    monitor = NewsMonitor()

    # Initialize insider tracker (optional)
    insider_tracker = None
    if not args.no_insider:
        try:
            from src.insider_tracker import InsiderTracker
            insider_tracker = InsiderTracker()
            print("✅ Insider tracking enabled")
        except ImportError:
            print("⚠️  finnhub-python not installed, skipping insider tracking")
            print("   Install: pip install finnhub-python")
        except ValueError as e:
            print(f"⚠️  Insider tracking disabled: {e}")
            print("   Set FINNHUB_API_KEY to enable")
        except Exception as e:
            print(f"⚠️  Insider tracking failed to initialize: {e}")
    else:
        print("⏭️  Insider tracking skipped (--no-insider)")

    print()

    # Scan all symbols with progress bar
    print("🔍 Scanning symbols...")
    all_opportunities = []

    # Use a simple sequential scan with progress bar
    # (Parallel might hit rate limits)
    for symbol in tqdm(symbols, desc="Scanning", unit="stock"):
        try:
            opps = monitor.identify_opportunities([symbol], min_drop=3.0)

            # Add sector information to each opportunity
            for opp in opps:
                if symbol in symbol_data:
                    opp['sector'] = symbol_data[symbol]['sector']
                    opp['company_full'] = symbol_data[symbol]['company']

                # Add insider tracking if enabled
                if insider_tracker:
                    try:
                        insider_data = insider_tracker.get_insider_activity(symbol, days=30)
                        if insider_data:
                            opp['insider_activity'] = insider_data

                            # Adjust opportunity score based on insider sentiment
                            adjustment = insider_data['score_adjustment']
                            old_score = opp['opportunity_score']
                            new_score = max(0, min(100, old_score + adjustment))
                            opp['opportunity_score'] = new_score
                            opp['insider_boost'] = adjustment
                    except Exception as e:
                        # Don't fail the whole scan if insider tracking errors
                        pass

            all_opportunities.extend(opps)
        except Exception as e:
            # Skip symbols that fail
            continue

    # Save results
    output_file = 'signals/sp500_opportunities.json'
    os.makedirs('signals', exist_ok=True)

    output_data = {
        'scan_date': datetime.now().isoformat(),
        'scan_type': scan_type,
        'symbols_scanned': len(symbols),
        'opportunities_found': len(all_opportunities),
        'opportunities': all_opportunities
    }

    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2, default=str)

    print()
    print(f"✅ Scan complete! Found {len(all_opportunities)} opportunities")
    print(f"💾 Saved to {output_file}")

    # Print summary
    if all_opportunities:
        print("\n📊 Top 10 Opportunities:")
        for i, opp in enumerate(all_opportunities[:10], 1):
            fund = opp['fundamentals']
            insider_boost = opp.get('insider_boost', 0)
            boost_str = f" (+{insider_boost} insider)" if insider_boost > 0 else (f" ({insider_boost} insider)" if insider_boost < 0 else "")
            print(f"  {i}. {opp['symbol']:6s} - Score: {opp['opportunity_score']:3d}/100{boost_str} ({fund['5d_change']:+.2f}%) - {fund['company_name'][:40]}")
    else:
        print("\n✅ No significant dips found in S&P 500")
        print("   Market is generally stable")

    # Send to Telegram
    if not args.no_telegram and (bot_token and chat_id):
        print("\n📤 Sending to Telegram...")
        message = format_opportunity_message(all_opportunities, len(symbols), scan_type)
        if send_telegram_message(message, bot_token, chat_id):
            print("✅ Sent to Telegram")
        else:
            print("❌ Failed to send to Telegram")
    else:
        print("\n⏭️  Skipped Telegram notification")

    print("\n🎉 S&P 500 scan complete!")


if __name__ == '__main__':
    main()
