#!/usr/bin/env python3
"""
Send Trading Signals to Telegram
Simple bot that fetches signals from GitHub and sends to your Telegram chat.

Setup:
1. Create a bot: Talk to @BotFather on Telegram
2. Get your bot token
3. Get your chat ID: Talk to @userinfobot on Telegram
4. Set environment variables or update this script

Usage:
    # Set env vars (recommended for security)
    export TELEGRAM_BOT_TOKEN="your_bot_token"
    export TELEGRAM_CHAT_ID="your_chat_id"
    export GITHUB_REPO="username/daily_market_automation"

    python scripts/send_telegram_signals.py

    # Or run with arguments
    python scripts/send_telegram_signals.py --token YOUR_TOKEN --chat YOUR_CHAT_ID
"""

import requests
import json
import os
import argparse
from datetime import datetime


def send_telegram_message(bot_token: str, chat_id: str, message: str, parse_mode: str = "HTML"):
    """Send a message via Telegram Bot API"""
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": parse_mode,
        "disable_web_page_preview": True
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"❌ Failed to send Telegram message: {e}")
        return False


def fetch_signals_from_github(repo: str, branch: str = "main") -> dict:
    """Fetch trading signals from GitHub"""
    url = f"https://raw.githubusercontent.com/{repo}/{branch}/signals/trading_signals.json"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"❌ Failed to fetch signals: {e}")
        return None


def format_signal_message(data: dict) -> str:
    """Format signals into a nice Telegram message with HTML"""

    if not data:
        return "❌ <b>Error fetching signals</b>"

    summary = data.get('summary', {})
    signals = data.get('signals', [])

    # Header
    generated_time = summary.get('generated_at', 'Unknown')
    try:
        dt = datetime.fromisoformat(generated_time.replace('Z', '+00:00'))
        time_str = dt.strftime('%Y-%m-%d %I:%M %p')
    except:
        time_str = generated_time

    message = f"📊 <b>Trading Signals Report</b>\n"
    message += f"🕐 Generated: {time_str}\n\n"

    # Summary
    message += f"📈 <b>Summary:</b>\n"
    message += f"• Symbols Analyzed: {summary.get('total_symbols_analyzed', 0)}\n"
    message += f"• Confirmed Breakouts: {summary.get('confirmed_breakouts', 0)}\n"
    message += f"  🟢 BUY: {summary.get('buy_signals', 0)}\n"
    message += f"  🔴 SELL: {summary.get('sell_signals', 0)}\n"
    message += f"  ⚪ WATCH: {summary.get('watch_signals', 0)}\n\n"

    # Signals
    if signals:
        message += "🎯 <b>Actionable Signals:</b>\n\n"

        for signal in signals:
            emoji = "🟢" if signal['signal'] == 'BUY' else "🔴" if signal['signal'] == 'SELL' else "⚪"

            message += f"{emoji} <b>{signal['signal']}: {signal['symbol']}</b>\n"
            message += f"💵 Price: ${signal['price']:.2f}\n"
            message += f"⭐ Score: {signal['confirmation_score']}/6\n"
            message += f"📊 Volume: {signal['details']['volume_ratio']:.2f}x avg\n"
            message += f"📈 Trend: {signal['details']['trend_direction']}\n"
            message += f"🎯 Type: {signal['breakout_type']}\n"

            # Support/Resistance levels
            support = signal['details']['support']
            resistance = signal['details']['resistance']
            message += f"📉 Support: ${support:.2f}\n"
            message += f"📈 Resistance: ${resistance:.2f}\n"
            message += f"\n"
    else:
        message += "✅ <b>No confirmed breakouts today.</b>\n"
        message += "Hold positions and monitor.\n"

    message += f"\n────────────────────\n"
    message += f"🔗 View details: <a href='https://github.com/{os.getenv('GITHUB_REPO', 'your-repo')}/blob/main/signals/trading_signals.json'>JSON</a>"

    return message


def main():
    parser = argparse.ArgumentParser(description='Send trading signals to Telegram')
    parser.add_argument('--token', help='Telegram bot token (or set TELEGRAM_BOT_TOKEN env var)')
    parser.add_argument('--chat', help='Telegram chat ID (or set TELEGRAM_CHAT_ID env var)')
    parser.add_argument('--repo', help='GitHub repo (or set GITHUB_REPO env var)',
                       default='ravi4j/daily_market_automation')
    parser.add_argument('--branch', default='main', help='GitHub branch (default: main)')
    parser.add_argument('--min-score', type=int, default=0,
                       help='Only send signals with score >= N (default: 0, all signals)')

    args = parser.parse_args()

    # Get credentials
    bot_token = args.token or os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = args.chat or os.getenv('TELEGRAM_CHAT_ID')
    repo = args.repo or os.getenv('GITHUB_REPO', 'ravi4j/daily_market_automation')

    if not bot_token or not chat_id:
        print("❌ Error: Telegram credentials not provided!")
        print("\nSetup Instructions:")
        print("1. Create bot: Talk to @BotFather on Telegram")
        print("2. Get chat ID: Talk to @userinfobot on Telegram")
        print("3. Set environment variables:")
        print("   export TELEGRAM_BOT_TOKEN='your_bot_token'")
        print("   export TELEGRAM_CHAT_ID='your_chat_id'")
        print("   export GITHUB_REPO='username/daily_market_automation'")
        return

    print(f"📡 Fetching signals from: {repo}")

    # Fetch signals
    data = fetch_signals_from_github(repo, args.branch)

    if not data:
        send_telegram_message(bot_token, chat_id, "❌ Failed to fetch trading signals from GitHub")
        return

    # Filter by minimum score if specified
    if args.min_score > 0:
        signals = data.get('signals', [])
        filtered = [s for s in signals if s['confirmation_score'] >= args.min_score]
        data['signals'] = filtered
        data['summary']['confirmed_breakouts'] = len(filtered)

        # Update signal counts
        buy_count = sum(1 for s in filtered if s['signal'] == 'BUY')
        sell_count = sum(1 for s in filtered if s['signal'] == 'SELL')
        watch_count = sum(1 for s in filtered if s['signal'] == 'WATCH')

        data['summary']['buy_signals'] = buy_count
        data['summary']['sell_signals'] = sell_count
        data['summary']['watch_signals'] = watch_count

    # Format and send message
    message = format_signal_message(data)

    print("📤 Sending to Telegram...")

    if send_telegram_message(bot_token, chat_id, message):
        print("✅ Signals sent successfully!")

        # Print summary
        summary = data.get('summary', {})
        if summary.get('confirmed_breakouts', 0) > 0:
            print(f"\n🎯 Sent {summary['confirmed_breakouts']} signals:")
            print(f"   🟢 BUY: {summary.get('buy_signals', 0)}")
            print(f"   🔴 SELL: {summary.get('sell_signals', 0)}")
            print(f"   ⚪ WATCH: {summary.get('watch_signals', 0)}")
    else:
        print("❌ Failed to send message")


if __name__ == "__main__":
    main()
