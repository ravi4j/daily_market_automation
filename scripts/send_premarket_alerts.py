"""
Send Pre-Market Gap Alerts to Telegram
Runs at 7 AM, 8 AM, 9 AM ET to monitor gaps before market open
"""

import os
import sys
import yaml
import json
from pathlib import Path
from datetime import datetime
import pytz

# Add src to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.premarket_monitor import PreMarketMonitor
from src.futures_monitor import FuturesMonitor
from src.premarket_opportunity_scanner import PreMarketOpportunityScanner


def load_config():
    """Load pre-market configuration"""
    config_path = PROJECT_ROOT / 'config' / 'premarket_config.yaml'
    
    if not config_path.exists():
        print("⚠️  premarket_config.yaml not found!")
        print(f"   Expected at: {config_path}")
        print("   Using default config...")
        return {
            'positions': {},
            'telegram': {'send_alerts': True, 'send_if_no_positions': False},
            'alerts': {},
            'features': {}
        }
    
    with open(config_path) as f:
        config = yaml.safe_load(f)
    
    return config


def send_telegram_message(bot_token: str, chat_id: str, message: str) -> bool:
    """Send message to Telegram (copied from existing utils)"""
    try:
        import requests
        
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "HTML",
            "disable_web_page_preview": True
        }
        
        response = requests.post(url, json=payload, timeout=10)
        
        if response.status_code == 200:
            return True
        else:
            print(f"❌ Telegram API error: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    
    except Exception as e:
        print(f"❌ Error sending to Telegram: {e}")
        return False


def format_telegram_message(alerts, market_sentiment, vix_data, opportunities, config):
    """Format comprehensive Telegram alert message with opportunities"""
    
    et_tz = pytz.timezone('America/New_York')
    now_et = datetime.now(et_tz)
    time_str = now_et.strftime('%I:%M %p ET')
    
    # Header
    message = f"🌅 <b>PRE-MARKET ALERT</b>\n"
    message += f"<i>{time_str}</i>\n\n"
    
    # Market Sentiment Section
    if config.get('telegram', {}).get('include_market_sentiment', True) and market_sentiment:
        message += "<b>📊 MARKET FUTURES</b>\n"
        
        # Individual futures
        for name in ['S&P 500', 'Nasdaq', 'Dow Jones']:
            if name in market_sentiment:
                data = market_sentiment[name]
                emoji = "🟢" if data['change_pct'] > 0 else "🔴" if data['change_pct'] < 0 else "🟡"
                message += f"{emoji} {name}: <b>{data['change_pct']:+.2f}%</b>\n"
        
        # Overall sentiment
        message += f"\n{market_sentiment.get('sentiment_emoji', '•')} "
        message += f"<b>{market_sentiment.get('overall_sentiment', 'N/A')}</b> "
        message += f"({market_sentiment.get('avg_change', 0):+.2f}%)\n"
        message += f"<i>{market_sentiment.get('recommendation', 'Monitor normally')}</i>\n"
        
        message += "━━━━━━━━━━━━━━━━━━━━\n\n"
    
    # VIX Section
    if config.get('telegram', {}).get('include_vix', True) and vix_data:
        message += f"{vix_data.get('emoji', '•')} <b>VIX:</b> {vix_data.get('vix', 'N/A')} "
        message += f"({vix_data.get('level', 'N/A')})\n"
        message += f"<i>{vix_data.get('interpretation', '')}</i>\n"
        message += "━━━━━━━━━━━━━━━━━━━━\n\n"
    
    # Position Alerts Section
    if not alerts:
        if config.get('telegram', {}).get('send_if_no_positions', False):
            message += "✅ <b>No positions to monitor</b>\n\n"
            message += "<i>Add positions to config/premarket_config.yaml</i>"
        return message
    
    message += "<b>📈 YOUR POSITIONS</b>\n\n"
    
    # Filter alerts by configured levels
    alert_levels = config.get('telegram', {}).get('alert_levels', ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'])
    filtered_alerts = [a for a in alerts if a['risk_level'] in alert_levels]
    
    # Sort by risk level (CRITICAL first)
    risk_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
    sorted_alerts = sorted(filtered_alerts, key=lambda x: risk_order.get(x['risk_level'], 4))
    
    for alert in sorted_alerts:
        symbol = alert['symbol']
        pos = alert['position']
        
        # Risk emoji
        risk_emoji = {
            'CRITICAL': '🚨',
            'HIGH': '⚠️',
            'MEDIUM': '🟡',
            'LOW': '✅'
        }.get(alert['risk_level'], '•')
        
        message += f"{risk_emoji} <b>{symbol}</b>\n"
        
        # Price info
        change_emoji = "🟢" if alert['change_pct'] > 0 else "🔴"
        message += f"{change_emoji} Pre-Market: <b>${alert['premarket_price']}</b> "
        message += f"(<b>{alert['change_pct']:+.2f}%</b>)\n"
        message += f"Previous Close: ${alert['previous_close']}\n"
        
        # Position info
        message += f"Your Entry: ${pos['avg_entry']}\n"
        message += f"Your Stop: ${pos['stop_loss']}\n"
        
        # Distance from stop
        if alert['distance_from_stop_pct'] is not None:
            if alert['below_stop']:
                message += f"<b>⚠️ BELOW STOP by {abs(alert['distance_from_stop_pct']):.2f}%</b>\n"
            elif alert['near_stop']:
                message += f"<b>⚠️ Near Stop: {alert['distance_from_stop_pct']:.2f}%</b>\n"
            else:
                message += f"Distance: {alert['distance_from_stop_pct']:.2f}% from stop\n"
        
        # Volume (if available and configured)
        if config.get('alerts', {}).get('show_volume', True) and alert.get('volume', 0) > 0:
            vol_k = alert['volume'] // 1000
            message += f"Pre-Market Volume: {vol_k}K shares\n"
        
        # Gap type
        if config.get('features', {}).get('gap_classification', True):
            gap_display = alert['gap_type'].replace('_', ' ').title()
            if alert['gap_category'] != 'none':
                gap_display += f" ({alert['gap_category']})"
            message += f"Gap: {gap_display}\n"
        
        # Recommendation
        if config.get('telegram', {}).get('include_recommendations', True):
            message += f"\n💡 <i>{alert['recommendation']}</i>\n"
        
        message += "━━━━━━━━━━━━━━━━━━━━\n\n"
    
    # Gap Opportunities Section (NEW!)
    if config.get('telegram', {}).get('include_opportunities', True) and opportunities:
        message += "<b>🟢 GAP OPPORTUNITIES</b>\n"
        message += "<i>New buying opportunities detected</i>\n\n"
        
        for i, opp in enumerate(opportunities[:5], 1):  # Top 5
            # Emoji based on opportunity type
            if opp['opportunity_type'] == 'GAP_DOWN_OVERSOLD':
                type_emoji = "📉"
                type_name = "Gap Down (Oversold)"
            else:
                type_emoji = "📈"
                type_name = "Gap Up (Breakout)"
            
            # Confidence emoji
            conf_emoji = "⭐⭐⭐" if opp['confidence'] == 'HIGH' else "⭐⭐" if opp['confidence'] == 'MEDIUM' else "⭐"
            
            message += f"{type_emoji} <b>{i}. {opp['symbol']}</b> {conf_emoji}\n"
            message += f"{type_name}\n"
            message += f"Gap: <b>{opp['gap_pct']:+.2f}%</b> "
            message += f"(${opp['previous_close']:.2f} → ${opp['current_price']:.2f})\n"
            message += f"Score: <b>{opp['score']}/100</b>\n\n"
            
            message += f"<b>Trade Setup:</b>\n"
            message += f"• Entry: ${opp['entry']:.2f}\n"
            message += f"• Stop: ${opp['stop']:.2f}\n"
            message += f"• Target: ${opp['target']:.2f}\n"
            message += f"• Risk/Reward: 1:{opp['risk_reward']:.1f}\n\n"
            
            if opp.get('reasons'):
                message += f"<b>Why:</b>\n"
                for reason in opp['reasons'][:3]:  # Top 3 reasons
                    message += f"• {reason}\n"
            
            message += "━━━━━━━━━━━━━━━━━━━━\n\n"
    
    # Footer with action items
    has_critical = any(a['risk_level'] in ['CRITICAL', 'HIGH'] for a in sorted_alerts) if alerts else False
    
    if has_critical:
        message += "<b>⚠️  ACTION REQUIRED</b>\n"
        message += "• Be at computer/phone at <b>9:25 AM ET</b>\n"
        message += "• Prepare to exit positions if needed\n"
        
        # Calculate time until market open
        market_open = now_et.replace(hour=9, minute=30, second=0, microsecond=0)
        if now_et < market_open:
            delta = market_open - now_et
            minutes = int(delta.total_seconds() / 60)
            message += f"• Market opens in <b>{minutes} minutes</b>\n"
        else:
            message += "• <b>MARKET IS NOW OPEN!</b>\n"
    else:
        message += "✅ <b>All positions look stable</b>\n"
        message += "Continue monitoring until market open\n"
    
    return message


def save_alerts_to_file(alerts, market_sentiment):
    """Save alerts to JSON file for debugging/review"""
    try:
        logs_dir = PROJECT_ROOT / 'logs'
        logs_dir.mkdir(exist_ok=True)
        
        et_tz = pytz.timezone('America/New_York')
        timestamp = datetime.now(et_tz).strftime('%Y%m%d_%H%M%S')
        
        log_file = logs_dir / f'premarket_alerts_{timestamp}.json'
        
        data = {
            'timestamp': datetime.now(et_tz).isoformat(),
            'market_sentiment': market_sentiment,
            'alerts': alerts
        }
        
        with open(log_file, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        
        print(f"💾 Alerts saved to: {log_file}")
    
    except Exception as e:
        print(f"⚠️  Could not save alerts to file: {e}")


def main():
    print("="*80)
    print("PRE-MARKET GAP MONITOR")
    print("="*80)
    
    # Load configuration
    print("\n📋 Loading configuration...")
    config = load_config()
    
    positions = config.get('positions', {})
    
    if not positions:
        print("\nℹ️  No positions configured in premarket_config.yaml")
        
        if not config.get('telegram', {}).get('send_if_no_positions', False):
            print("   Skipping alert (send_if_no_positions = false)")
            return
        
        print("   Sending 'no positions' alert...")
    else:
        print(f"📊 Monitoring {len(positions)} position(s): {', '.join(positions.keys())}")
    
    # Monitor positions
    print("\n🔍 Checking pre-market prices...")
    monitor = PreMarketMonitor(positions)
    alerts = monitor.monitor_all_positions()
    
    # Get market sentiment
    print("\n📊 Checking market futures...")
    futures = FuturesMonitor()
    market_sentiment = futures.get_futures_sentiment()
    
    # Get VIX data
    print()
    vix_data = futures.get_vix_sentiment()
    
    # Scan for gap opportunities (NEW!)
    opportunities = []
    if config.get('telegram', {}).get('include_opportunities', True):
        print("\n🔍 Scanning for gap opportunities...")
        
        # Load S&P 500 symbols or use configured scan list
        scan_symbols = config.get('opportunity_scanner', {}).get('symbols_to_scan', [])
        
        if not scan_symbols:
            # Try to load from S&P 500 list
            sp500_file = PROJECT_ROOT / 'data' / 'metadata' / 'sp500_symbols.json'
            if sp500_file.exists():
                import json
                with open(sp500_file) as f:
                    sp500_data = json.load(f)
                    scan_symbols = [item['symbol'] for item in sp500_data.get('symbols', [])]
                    print(f"   Loaded {len(scan_symbols)} symbols from S&P 500 list")
            else:
                # Fallback to a smaller list for testing
                scan_symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'TSLA', 'META', 'NFLX']
                print(f"   Using fallback list of {len(scan_symbols)} symbols")
        
        min_gap = config.get('opportunity_scanner', {}).get('min_gap_pct', 2.0)
        max_opportunities = config.get('opportunity_scanner', {}).get('max_opportunities', 5)
        
        scanner = PreMarketOpportunityScanner(scan_symbols)
        opportunities = scanner.scan_for_opportunities(min_gap_pct=min_gap, max_symbols=max_opportunities)
        
        if opportunities:
            print(f"   ✅ Found {len(opportunities)} gap opportunities!")
        else:
            print("   ℹ️  No significant gaps found")
    
    # Format message
    print("\n📝 Formatting alert message...")
    message = format_telegram_message(alerts, market_sentiment, vix_data, opportunities, config)
    
    # Save to file if configured
    if config.get('debug', {}).get('save_alerts_to_file', False):
        save_alerts_to_file(alerts, market_sentiment)
    
    # Send to Telegram
    if config.get('telegram', {}).get('send_alerts', True):
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        chat_id = os.getenv('TELEGRAM_CHAT_ID')
        
        if not bot_token or not chat_id:
            print("\n⚠️  Telegram credentials not found!")
            print("   Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID environment variables")
            print("\n📱 Message preview:")
            print("="*80)
            # Remove HTML tags for console display
            console_msg = message.replace('<b>', '').replace('</b>', '')
            console_msg = console_msg.replace('<i>', '').replace('</i>', '')
            print(console_msg)
            print("="*80)
            return
        
        print("📱 Sending to Telegram...")
        success = send_telegram_message(bot_token, chat_id, message)
        
        if success:
            print("✅ Alert sent successfully!")
        else:
            print("❌ Failed to send alert")
    else:
        print("\n📱 Telegram alerts disabled in config")
    
    # Print summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    
    if alerts:
        risk_counts = {}
        for alert in alerts:
            level = alert['risk_level']
            risk_counts[level] = risk_counts.get(level, 0) + 1
        
        print(f"\nTotal Alerts: {len(alerts)}")
        for level in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
            if level in risk_counts:
                emoji = {'CRITICAL': '🚨', 'HIGH': '⚠️', 'MEDIUM': '🟡', 'LOW': '✅'}[level]
                print(f"  {emoji} {level}: {risk_counts[level]}")
    else:
        print("\n✅ No alerts (no positions tracked)")
    
    if market_sentiment:
        print(f"\nMarket Sentiment: {market_sentiment.get('overall_sentiment', 'N/A')} "
              f"({market_sentiment.get('avg_change', 0):+.2f}%)")
    
    print("\n" + "="*80)
    print("✅ Pre-market monitor complete!")
    print("="*80)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

