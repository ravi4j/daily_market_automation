"""
Daily ETF Trade Selector
Scans ONLY ETFs (no individual stocks) for best daily opportunities
"""

import os
import sys
import pandas as pd
import yaml
from pathlib import Path
from typing import Dict, List

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.daily_sector_trades import (
    calculate_composite_score,
    format_telegram_message,
    save_results
)
from src.news_monitor import NewsMonitor
from src.insider_tracker import InsiderTracker


def load_etf_universe() -> Dict[str, List[str]]:
    """Load ETF universe from config"""
    config_file = PROJECT_ROOT / 'config' / 'etf_universe.yaml'
    
    if not config_file.exists():
        print("⚠️  ETF universe config not found, using defaults...")
        return {
            'Recommended Daily Trading': [
                'SPY', 'QQQ', 'XLK', 'XLF', 'XLE', 'IWM', 'TQQQ', 'SQQQ'
            ]
        }
    
    with open(config_file) as f:
        config = yaml.safe_load(f)
    
    return config


def get_etf_list(category: str = 'recommended_daily_trading') -> List[str]:
    """Get list of ETFs from a specific category"""
    universe = load_etf_universe()
    
    if category in universe:
        etfs = universe[category]
        if isinstance(etfs, list):
            return etfs
        elif isinstance(etfs, dict):
            # Flatten dict values
            all_etfs = []
            for etf_list in etfs.values():
                if isinstance(etf_list, list):
                    all_etfs.extend(etf_list)
            return all_etfs
    
    return []


def get_all_etfs() -> List[str]:
    """Get all ETFs from universe (deduplicated)"""
    universe = load_etf_universe()
    all_etfs = set()
    
    def extract_etfs(data):
        if isinstance(data, list):
            for item in data:
                if isinstance(item, str):
                    all_etfs.add(item)
        elif isinstance(data, dict):
            for value in data.values():
                extract_etfs(value)
    
    extract_etfs(universe)
    return sorted(list(all_etfs))


def categorize_etf(symbol: str) -> str:
    """Determine ETF category/type"""
    universe = load_etf_universe()
    
    # Check each category
    if 'sector_etfs' in universe:
        for sector, etfs in universe['sector_etfs'].items():
            if symbol in etfs:
                return sector.replace('_', ' ').title()
    
    if 'index_etfs' in universe:
        for index_type, etfs in universe['index_etfs'].items():
            if isinstance(etfs, list) and symbol in etfs:
                return f"{index_type.upper()} Index"
    
    if 'leveraged_long' in universe:
        for market, etfs in universe['leveraged_long'].items():
            if symbol in etfs:
                return f"3x Long {market.title()}"
    
    if 'leveraged_short' in universe:
        for market, etfs in universe['leveraged_short'].items():
            if symbol in etfs:
                return f"3x Short {market.title()}"
    
    return "Other ETF"


def scan_etfs_for_trades(etf_list: List[str], max_per_category: int = 2) -> Dict[str, List]:
    """
    Scan ETFs and group by category
    
    Args:
        etf_list: List of ETF symbols to scan
        max_per_category: Max trades per category
    
    Returns:
        Dict with category -> list of trades
    """
    print(f"\n📊 Scanning {len(etf_list)} ETFs for best daily trades...")
    print("="*80)
    
    news_monitor = NewsMonitor()
    insider_tracker = InsiderTracker()
    
    # Scan all ETFs
    all_trades = []
    
    for symbol in etf_list:
        category = categorize_etf(symbol)
        print(f"\n🔍 Analyzing {symbol} ({category})...")
        
        trade = calculate_composite_score(
            symbol, 
            category,  # Use ETF category as "sector"
            news_monitor,
            insider_tracker
        )
        
        if trade and trade['total_score'] >= 40:  # Minimum threshold
            all_trades.append(trade)
    
    # Group by category
    results_by_category = {}
    
    for trade in all_trades:
        category = trade['sector']  # Actually the ETF category
        
        if category not in results_by_category:
            results_by_category[category] = []
        
        results_by_category[category].append(trade)
    
    # Sort each category by score and limit
    for category in results_by_category:
        results_by_category[category].sort(key=lambda x: x['total_score'], reverse=True)
        results_by_category[category] = results_by_category[category][:max_per_category]
    
    # Print summary
    print("\n" + "="*80)
    print("SCAN COMPLETE")
    print("="*80)
    
    total_trades = sum(len(trades) for trades in results_by_category.values())
    print(f"\n✅ Found {total_trades} qualified ETF trades across {len(results_by_category)} categories")
    
    for category, trades in sorted(results_by_category.items()):
        print(f"\n📊 {category} ({len(trades)} trade(s)):")
        for trade in trades:
            print(f"   • {trade['symbol']}: {trade['total_score']:.0f}/100 - {trade['recommendation']}")
    
    return results_by_category


def format_etf_telegram_message(results: Dict[str, List]) -> str:
    """Format ETF results as Telegram message"""
    from datetime import datetime
    
    if not results:
        return "ℹ️ No qualified ETF trades found today"
    
    message = "<b>📊 DAILY ETF TRADES</b>\n"
    message += "<i>ETFs Only - No Individual Stocks</i>\n"
    message += f"<i>{datetime.now().strftime('%B %d, %Y')}</i>\n\n"
    
    total_trades = sum(len(trades) for trades in results.values())
    message += f"<b>{total_trades} ETF trades across {len(results)} categories</b>\n"
    message += "━━━━━━━━━━━━━━━━━━━━\n\n"
    
    for category, trades in sorted(results.items()):
        message += f"<b>📊 {category}</b>\n\n"
        
        for i, trade in enumerate(trades, 1):
            # Emoji based on confidence
            if trade['confidence'] == 'HIGH':
                emoji = "⭐⭐⭐"
            elif trade['confidence'] == 'MEDIUM':
                emoji = "⭐⭐"
            else:
                emoji = "⭐"
            
            message += f"{i}. <b>{trade['symbol']}</b> {emoji}\n"
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
    
    message += "<b>💡 ETF Trading Strategy:</b>\n"
    message += "• Focus on HIGH confidence (⭐⭐⭐)\n"
    message += "• Diversify across categories\n"
    message += "• Lower risk than individual stocks\n"
    message += "• Set stop losses immediately\n"
    message += "• Leveraged ETFs (3x) = SHORT-TERM only!\n"
    
    return message


def save_etf_results(results: Dict[str, List]):
    """Save ETF results to JSON"""
    import json
    from datetime import datetime
    
    output_file = PROJECT_ROOT / 'signals' / 'daily_etf_trades.json'
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Flatten for JSON
    flat_results = []
    for category, trades in results.items():
        flat_results.extend(trades)
    
    output = {
        'date': datetime.now().strftime('%Y-%m-%d'),
        'timestamp': datetime.now().isoformat(),
        'total_trades': len(flat_results),
        'categories_covered': len(results),
        'trades': flat_results
    }
    
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\n✅ Saved results to: {output_file}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Daily ETF trade selector')
    parser.add_argument('--category', 
                       default='recommended_daily_trading',
                       help='ETF category to scan (default: recommended_daily_trading)')
    parser.add_argument('--all', action='store_true',
                       help='Scan ALL ETFs from universe')
    parser.add_argument('--etfs', nargs='+',
                       help='Specific ETFs to scan')
    parser.add_argument('--max-per-category', type=int, default=2,
                       help='Max trades per category (default: 2)')
    parser.add_argument('--min-score', type=int, default=60,
                       help='Minimum composite score (default: 60)')
    
    args = parser.parse_args()
    
    print("="*80)
    print("DAILY ETF TRADE SELECTOR")
    print("="*80)
    print("🎯 ETFs Only - No Individual Stocks")
    from datetime import datetime
    print(f"Date: {datetime.now().strftime('%B %d, %Y')}\n")
    
    # Determine which ETFs to scan
    if args.etfs:
        etf_list = args.etfs
        print(f"📊 Scanning {len(etf_list)} specified ETFs: {', '.join(etf_list)}")
    elif args.all:
        etf_list = get_all_etfs()
        print(f"📊 Scanning ALL {len(etf_list)} ETFs from universe")
    else:
        etf_list = get_etf_list(args.category)
        print(f"📊 Scanning '{args.category}' category: {len(etf_list)} ETFs")
        if not etf_list:
            print(f"⚠️  Category '{args.category}' not found or empty")
            print("\nAvailable categories:")
            print("  - recommended_daily_trading")
            print("  - recommended_sector_rotation")
            print("  - sector_etfs")
            print("  - index_etfs")
            print("  - leveraged_long")
            print("  - leveraged_short")
            print("  - conservative")
            print("  - aggressive")
            return
    
    if not etf_list:
        print("❌ No ETFs to scan")
        return
    
    # Scan for trades
    results = scan_etfs_for_trades(etf_list, args.max_per_category)
    
    # Save results
    if results:
        save_etf_results(results)
    
    # Format for Telegram
    message = format_etf_telegram_message(results)
    
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
    
    print("\n✅ ETF TRADE SELECTION COMPLETE!")
    print("\n💡 Tip: ETFs are lower risk than individual stocks!")
    print("💡 Tip: Leveraged ETFs (3x) are for SHORT-TERM trading only!")


if __name__ == '__main__':
    main()

