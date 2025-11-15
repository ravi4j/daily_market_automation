#!/usr/bin/env python3
"""
Send news-based buying opportunities to Telegram
Uses symbols from config/symbols.yaml
"""

import os
import sys
import json
import requests
import yaml
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from src.news_monitor import NewsMonitor


def load_symbols_config():
    """Load symbols from config/symbols.yaml"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    config_path = os.path.join(project_root, "config", "symbols.yaml")
    
    # Fallback to hardcoded symbols if config file doesn't exist
    default_symbols = ['TQQQ', 'AAPL', 'UBER', 'SP500']
    
    if not os.path.exists(config_path):
        print(f"⚠️  Config file not found at {config_path}, using defaults")
        return default_symbols
    
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            symbols = list(config.get('symbols', {}).keys())
            print(f"✅ Loaded {len(symbols)} symbols from config")
            return symbols
    except Exception as e:
        print(f"⚠️  Error loading config: {e}, using defaults")
        return default_symbols


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


def format_opportunity_message(opportunities: list, symbols_scanned: int) -> str:
    """Format opportunities as Telegram message"""
    message = f"📰 *Daily News Scan Report*\n"
    message += f"_{datetime.now().strftime('%Y-%m-%d %H:%M')}_\n\n"
    message += f"Scanned: *{symbols_scanned}* symbols\n"
    
    if not opportunities:
        message += "\n✅ No significant buying opportunities found.\n"
        message += "All tracked symbols are stable or rising.\n"
        return message
    
    message += f"Found: *{len(opportunities)}* opportunities\n\n"
    message += "━━━━━━━━━━━━━━━━━━━━\n\n"
    
    for i, opp in enumerate(opportunities[:5], 1):  # Top 5
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
        message += f"_{fund['company_name'][:40]}_\n"
        
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
        
        if fund.get('recommendation') and fund['recommendation'] != 'none':
            message += f"• Analyst: {fund['recommendation'].replace('_', ' ').title()}\n"
        
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
            if len(title) > 60:
                title = title[:60] + "..."
            message += f"\n📰 _{title}_\n"
        
        message += "\n"
    
    if len(opportunities) > 5:
        message += f"_...and {len(opportunities) - 5} more opportunities_\n\n"
    
    message += "━━━━━━━━━━━━━━━━━━━━\n\n"
    message += "💡 *Next Steps:*\n"
    message += "• Review fundamentals\n"
    message += "• Run on-demand analysis\n"
    message += "• Set price alerts\n"
    message += "• Consider position sizing\n\n"
    message += "⚠️ _Not financial advice. DYOR._"
    
    return message


def main():
    # Get credentials
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    if not bot_token or not chat_id:
        print("⚠️  Telegram credentials not configured")
        print("Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID environment variables")
        print("Continuing without Telegram notifications...")
    
    # Initialize monitor
    monitor = NewsMonitor()
    
    # Initialize insider tracker (optional)
    insider_tracker = None
    try:
        from src.insider_tracker import InsiderTracker
        insider_tracker = InsiderTracker()
        print("✅ Insider tracking enabled")
    except ImportError:
        print("⚠️  finnhub-python not installed, skipping insider tracking")
    except ValueError as e:
        print(f"⚠️  Insider tracking disabled: {e}")
    except Exception as e:
        print(f"⚠️  Insider tracking failed: {e}")
    
    # Load symbols from config
    symbols_to_scan = load_symbols_config()
    
    print(f"📰 Scanning {len(symbols_to_scan)} symbols for opportunities...")
    print(f"Symbols: {', '.join(symbols_to_scan)}")
    
    # Scan for opportunities (using lower threshold to catch more)
    opportunities = monitor.identify_opportunities(symbols_to_scan, min_drop=3.0)
    
    # Add insider tracking to opportunities
    if insider_tracker and opportunities:
        print("\n💼 Fetching insider data...")
        for opp in opportunities:
            symbol = opp['symbol']
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
            except Exception:
                pass  # Skip if insider data fails
    
    # Re-sort opportunities by adjusted score
    if opportunities:
        opportunities.sort(key=lambda x: x['opportunity_score'], reverse=True)
    
    # Save to file
    output_file = 'signals/news_opportunities.json'
    os.makedirs('signals', exist_ok=True)
    
    output_data = {
        'scan_date': datetime.now().isoformat(),
        'symbols_scanned': len(symbols_to_scan),
        'scanned_symbols': symbols_to_scan,
        'opportunities_found': len(opportunities),
        'opportunities': opportunities
    }
    
    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2, default=str)
    
    print(f"✅ Found {len(opportunities)} opportunities")
    print(f"💾 Saved to {output_file}")
    
    # Print summary
    if opportunities:
        print("\n📊 Top Opportunities:")
        for i, opp in enumerate(opportunities[:5], 1):
            fund = opp['fundamentals']
            insider_boost = opp.get('insider_boost', 0)
            boost_str = f" (+{insider_boost} insider)" if insider_boost > 0 else (f" ({insider_boost} insider)" if insider_boost < 0 else "")
            print(f"  {i}. {opp['symbol']} - Score: {opp['opportunity_score']}/100{boost_str} ({fund['5d_change']:+.2f}%)")
    else:
        print("\n✅ No significant dips found in tracked symbols")
    
    # Send to Telegram if configured
    if bot_token and chat_id:
        message = format_opportunity_message(opportunities, len(symbols_to_scan))
        if send_telegram_message(message, bot_token, chat_id):
            print("📤 Sent to Telegram")
        else:
            print("❌ Failed to send to Telegram")
    else:
        print("⏭️  Skipped Telegram notification (not configured)")


if __name__ == '__main__':
    main()

