"""
Scan for opportunities by sector (1-2 per sector for diversification)
"""

import os
import sys
import pandas as pd
from pathlib import Path
from typing import Dict, List

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.news_monitor import NewsMonitor

METADATA_FILE = PROJECT_ROOT / 'data' / 'metadata' / 'symbol_metadata.csv'


def load_metadata() -> pd.DataFrame:
    """Load symbol metadata"""
    if not METADATA_FILE.exists():
        print(f"❌ Metadata file not found: {METADATA_FILE}")
        print("   Run first: python scripts/fetch_symbol_metadata.py")
        sys.exit(1)
    
    return pd.read_csv(METADATA_FILE)


def scan_sector(sector: str, symbols: List[str], max_per_sector: int = 2) -> List[Dict]:
    """
    Scan a sector for opportunities
    
    Args:
        sector: Sector name
        symbols: List of symbols in this sector
        max_per_sector: Maximum opportunities to return per sector
    
    Returns:
        List of opportunities (max max_per_sector)
    """
    print(f"\n🔍 Scanning {sector} ({len(symbols)} symbols)...")
    
    monitor = NewsMonitor()
    opportunities = monitor.identify_opportunities(symbols, min_drop=3.0)
    
    if not opportunities:
        print(f"   ℹ️  No opportunities found in {sector}")
        return []
    
    # Sort by score
    opportunities.sort(key=lambda x: x.get('score', 0), reverse=True)
    
    # Take top N per sector
    top_opportunities = opportunities[:max_per_sector]
    
    for opp in top_opportunities:
        opp['sector'] = sector
    
    print(f"   ✅ Found {len(top_opportunities)} opportunity(ies)")
    for opp in top_opportunities:
        print(f"      • {opp['symbol']}: Score {opp['score']}/100")
    
    return top_opportunities


def scan_all_sectors(metadata_df: pd.DataFrame, max_per_sector: int = 2) -> Dict[str, List]:
    """
    Scan all sectors for opportunities
    
    Returns:
        Dict with sector -> list of opportunities
    """
    sectors = metadata_df['sector'].unique()
    sectors = [s for s in sectors if s != 'Unknown']
    
    print(f"\n📊 Scanning {len(sectors)} sectors...")
    print("="*80)
    
    results = {}
    
    for sector in sorted(sectors):
        symbols = metadata_df[metadata_df['sector'] == sector]['symbol'].tolist()
        opportunities = scan_sector(sector, symbols, max_per_sector)
        
        if opportunities:
            results[sector] = opportunities
    
    return results


def format_telegram_message(results: Dict[str, List]) -> str:
    """Format results as Telegram message"""
    
    if not results:
        return "ℹ️ No opportunities found across all sectors"
    
    message = "<b>🎯 SECTOR OPPORTUNITIES</b>\n"
    message += f"<i>Diversified across {len(results)} sectors</i>\n\n"
    
    total_opportunities = sum(len(opps) for opps in results.values())
    message += f"<b>Total: {total_opportunities} opportunities</b>\n"
    message += "━━━━━━━━━━━━━━━━━━━━\n\n"
    
    for sector, opportunities in sorted(results.items()):
        message += f"<b>🏢 {sector}</b>\n\n"
        
        for i, opp in enumerate(opportunities, 1):
            message += f"{i}. <b>{opp['symbol']}</b> - {opp['company_name']}\n"
            message += f"   Score: <b>{opp['score']}/100</b>\n"
            message += f"   Price: ${opp['current_price']:.2f}\n"
            message += f"   Drop: <b>{opp['price_change_5d']:.2f}%</b>\n"
            message += f"   Reason: {opp['news_reason']}\n\n"
        
        message += "━━━━━━━━━━━━━━━━━━━━\n\n"
    
    message += "<b>💡 Diversification Strategy:</b>\n"
    message += "• Pick 1-2 from each sector\n"
    message += "• Spread risk across industries\n"
    message += "• Monitor daily for changes\n"
    
    return message


def save_results(results: Dict[str, List]):
    """Save results to JSON"""
    import json
    
    output_file = PROJECT_ROOT / 'signals' / 'sector_opportunities.json'
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Flatten for JSON
    flat_results = []
    for sector, opportunities in results.items():
        flat_results.extend(opportunities)
    
    output = {
        'timestamp': pd.Timestamp.now().isoformat(),
        'total_opportunities': len(flat_results),
        'sectors_covered': len(results),
        'opportunities': flat_results
    }
    
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\n✅ Saved results to: {output_file}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Scan by sector')
    parser.add_argument('--max-per-sector', type=int, default=2, 
                       help='Max opportunities per sector (default: 2)')
    parser.add_argument('--sectors', nargs='+', 
                       help='Specific sectors to scan (default: all)')
    
    args = parser.parse_args()
    
    print("="*80)
    print("SECTOR-BASED OPPORTUNITY SCANNER")
    print("="*80)
    
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
    
    print("\n✅ SCAN COMPLETE!")


if __name__ == '__main__':
    main()

