#!/usr/bin/env python3
"""
Send analysis report to Telegram
"""

import os
import sys
import json
import argparse
import requests


def send_to_telegram(report: dict):
    """Send formatted analysis to Telegram"""
    
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    if not bot_token or not chat_id:
        print("⚠️  Telegram not configured (TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID required)")
        return False
    
    # Format the message
    symbol = report['symbol']
    rec = report['recommendation']
    
    # Emojis
    if rec == 'BUY':
        emoji = '🟢'
    elif rec == 'SELL':
        emoji = '🔴'
    else:
        emoji = '⚪'
    
    conf_emoji = {
        'HIGH': '⭐⭐⭐',
        'MEDIUM': '⭐⭐',
        'LOW': '⭐'
    }.get(report['confidence'], '⭐')
    
    # Build message
    message = f"🔍 <b>On-Demand Analysis: {symbol}</b>\n\n"
    message += f"<b>{report['company_name']}</b>\n"
    message += f"💰 Current Price: <b>${report['current_price']}</b>\n\n"
    
    # Price changes
    message += "<b>📊 Price Changes:</b>\n"
    changes = report['price_changes']
    for period, change in [('1 Day', '1_day'), ('5 Days', '5_day'), ('1 Month', '1_month')]:
        val = changes[change]
        change_emoji = '🟢' if val > 0 else '🔴' if val < 0 else '⚪'
        message += f"  {change_emoji} {period:8s}: {val:+.2f}%\n"
    
    # Technical indicators
    message += "\n<b>📈 Technical Indicators:</b>\n"
    ti = report['technical_indicators']
    message += f"  • RSI: {ti['RSI']:.1f}"
    if ti['RSI'] < 30:
        message += " (Oversold)"
    elif ti['RSI'] > 70:
        message += " (Overbought)"
    message += "\n"
    
    message += f"  • MACD: {ti['MACD']:.3f} / Signal: {ti['MACD_Signal']:.3f}\n"
    message += f"  • ADX: {ti['ADX']:.1f}"
    if ti['ADX'] > 25:
        message += " (Strong trend)"
    message += "\n"
    
    message += f"  • SMA 20: ${ti['SMA_20']:.2f}\n"
    message += f"  • SMA 50: ${ti['SMA_50']:.2f}\n"
    message += f"  • SMA 200: ${ti['SMA_200']:.2f}\n"
    message += f"  • BB Range: ${ti['BB_Lower']:.2f} - ${ti['BB_Upper']:.2f}\n"
    
    vol_ratio = ti['Volume'] / ti['Volume_SMA'] if ti['Volume_SMA'] > 0 else 1
    message += f"  • Volume: {ti['Volume']:,} ({vol_ratio:.1f}x avg)\n"
    
    # Signals
    message += "\n<b>🎯 Signals Detected:</b>\n"
    if report['signals']:
        buy_count = report.get('buy_signals_count', 0)
        sell_count = report.get('sell_signals_count', 0)
        message += f"  📊 {buy_count} BUY signals, {sell_count} SELL signals\n\n"
        
        for sig in report['signals'][:5]:  # Show top 5
            sig_emoji = '🟢' if sig['signal'] == 'BUY' else '🔴'
            conf_badge = '⭐⭐⭐' if sig['confidence'] == 'HIGH' else '⭐⭐'
            message += f"  {sig_emoji} <b>{sig['strategy']}</b> {conf_badge}\n"
            message += f"     {sig['reason']}\n"
    else:
        message += "  No strong signals detected\n"
    
    # Recommendation
    message += f"\n<b>💡 Recommendation: {emoji} {rec} {conf_emoji}</b>\n"
    message += f"<i>Confidence: {report['confidence']}</i>\n"
    
    # Footer
    message += f"\n📅 Analysis based on {report['data_points']} days\n"
    message += f"<i>Period: {report['date_range']}</i>"
    
    # Send to Telegram
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'HTML'
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        print(f"✅ Analysis sent to Telegram for {symbol}")
        return True
    except Exception as e:
        print(f"❌ Failed to send to Telegram: {e}")
        return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--symbol', required=True)
    parser.add_argument('--report', required=True, help='JSON report file')
    
    args = parser.parse_args()
    
    try:
        with open(args.report, 'r') as f:
            report = json.load(f)
        
        success = send_to_telegram(report)
        return 0 if success else 1
    except FileNotFoundError:
        print(f"❌ Report file not found: {args.report}")
        return 1
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

