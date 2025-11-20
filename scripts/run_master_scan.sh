#!/bin/bash
################################################################################
# MASTER DAILY SCANNER - macOS/Linux
# Intelligent market scanning system
################################################################################

set -e  # Exit on error

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "================================================================================================="
echo -e "${BLUE}🤖 MASTER DAILY MARKET SCANNER${NC}"
echo "================================================================================================="
echo ""

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${RED}❌ Virtual environment not found!${NC}"
    echo ""
    echo "Run setup first:"
    echo "  ./scripts/setup_local.sh"
    exit 1
fi

# Activate virtual environment
echo -e "${BLUE}🔧 Activating virtual environment...${NC}"
source venv/bin/activate

# Check environment variables
if [ -f ".env" ]; then
    export $(cat .env | grep -v '^#' | xargs)
    echo -e "${GREEN}✅ Environment variables loaded${NC}"
else
    echo -e "${YELLOW}⚠️  No .env file found${NC}"
    echo "   Set FINNHUB_API_KEY and TELEGRAM credentials for full functionality"
fi

echo ""
echo "================================================================================================="
echo -e "${BLUE}🚀 STARTING INTELLIGENT MARKET SCAN${NC}"
echo "================================================================================================="
echo ""
echo "This will:"
echo "  1. Fetch complete US market universe (stocks + ETFs)"
echo "  2. Quick pre-screen for opportunities (price drops, volume spikes)"
echo "  3. Deep analysis with multi-signal scoring"
echo "  4. Generate consolidated alert with top 5 trades"
echo ""
echo "Expected time: 5-10 minutes"
echo ""

# Run master scanner
python scripts/master_daily_scan.py

# Check exit code
if [ $? -eq 0 ]; then
    echo ""
    echo "================================================================================================="
    echo -e "${GREEN}✅ SCAN COMPLETE!${NC}"
    echo "================================================================================================="
    echo ""
    echo "Results saved to:"
    echo "  📄 signals/master_scan_results.json"
    echo ""
    echo "Telegram alert sent (if configured)"
    echo ""
else
    echo ""
    echo "================================================================================================="
    echo -e "${RED}❌ SCAN FAILED${NC}"
    echo "================================================================================================="
    echo ""
    exit 1
fi
