#!/bin/bash
################################################################################
# PRE-MARKET SCANNER - macOS/Linux
# Run before market open (4:00 AM - 9:30 AM ET)
################################################################################

set -e

echo "================================================================================="
echo "🌅 PRE-MARKET GAP SCANNER"
echo "================================================================================="
echo ""

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

# Activate virtual environment
if [ ! -d ".venv" ] && [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found! Run: ./scripts/setup_local.sh"
    exit 1
fi

if [ -d ".venv" ]; then
    source .venv/bin/activate
else
    source venv/bin/activate
fi

# Load environment variables
if [ -f ".env" ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

echo "This will:"
echo "  1. Check your portfolio positions for gaps"
echo "  2. Scan market for gap opportunities (gap downs + gap ups)"
echo "  3. Send Telegram alert with actionable insights"
echo ""

# Run pre-market scan
python scripts/master_daily_scan.py --mode premarket

echo ""
echo "✅ Pre-market scan complete!"
echo ""
