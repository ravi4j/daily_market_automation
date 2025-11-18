#!/bin/bash
# Daily ETF Trading & Rebalancing Workflow (macOS/Linux)
# Run this after market close (4:30 PM ET or later)

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "========================================"
echo "  Daily ETF Trading & Rebalancing"
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
    echo -e "${RED}⚠${NC}  Telegram credentials not set (alerts will be skipped)"
    echo "   Set: TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID"
    echo ""
fi

# ============================================================================
# STEP 1: Update Daily Data
# ============================================================================
echo -e "${BLUE}=== Step 1: Updating Market Data ===${NC}"
python src/fetch_daily_prices.py
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Market data updated"
else
    echo -e "${RED}✗${NC} Failed to update market data"
    # Don't exit - continue with available data
fi

# ============================================================================
# STEP 2: Scan ETFs for Daily Trades
# ============================================================================
echo ""
echo -e "${BLUE}=== Step 2: Scanning ETFs for Trades ===${NC}"
python scripts/daily_etf_trades.py --category recommended_daily_trading
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} ETF scan completed"
else
    echo -e "${RED}✗${NC} Failed to scan ETFs"
    exit 1
fi

# ============================================================================
# STEP 3: Check Portfolio Rebalancing
# ============================================================================
echo ""
echo -e "${BLUE}=== Step 3: Checking Portfolio Rebalancing ===${NC}"
python scripts/portfolio_rebalancer.py
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Rebalancing check completed"
else
    echo -e "${RED}✗${NC} Failed to check rebalancing"
    # Don't exit - this is optional
fi

# ============================================================================
# END OF WORKFLOW
# ============================================================================

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  ✓ ETF Workflow Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "📊 Summary:"
echo "  - Market data updated"
echo "  - ETF trades identified"
echo "  - Rebalancing checked"
echo ""
echo "📁 Check outputs in:"
echo "  - signals/daily_etf_trades.json"
echo "  - signals/rebalancing_report.txt (if needed)"
echo "  - signals/rebalancing_orders.json (if needed)"
echo ""

# Show ETF results if available
if [ -f "signals/daily_etf_trades.json" ]; then
    echo "📊 ETF Scan Results:"
    TRADES=$(python3 -c "import json; data=json.load(open('signals/daily_etf_trades.json')); print(data.get('total_trades', 0))")
    CATEGORIES=$(python3 -c "import json; data=json.load(open('signals/daily_etf_trades.json')); print(data.get('categories_covered', 0))")
    echo "   ✓ Found $TRADES opportunities across $CATEGORIES categories"
fi

# Show rebalancing results if available
if [ -f "signals/rebalancing_orders.json" ]; then
    echo ""
    echo "🔄 Rebalancing Results:"
    ORDERS=$(python3 -c "import json; data=json.load(open('signals/rebalancing_orders.json')); print(data.get('total_orders', 0))")
    if [ "$ORDERS" -gt 0 ]; then
        echo "   ⚠️  $ORDERS trade orders generated"
        echo "   📋 Review: signals/rebalancing_report.txt"
    else
        echo "   ✓ Portfolio is balanced"
    fi
elif [ -f "signals/rebalancing_report.txt" ]; then
    echo ""
    echo "🔄 Rebalancing Results:"
    echo "   ✓ Portfolio is balanced (no trades needed)"
fi

echo ""
echo "💡 Next: Review Telegram alerts and execute trades if needed"
echo ""
