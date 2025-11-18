"""
Portfolio Rebalancer
Automatically maintains target allocations and implements "buy low, sell high"
"""

import os
import sys
import yaml
import yfinance as yf
import pandas as pd
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def load_config() -> Dict:
    """Load portfolio allocation configuration"""
    config_file = PROJECT_ROOT / 'config' / 'portfolio_allocation.yaml'

    if not config_file.exists():
        print("❌ portfolio_allocation.yaml not found!")
        print(f"   Expected at: {config_file}")
        sys.exit(1)

    with open(config_file) as f:
        return yaml.safe_load(f)


def get_current_prices(symbols: List[str]) -> Dict[str, float]:
    """Fetch current prices for symbols"""
    prices = {}

    for symbol in symbols:
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period='1d')

            if not data.empty:
                prices[symbol] = float(data['Close'].iloc[-1])
            else:
                print(f"   ⚠️  No price data for {symbol}")

        except Exception as e:
            print(f"   ⚠️  Error fetching {symbol}: {e}")

    return prices


def calculate_current_allocation(holdings: Dict, prices: Dict) -> Tuple[Dict, float]:
    """
    Calculate current portfolio allocation

    Returns:
        (allocation_dict, total_value)
    """
    # Calculate current value of each holding
    holdings_value = {}
    total_value = 0

    for symbol, position in holdings.items():
        if symbol in prices:
            current_value = position['shares'] * prices[symbol]
            holdings_value[symbol] = current_value
            total_value += current_value

    # Group by category
    config = load_config()
    etf_mappings = config['etf_mappings']

    category_values = {}

    for category, etfs in etf_mappings.items():
        category_value = sum(holdings_value.get(etf, 0) for etf in etfs if etf in holdings_value)
        category_values[category] = category_value

    # Calculate percentages
    current_allocation = {}

    if total_value > 0:
        for category, value in category_values.items():
            current_allocation[category] = (value / total_value) * 100

    return current_allocation, total_value


def calculate_rebalancing_needs(config: Dict, current_allocation: Dict,
                                total_value: float) -> Dict:
    """
    Calculate which categories need rebalancing

    Returns:
        Dict with category -> {target%, current%, drift%, action, amount}
    """
    target_allocation = config['target_allocation']
    drift_threshold = config['rebalancing']['drift_threshold']

    rebalancing_needs = {}

    for category, target_pct in target_allocation.items():
        current_pct = current_allocation.get(category, 0)
        drift = current_pct - target_pct
        drift_abs = abs(drift)

        # Determine action
        if drift_abs >= drift_threshold:
            if drift > 0:
                action = 'SELL'  # Over-allocated (sell high!)
            else:
                action = 'BUY'   # Under-allocated (buy low!)
        else:
            action = 'HOLD'  # Within threshold

        # Calculate dollar amount to rebalance
        target_value = (target_pct / 100) * total_value
        current_value = (current_pct / 100) * total_value
        amount = target_value - current_value

        rebalancing_needs[category] = {
            'target_pct': target_pct,
            'current_pct': round(current_pct, 2),
            'drift_pct': round(drift, 2),
            'drift_abs': round(drift_abs, 2),
            'action': action,
            'amount': round(amount, 2),
            'target_value': round(target_value, 2),
            'current_value': round(current_value, 2)
        }

    return rebalancing_needs


def generate_trade_orders(config: Dict, rebalancing_needs: Dict,
                         holdings: Dict, prices: Dict) -> List[Dict]:
    """
    Generate specific buy/sell orders to rebalance portfolio

    Returns:
        List of trade orders
    """
    etf_mappings = config['etf_mappings']
    min_trade = config['rebalancing']['min_trade_dollars']

    orders = []

    # Process sells first (free up capital)
    for category, needs in rebalancing_needs.items():
        if needs['action'] == 'SELL' and abs(needs['amount']) >= min_trade:
            # Find which ETFs in this category to sell
            etfs_in_category = etf_mappings.get(category, [])

            for etf in etfs_in_category:
                if etf in holdings and etf in prices:
                    position = holdings[etf]
                    current_value = position['shares'] * prices[etf]

                    # Calculate how much to sell from this position
                    # Sell proportionally from all holdings in category
                    total_category_value = sum(
                        holdings[e]['shares'] * prices[e]
                        for e in etfs_in_category
                        if e in holdings and e in prices
                    )

                    if total_category_value > 0:
                        proportion = current_value / total_category_value
                        sell_value = abs(needs['amount']) * proportion
                        sell_shares = int(sell_value / prices[etf])

                        if sell_shares > 0 and sell_shares <= position['shares']:
                            # Calculate P&L
                            cost_basis = position['avg_cost'] * sell_shares
                            proceeds = prices[etf] * sell_shares
                            pnl = proceeds - cost_basis
                            pnl_pct = (pnl / cost_basis) * 100

                            orders.append({
                                'action': 'SELL',
                                'symbol': etf,
                                'shares': sell_shares,
                                'price': prices[etf],
                                'value': round(sell_value, 2),
                                'category': category,
                                'reason': f'Rebalance: Over-allocated by {needs["drift_abs"]:.1f}%',
                                'pnl': round(pnl, 2),
                                'pnl_pct': round(pnl_pct, 2)
                            })

    # Process buys (allocate capital)
    for category, needs in rebalancing_needs.items():
        if needs['action'] == 'BUY' and abs(needs['amount']) >= min_trade:
            # Find best ETF in this category to buy
            etfs_in_category = etf_mappings.get(category, [])

            # Load ETF scores if available
            scores_file = PROJECT_ROOT / 'signals' / 'daily_etf_trades.json'
            etf_scores = {}

            if scores_file.exists():
                import json
                with open(scores_file) as f:
                    data = json.load(f)
                    for trade in data.get('trades', []):
                        etf_scores[trade['symbol']] = trade['total_score']

            # Find best ETF to buy (highest score or first available)
            best_etf = None
            best_score = 0

            for etf in etfs_in_category:
                if etf in prices:
                    score = etf_scores.get(etf, 50)
                    if score > best_score:
                        best_score = score
                        best_etf = etf

            if not best_etf and etfs_in_category:
                best_etf = etfs_in_category[0]  # Fallback

            if best_etf and best_etf in prices:
                buy_value = abs(needs['amount'])
                buy_shares = int(buy_value / prices[best_etf])

                if buy_shares > 0:
                    orders.append({
                        'action': 'BUY',
                        'symbol': best_etf,
                        'shares': buy_shares,
                        'price': prices[best_etf],
                        'value': round(buy_shares * prices[best_etf], 2),
                        'category': category,
                        'reason': f'Rebalance: Under-allocated by {needs["drift_abs"]:.1f}%',
                        'score': best_score
                    })

    # Limit number of trades
    max_trades = config['rebalancing']['max_trades_per_session']

    if len(orders) > max_trades:
        # Prioritize by drift magnitude
        orders.sort(key=lambda x: abs(rebalancing_needs[x['category']]['drift_abs']), reverse=True)
        orders = orders[:max_trades]

    return orders


def format_rebalancing_report(config: Dict, current_allocation: Dict,
                              total_value: float, rebalancing_needs: Dict,
                              orders: List[Dict]) -> str:
    """Format rebalancing report"""

    report = "="*80 + "\n"
    report += "PORTFOLIO REBALANCING REPORT\n"
    report += "="*80 + "\n"
    report += f"Date: {datetime.now().strftime('%B %d, %Y %I:%M %p')}\n"
    report += f"Total Portfolio Value: ${total_value:,.2f}\n\n"

    # Current vs Target Allocation
    report += "CURRENT ALLOCATION vs TARGET\n"
    report += "-"*80 + "\n"
    report += f"{'Category':<25} {'Target':<10} {'Current':<10} {'Drift':<10} {'Action':<10}\n"
    report += "-"*80 + "\n"

    for category, needs in sorted(rebalancing_needs.items()):
        emoji = "🔴" if needs['action'] == 'SELL' else "🟢" if needs['action'] == 'BUY' else "⚪"
        report += f"{emoji} {category:<23} {needs['target_pct']:>6.1f}%  {needs['current_pct']:>7.1f}%  "
        report += f"{needs['drift_pct']:>+7.1f}%  {needs['action']:<10}\n"

    report += "\n"

    # Rebalancing needs
    needs_rebalancing = [c for c, n in rebalancing_needs.items() if n['action'] != 'HOLD']

    if needs_rebalancing:
        report += "REBALANCING NEEDED\n"
        report += "-"*80 + "\n"

        for category in needs_rebalancing:
            needs = rebalancing_needs[category]
            report += f"\n{category.upper()}:\n"
            report += f"  Current: ${needs['current_value']:,.2f} ({needs['current_pct']:.1f}%)\n"
            report += f"  Target:  ${needs['target_value']:,.2f} ({needs['target_pct']:.1f}%)\n"
            report += f"  Action:  {needs['action']} ${abs(needs['amount']):,.2f}\n"

        report += "\n"
    else:
        report += "✅ Portfolio is balanced! No trades needed.\n\n"

    # Trade orders
    if orders:
        report += "RECOMMENDED TRADES\n"
        report += "="*80 + "\n"

        total_sells = sum(o['value'] for o in orders if o['action'] == 'SELL')
        total_buys = sum(o['value'] for o in orders if o['action'] == 'BUY')

        report += f"Total Sells: ${total_sells:,.2f}\n"
        report += f"Total Buys:  ${total_buys:,.2f}\n\n"

        # Sell orders first
        sells = [o for o in orders if o['action'] == 'SELL']
        if sells:
            report += "SELL ORDERS (Free up capital):\n"
            report += "-"*80 + "\n"

            for order in sells:
                report += f"\n📉 SELL {order['shares']} shares of {order['symbol']} @ ${order['price']:.2f}\n"
                report += f"   Value: ${order['value']:,.2f}\n"
                report += f"   Category: {order['category']}\n"
                report += f"   Reason: {order['reason']}\n"
                if 'pnl' in order:
                    pnl_emoji = "📈" if order['pnl'] > 0 else "📉"
                    report += f"   P&L: {pnl_emoji} ${order['pnl']:+,.2f} ({order['pnl_pct']:+.1f}%)\n"

        # Buy orders
        buys = [o for o in orders if o['action'] == 'BUY']
        if buys:
            report += "\nBUY ORDERS (Allocate capital):\n"
            report += "-"*80 + "\n"

            for order in buys:
                report += f"\n📈 BUY {order['shares']} shares of {order['symbol']} @ ${order['price']:.2f}\n"
                report += f"   Value: ${order['value']:,.2f}\n"
                report += f"   Category: {order['category']}\n"
                report += f"   Reason: {order['reason']}\n"
                if 'score' in order:
                    report += f"   Score: {order['score']}/100\n"

    report += "\n" + "="*80 + "\n"

    return report


def format_telegram_message(config: Dict, current_allocation: Dict,
                           total_value: float, rebalancing_needs: Dict,
                           orders: List[Dict]) -> str:
    """Format Telegram alert message"""

    needs_rebalancing = [c for c, n in rebalancing_needs.items() if n['action'] != 'HOLD']

    if not needs_rebalancing:
        message = "<b>✅ PORTFOLIO BALANCED</b>\n\n"
        message += f"Total Value: ${total_value:,.2f}\n"
        message += "All allocations within target ranges.\n"
        message += "No rebalancing needed today!"
        return message

    message = "<b>🔄 PORTFOLIO REBALANCING</b>\n"
    message += f"<i>{datetime.now().strftime('%B %d, %Y')}</i>\n\n"

    message += f"<b>Portfolio Value: ${total_value:,.2f}</b>\n"
    message += f"<b>Categories needing rebalance: {len(needs_rebalancing)}</b>\n"
    message += "━━━━━━━━━━━━━━━━━━━━\n\n"

    # Show categories needing rebalancing
    for category in needs_rebalancing[:5]:  # Top 5
        needs = rebalancing_needs[category]

        if needs['action'] == 'SELL':
            emoji = "🔴"
            action_text = "OVER-ALLOCATED"
        else:
            emoji = "🟢"
            action_text = "UNDER-ALLOCATED"

        message += f"{emoji} <b>{category.title()}</b> - {action_text}\n"
        message += f"   Current: {needs['current_pct']:.1f}% (Target: {needs['target_pct']:.1f}%)\n"
        message += f"   Drift: {needs['drift_pct']:+.1f}%\n"
        message += f"   Action: {needs['action']} ${abs(needs['amount']):,.0f}\n\n"

    if orders:
        message += "━━━━━━━━━━━━━━━━━━━━\n\n"
        message += f"<b>📋 RECOMMENDED TRADES ({len(orders)})</b>\n\n"

        # Sells
        sells = [o for o in orders if o['action'] == 'SELL']
        if sells:
            message += "<b>SELL (Take Profits):</b>\n"
            for order in sells[:3]:  # Top 3
                message += f"• {order['symbol']}: {order['shares']} shares @ ${order['price']:.2f}\n"
                if 'pnl' in order:
                    pnl_emoji = "📈" if order['pnl'] > 0 else "📉"
                    message += f"  {pnl_emoji} P&L: ${order['pnl']:+,.0f} ({order['pnl_pct']:+.1f}%)\n"
            message += "\n"

        # Buys
        buys = [o for o in orders if o['action'] == 'BUY']
        if buys:
            message += "<b>BUY (Buy the Dip):</b>\n"
            for order in buys[:3]:  # Top 3
                message += f"• {order['symbol']}: {order['shares']} shares @ ${order['price']:.2f}\n"
                if 'score' in order:
                    message += f"  Score: {order['score']}/100\n"

    message += "\n━━━━━━━━━━━━━━━━━━━━\n\n"
    message += "<b>💡 Rebalancing Strategy:</b>\n"
    message += "• Sell high (over-allocated)\n"
    message += "• Buy low (under-allocated)\n"
    message += "• Maintain target allocation\n"
    message += "• Automatic profit-taking\n"

    return message


def save_rebalancing_report(report: str, orders: List[Dict]):
    """Save rebalancing report to file"""
    import json

    # Save text report
    report_file = PROJECT_ROOT / 'signals' / 'rebalancing_report.txt'
    report_file.parent.mkdir(parents=True, exist_ok=True)

    with open(report_file, 'w') as f:
        f.write(report)

    print(f"✅ Report saved to: {report_file}")

    # Save JSON orders
    if orders:
        orders_file = PROJECT_ROOT / 'signals' / 'rebalancing_orders.json'

        output = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'timestamp': datetime.now().isoformat(),
            'total_orders': len(orders),
            'orders': orders
        }

        with open(orders_file, 'w') as f:
            json.dump(output, f, indent=2)

        print(f"✅ Orders saved to: {orders_file}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Portfolio rebalancer')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show report only, don\'t send alerts')
    parser.add_argument('--force', action='store_true',
                       help='Force rebalancing check even if not scheduled')

    args = parser.parse_args()

    print("="*80)
    print("PORTFOLIO REBALANCER")
    print("="*80)
    print(f"Date: {datetime.now().strftime('%B %d, %Y %I:%M %p')}\n")

    # Load configuration
    print("📋 Loading configuration...")
    config = load_config()

    holdings = config['current_holdings']

    if not holdings:
        print("⚠️  No holdings configured in portfolio_allocation.yaml")
        print("   Please add your current positions first.")
        return

    print(f"   Tracking {len(holdings)} position(s)\n")

    # Fetch current prices
    print("💰 Fetching current prices...")
    symbols = list(holdings.keys())
    prices = get_current_prices(symbols)
    print(f"   Got prices for {len(prices)} symbol(s)\n")

    # Calculate current allocation
    print("📊 Calculating current allocation...")
    current_allocation, total_value = calculate_current_allocation(holdings, prices)
    print(f"   Total Portfolio Value: ${total_value:,.2f}\n")

    # Calculate rebalancing needs
    print("🔄 Analyzing rebalancing needs...")
    rebalancing_needs = calculate_rebalancing_needs(config, current_allocation, total_value)

    needs_rebalancing = [c for c, n in rebalancing_needs.items() if n['action'] != 'HOLD']
    print(f"   {len(needs_rebalancing)} category(ies) need rebalancing\n")

    # Generate trade orders
    print("📋 Generating trade orders...")
    orders = generate_trade_orders(config, rebalancing_needs, holdings, prices)
    print(f"   Generated {len(orders)} trade order(s)\n")

    # Format report
    report = format_rebalancing_report(config, current_allocation, total_value,
                                      rebalancing_needs, orders)

    # Print report
    print(report)

    # Save report
    save_rebalancing_report(report, orders)

    # Send to Telegram
    if not args.dry_run and config['alerts']['send_telegram_alert']:
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        chat_id = os.getenv('TELEGRAM_CHAT_ID')

        if bot_token and chat_id:
            print("\n📱 Sending to Telegram...")
            message = format_telegram_message(config, current_allocation, total_value,
                                            rebalancing_needs, orders)

            import requests
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            payload = {
                "chat_id": chat_id,
                "text": message,
                "parse_mode": "HTML"
            }
            response = requests.post(url, json=payload, timeout=10)

            if response.status_code == 200:
                print("✅ Alert sent to Telegram!")
            else:
                print(f"❌ Telegram error: {response.status_code}")
        else:
            print("\n⚠️  Telegram credentials not set (skipping alert)")

    print("\n✅ REBALANCING ANALYSIS COMPLETE!")

    if orders:
        print(f"\n💡 Execute {len(orders)} trade(s) to rebalance portfolio")
        print("💡 This automatically implements 'buy low, sell high'!")
    else:
        print("\n✅ Portfolio is balanced - no trades needed!")


if __name__ == '__main__':
    main()
