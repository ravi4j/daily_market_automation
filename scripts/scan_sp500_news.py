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


def format_opportunity_message(opportunities: list, symbols_scanned: int, scan_type: str = "S&P 500") -> str:
    """Format opportunities as Telegram message"""
    message = f"📰 *{scan_type} News Scan*\n"
    message += f"_{datetime.now().strftime('%Y-%m-%d %H:%M')}_\n\n"
    message += f"Scanned: *{symbols_scanned}* stocks\n"
    
    if not opportunities:
        message += "\n✅ No significant buying opportunities found.\n"
        message += "Market is generally stable or rising.\n"
        return message
    
    message += f"Found: *{len(opportunities)}* opportunities\n\n"
    message += "━━━━━━━━━━━━━━━━━━━━\n\n"
    
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
        message += f"Score: *{score}/100*\n"
        message += f"• Price: ${fund['current_price']} ({fund['5d_change']:+.2f}%)\n"
        message += f"• From 52W High: {fund['distance_from_52w_high']:.1f}%\n"
        
        if fund.get('pe_ratio'):
            message += f"• P/E: {fund['pe_ratio']:.1f}\n"
        
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


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Scan S&P 500 for news opportunities')
    parser.add_argument('--sector', type=str, help='Filter by sector (e.g., "Information Technology")')
    parser.add_argument('--top', type=int, default=None, help='Scan only top N symbols alphabetically (for testing)')
    parser.add_argument('--batch-size', type=int, default=50, help='Batch size for parallel processing')
    parser.add_argument('--no-telegram', action='store_true', help='Skip Telegram notifications')
    
    args = parser.parse_args()
    
    # Get credentials
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    if not bot_token or not chat_id:
        print("⚠️  Telegram credentials not configured")
        args.no_telegram = True
    
    # Load S&P 500 symbols
    print("📊 Loading S&P 500 constituent list...")
    symbols = load_sp500_list()
    
    if not symbols:
        print("❌ S&P 500 list not found!")
        print("   Run: python scripts/fetch_sp500_list.py")
        sys.exit(1)
    
    # Filter by sector if specified
    if args.sector:
        from scripts.fetch_sp500_list import get_symbols_by_sector
        symbols = get_symbols_by_sector(args.sector)
        scan_type = f"{args.sector} Sector"
        print(f"🔍 Filtering by sector: {args.sector}")
    else:
        scan_type = "S&P 500"
    
    # Limit for testing
    if args.top:
        symbols = symbols[:args.top]
        print(f"🧪 Testing mode: scanning top {args.top} symbols")
    
    print(f"📰 Scanning {len(symbols)} stocks for opportunities...")
    print(f"⏱️  This will take approximately {len(symbols) * 0.5 / 60:.1f} minutes")
    print()
    
    # Initialize monitor
    monitor = NewsMonitor()
    
    # Scan all symbols with progress bar
    print("🔍 Scanning symbols...")
    all_opportunities = []
    
    # Use a simple sequential scan with progress bar
    # (Parallel might hit rate limits)
    for symbol in tqdm(symbols, desc="Scanning", unit="stock"):
        try:
            opps = monitor.identify_opportunities([symbol], min_drop=3.0)
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
            print(f"  {i}. {opp['symbol']:6s} - Score: {opp['opportunity_score']:3d}/100 ({fund['5d_change']:+.2f}%) - {fund['company_name'][:40]}")
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

