#!/bin/bash
# View Trading Signals from GitHub
# NO AUTHENTICATION REQUIRED - Works with public repos!
#
# Usage:
#   ./scripts/view_signals.sh
#   REPO="username/repo" ./scripts/view_signals.sh

# Configuration
REPO="${REPO:-your-username/daily_market_automation}"
BRANCH="${BRANCH:-main}"
URL="https://raw.githubusercontent.com/${REPO}/${BRANCH}/data/trading_signals.json"

echo "📡 Fetching signals from: $REPO"
echo "🔗 URL: $URL"
echo ""

# Fetch and display signals
if command -v jq &> /dev/null; then
    # If jq is available, pretty print with colors
    echo "================================================================================"
    echo "📊 TRADING SIGNALS"
    echo "================================================================================"

    curl -s "$URL" | jq -r '
        "Generated: \(.summary.generated_at)",
        "Symbols Analyzed: \(.summary.total_symbols_analyzed)",
        "Confirmed Breakouts: \(.summary.confirmed_breakouts)",
        "  🟢 BUY signals: \(.summary.buy_signals)",
        "  🔴 SELL signals: \(.summary.sell_signals)",
        "  ⚪ WATCH signals: \(.summary.watch_signals)",
        "",
        "================================================================================"
    '

    # Display individual signals
    SIGNAL_COUNT=$(curl -s "$URL" | jq '.signals | length')

    if [ "$SIGNAL_COUNT" -gt 0 ]; then
        echo "🎯 ACTIONABLE SIGNALS"
        echo "================================================================================"

        curl -s "$URL" | jq -r '.signals[] |
            (if .signal == "BUY" then "🟢" elif .signal == "SELL" then "🔴" else "⚪" end) +
            " " + .signal + " " + .symbol + " @ $" + (.price | tostring) +
            " | Score: " + (.confirmation_score | tostring) + "/6" +
            " | Vol: " + (.details.volume_ratio | tostring) + "x" +
            "\n   └─ " + .breakout_type +
            "\n   └─ Trend: " + .details.trend_direction + "\n"
        '
    else
        echo "✅ No confirmed breakouts today. Hold positions."
    fi
else
    # Fallback to plain JSON if jq not available
    echo "⚠️  Install 'jq' for better formatting: brew install jq (macOS) or apt-get install jq (Linux)"
    echo ""
    curl -s "$URL" | python3 -m json.tool
fi

echo ""
echo "================================================================================"
echo "📁 View full JSON: https://github.com/${REPO}/blob/${BRANCH}/data/trading_signals.json"
echo "================================================================================"
