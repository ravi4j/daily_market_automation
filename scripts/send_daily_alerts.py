#!/usr/bin/env python3
"""
Send Daily Trading Alerts via Telegram
Runs strategies and sends buy/sell alerts
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import os
import requests
import argparse
from strategy_runner import StrategyRunner


def send_telegram_message(bot_token: str, chat_id: str, message: str):
    """Send message via Telegram Bot API"""
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"❌ Failed to send Telegram message: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description='Send daily trading alerts via Telegram')
    parser.add_argument('--token', help='Telegram bot token (or set TELEGRAM_BOT_TOKEN env var)')
    parser.add_argument('--chat', help='Telegram chat ID (or set TELEGRAM_CHAT_ID env var)')
    parser.add_argument('--min-confidence', choices=['LOW', 'MEDIUM', 'HIGH'],
                       default='MEDIUM', help='Minimum confidence level')
    parser.add_argument('--strategies', nargs='+',
                       choices=['rsi_macd', 'trend_following', 'mean_reversion', 'momentum_breakout'],
                       help='Strategies to run (default: all)')

    args = parser.parse_args()

    # Get credentials
    bot_token = args.token or os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = args.chat or os.getenv('TELEGRAM_CHAT_ID')

    if not bot_token or not chat_id:
        print("❌ Error: Telegram credentials not found!")
        print("\nPlease set environment variables:")
        print("   export TELEGRAM_BOT_TOKEN='your_bot_token'")
        print("   export TELEGRAM_CHAT_ID='your_chat_id'")
        print("\nOr use command-line arguments:")
        print("   python scripts/send_daily_alerts.py --token YOUR_TOKEN --chat YOUR_CHAT_ID")
        sys.exit(1)

    print("="*80)
    print("📱 DAILY TRADING ALERTS - TELEGRAM SENDER")
    print("="*80)

    # Run strategies
    runner = StrategyRunner()
    alerts = runner.run_daily_analysis(
        strategies=args.strategies,
        min_confidence=args.min_confidence
    )

    # Print summary
    runner.print_summary()

    # Save alerts
    runner.save_alerts()

    # Send via Telegram
    if not alerts:
        message = (
            "✅ <b>Daily Market Analysis Complete</b>\n\n"
            "No trading alerts today.\n"
            "All positions hold steady.\n\n"
            f"<i>Analyzed: {', '.join(runner.discover_symbols())}</i>"
        )

        print("\n📱 Sending 'no alerts' message to Telegram...")
        success = send_telegram_message(bot_token, chat_id, message)

        if success:
            print("✅ Message sent successfully!")
        else:
            print("❌ Failed to send message")

        return

    # Combine ALL alerts into ONE message
    buy_count = len([a for a in alerts if a.signal == 'BUY'])
    sell_count = len([a for a in alerts if a.signal == 'SELL'])
    high_conf = len([a for a in alerts if a.confidence == 'HIGH'])

    # Start with summary
    message = (
        "🚨 <b>DAILY TRADING ALERTS</b> 🚨\n\n"
        f"<b>Total Alerts:</b> {len(alerts)}\n"
        f"  🟢 BUY: {buy_count}\n"
        f"  🔴 SELL: {sell_count}\n\n"
        f"<b>High Confidence:</b> ⭐⭐⭐ {high_conf}\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
    )

    # Sort alerts (HIGH confidence first)
    alerts_sorted = sorted(alerts, key=lambda x: (
        0 if x.confidence == 'HIGH' else 1 if x.confidence == 'MEDIUM' else 2,
        x.symbol
    ))

    # Add each alert to the same message
    for i, alert in enumerate(alerts_sorted, 1):
        print(f"   Adding alert {i}/{len(alerts)}: {alert.symbol} {alert.signal}...")

        # Get the formatted message
        alert_text = alert.to_telegram_message()

        # Add separator between alerts (but not before the first one)
        if i > 1:
            message += "\n━━━━━━━━━━━━━━━━━━━━\n\n"

        message += alert_text

    # Add footer
    message += "\n\n⚠️ <i>Not financial advice. DYOR.</i>"

    # Send ONE combined message with all alerts
    print(f"\n📱 Sending combined message with {len(alerts)} alerts to Telegram...")
    success = send_telegram_message(bot_token, chat_id, message)

    if success:
        print("✅ Message sent successfully!")
    else:
        print("❌ Failed to send message")

    print("\n" + "="*80)
    print("✅ All alerts processed!")
    print("="*80)


if __name__ == "__main__":
    main()
