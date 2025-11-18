#!/bin/bash
# Pre-Market Gap Monitor Workflow
# Runs morning gap detection and sends Telegram alerts
# Usage: ./scripts/run_premarket_workflow.sh

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Change to project directory
cd "$(dirname "$0")/.." || exit 1

echo ""
echo -e "${BLUE}============================================================================${NC}"
echo -e "${BLUE}                   PRE-MARKET GAP MONITOR WORKFLOW${NC}"
echo -e "${BLUE}============================================================================${NC}"
echo ""

# Get current time in ET
current_time_et=$(TZ='America/New_York' date '+%I:%M %p ET on %A, %B %d, %Y')
echo -e "${BLUE}📅 Current Time: ${current_time_et}${NC}"
echo ""

# ============================================================================
# PRE-FLIGHT CHECKS
# ============================================================================

echo -e "${BLUE}=== Pre-Flight Checks ===${NC}"

# Check if virtual environment is activated
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo -e "${YELLOW}⚠️  Virtual environment not activated${NC}"
    echo -e "${YELLOW}   Attempting to activate venv...${NC}"
    
    if [ -d "venv" ]; then
        source venv/bin/activate
        echo -e "${GREEN}✓${NC} Virtual environment activated"
    else
        echo -e "${RED}✗${NC} No virtual environment found at ./venv"
        echo -e "${RED}   Run: python3 -m venv venv && source venv/bin/activate${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✓${NC} Virtual environment active: $VIRTUAL_ENV"
fi

# Check required environment variables
if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    echo -e "${RED}✗${NC} TELEGRAM_BOT_TOKEN not set"
    echo -e "${RED}   Set it in your .env file or export it${NC}"
    exit 1
else
    echo -e "${GREEN}✓${NC} TELEGRAM_BOT_TOKEN is set"
fi

if [ -z "$TELEGRAM_CHAT_ID" ]; then
    echo -e "${RED}✗${NC} TELEGRAM_CHAT_ID not set"
    echo -e "${RED}   Set it in your .env file or export it${NC}"
    exit 1
else
    echo -e "${GREEN}✓${NC} TELEGRAM_CHAT_ID is set"
fi

# Check if positions are configured
echo ""
echo -e "${BLUE}=== Checking Configuration ===${NC}"

if grep -q "^  [A-Z]" config/premarket_config.yaml 2>/dev/null; then
    positions=$(grep "^  [A-Z]" config/premarket_config.yaml | cut -d':' -f1 | tr -d ' ' | tr '\n' ', ' | sed 's/,$//')
    echo -e "${GREEN}✓${NC} Positions configured: ${positions}"
else
    echo -e "${YELLOW}⚠️  No positions configured in premarket_config.yaml${NC}"
    echo -e "${YELLOW}   Add your active positions to receive gap alerts${NC}"
    echo ""
    echo -e "${YELLOW}   Edit: config/premarket_config.yaml${NC}"
fi

echo ""

# ============================================================================
# WORKFLOW EXECUTION
# Add new steps below following the same pattern
# See WORKFLOW_MAINTENANCE.md for details
# ============================================================================

echo -e "${BLUE}=== Running Pre-Market Gap Monitor ===${NC}"
python scripts/send_premarket_alerts.py

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Pre-market alerts sent successfully"
else
    echo -e "${RED}✗${NC} Failed to send pre-market alerts"
    exit 1
fi

# ============================================================================
# END OF WORKFLOW
# All workflow steps completed above
# ============================================================================

echo ""
echo -e "${GREEN}============================================================================${NC}"
echo -e "${GREEN}                    ✅ WORKFLOW COMPLETED SUCCESSFULLY${NC}"
echo -e "${GREEN}============================================================================${NC}"
echo ""
echo -e "Summary:"
echo -e "  • Pre-market gaps detected and analyzed"
echo -e "  • Market futures sentiment assessed"
echo -e "  • Telegram alerts sent"
echo ""
echo -e "Next scheduled runs:"
echo -e "  • 7:00 AM ET (early warning)"
echo -e "  • 8:00 AM ET (mid-check)"
echo -e "  • 9:00 AM ET (final warning before open)"
echo ""
echo -e "${BLUE}Market opens at 9:30 AM ET${NC}"
echo ""

