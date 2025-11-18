#!/bin/bash
# Weekly Portfolio Rebalancing (macOS/Linux)
# Run this every Monday evening or when you want comprehensive rebalancing

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "========================================"
echo "  Weekly Portfolio Rebalancing"
echo "========================================"
echo "Date: $(date)"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${RED}✗${NC} Virtual environment not found!"
    echo "   Run: python3 -m venv venv && source venv/bin/activate && pip install -r requirements-base.txt"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check environment variables
if [ -z "$TELEGRAM_BOT_TOKEN" ] || [ -z "$TELEGRAM_CHAT_ID" ]; then
    echo -e "${YELLOW}⚠${NC}  Telegram credentials not set (alerts will be skipped)"
    echo "   Set: TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID"
    echo ""
fi

# ============================================================================
# STEP 1: Update Latest Data
# ============================================================================
echo -e "${BLUE}=== Step 1: Updating Market Data ===${NC}"
python src/fetch_daily_prices.py
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Market data updated"
else
    echo -e "${RED}✗${NC} Failed to update market data"
fi

# ============================================================================
# STEP 2: Run Full Portfolio Rebalancing Analysis
# ============================================================================
echo ""
echo -e "${BLUE}=== Step 2: Running Portfolio Rebalancing ===${NC}"
python scripts/portfolio_rebalancer.py
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Rebalancing analysis completed"
else
    echo -e "${RED}✗${NC} Failed to run rebalancing analysis"
    exit 1
fi

# ============================================================================
# STEP 3: Scan All Sector ETFs for Opportunities
# ============================================================================
echo ""
echo -e "${BLUE}=== Step 3: Scanning All 11 Sector ETFs ===${NC}"
python scripts/daily_etf_trades.py --category recommended_sector_rotation --max-per-category 2
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Sector ETF scan completed"
else
    echo -e "${RED}✗${NC} Failed to scan sector ETFs"
fi

# ============================================================================
# END OF WORKFLOW
# ============================================================================

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  ✓ Weekly Rebalancing Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "📊 Summary:"
echo "  - Market data updated"
echo "  - Portfolio rebalancing analyzed"
echo "  - All 11 sector ETFs scanned"
echo ""
echo "📁 Check outputs in:"
echo "  - signals/rebalancing_report.txt"
echo "  - signals/rebalancing_orders.json"
echo "  - signals/daily_etf_trades.json"
echo ""

# Show detailed rebalancing results
if [ -f "signals/rebalancing_orders.json" ]; then
    echo "🔄 Rebalancing Analysis:"
    ORDERS=$(python3 -c "import json; data=json.load(open('signals/rebalancing_orders.json')); print(data.get('total_orders', 0))")

    if [ "$ORDERS" -gt 0 ]; then
        echo ""
        echo -e "${YELLOW}⚠️  REBALANCING NEEDED: $ORDERS trade orders${NC}"
        echo ""

        # Count sells and buys
        SELLS=$(python3 -c "import json; data=json.load(open('signals/rebalancing_orders.json')); print(len([o for o in data.get('orders', []) if o.get('action') == 'SELL']))")
        BUYS=$(python3 -c "import json; data=json.load(open('signals/rebalancing_orders.json')); print(len([o for o in data.get('orders', []) if o.get('action') == 'BUY']))")

        echo "   📉 SELL orders: $SELLS (take profits)"
        echo "   📈 BUY orders: $BUYS (buy opportunities)"
        echo ""
        echo "   📋 Review detailed report:"
        echo "      cat signals/rebalancing_report.txt"
        echo ""
        echo "   💡 Execute these trades to rebalance your portfolio"
        echo "   💡 This implements automatic 'buy low, sell high'!"
    else
        echo "   ✅ Portfolio is balanced - no trades needed"
    fi
elif [ -f "signals/rebalancing_report.txt" ]; then
    echo "🔄 Rebalancing Analysis:"
    echo "   ✅ Portfolio is balanced - no trades needed"
fi

# Show sector ETF results
if [ -f "signals/daily_etf_trades.json" ]; then
    echo ""
    echo "📊 Sector ETF Analysis:"
    TRADES=$(python3 -c "import json; data=json.load(open('signals/daily_etf_trades.json')); print(data.get('total_trades', 0))")
    CATEGORIES=$(python3 -c "import json; data=json.load(open('signals/daily_etf_trades.json')); print(data.get('categories_covered', 0))")
    echo "   ✓ Found $TRADES opportunities across $CATEGORIES sectors"
fi

echo ""
echo "💡 Next Steps:"
echo "   1. Review Telegram alerts"
echo "   2. Check signals/rebalancing_report.txt"
echo "   3. Execute recommended trades"
echo "   4. Update config/portfolio_allocation.yaml with new holdings"
echo ""
