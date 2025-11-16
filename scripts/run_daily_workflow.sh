#!/bin/bash
# Daily Market Automation - Complete Workflow
# Run all daily tasks in sequence
# Usage: ./scripts/run_daily_workflow.sh

set -e  # Exit on error

# Get project directory (script's parent's parent directory)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Daily Market Automation Workflow${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Activate virtual environment
if [ -d "venv" ]; then
    echo -e "${GREEN}✓${NC} Activating virtual environment..."
    source venv/bin/activate
else
    echo -e "${RED}✗${NC} Virtual environment not found! Run: python3 -m venv venv"
    exit 1
fi

# Check environment variables
if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    echo -e "${RED}⚠${NC}  TELEGRAM_BOT_TOKEN not set"
fi
if [ -z "$TELEGRAM_CHAT_ID" ]; then
    echo -e "${RED}⚠${NC}  TELEGRAM_CHAT_ID not set"
fi

echo ""
echo -e "${BLUE}=== Step 1: Fetching Market Data ===${NC}"
python src/fetch_daily_prices.py
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Market data fetched successfully"
else
    echo -e "${RED}✗${NC} Failed to fetch market data"
    exit 1
fi

echo ""
echo -e "${BLUE}=== Step 2: Generating Charts ===${NC}"
echo "  → Breakout charts..."
python src/visualize_breakouts.py
echo "  → Indicator charts..."
python src/visualize_breakouts_with_indicators.py
echo "  → ABC pattern charts..."
python src/visualize_abc_patterns.py
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} All charts generated successfully"
else
    echo -e "${RED}✗${NC} Failed to generate charts"
    exit 1
fi

echo ""
echo -e "${BLUE}=== Step 3: Running Trading Strategies ===${NC}"
python scripts/send_daily_alerts.py
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Trading alerts sent successfully"
else
    echo -e "${RED}✗${NC} Failed to send trading alerts"
    exit 1
fi

echo ""
echo -e "${BLUE}=== Step 4: Scanning News for Portfolio ===${NC}"
python scripts/send_news_opportunities.py
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} News opportunities scanned and sent"
else
    echo -e "${RED}✗${NC} Failed to scan news opportunities"
    exit 1
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  ✓ Daily Workflow Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "📊 Summary:"
echo "  - Market data updated"
echo "  - Charts generated"
echo "  - Trading alerts sent"
echo "  - News opportunities scanned"
echo ""
echo "📁 Check outputs in:"
echo "  - data/market_data/*.csv"
echo "  - charts/*/*.png"
echo "  - signals/*.json"
echo ""

