#!/bin/bash
# Weekly Market Automation - S&P 500 Scan & Correlations Update
# Run weekly tasks (typically Sunday evenings)
# Usage: ./scripts/run_weekly_workflow.sh

set -e  # Exit on error

# Get project directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Weekly Market Automation Workflow${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Activate virtual environment
if [ -d "venv" ]; then
    echo -e "${GREEN}✓${NC} Activating virtual environment..."
    source venv/bin/activate
else
    echo -e "${RED}✗${NC} Virtual environment not found!"
    exit 1
fi

# ============================================================================
# WEEKLY WORKFLOW STEPS
# When adding new weekly features, add them below
# See WORKFLOW_MAINTENANCE.md for details
# ============================================================================

echo ""
echo -e "${BLUE}=== Step 1: Update S&P 500 List ===${NC}"
python scripts/fetch_sp500_list.py
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} S&P 500 list updated"
else
    echo -e "${RED}✗${NC} Failed to update S&P 500 list"
    exit 1
fi

echo ""
echo -e "${BLUE}=== Step 2: Scan S&P 500 for Opportunities ===${NC}"
python scripts/scan_sp500_news.py
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} S&P 500 scan complete"
else
    echo -e "${RED}✗${NC} Failed to scan S&P 500"
    exit 1
fi

echo ""
echo -e "${BLUE}=== Step 3: Update News Correlations ===${NC}"
python scripts/update_news_correlations.py
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} News correlations updated"
else
    echo -e "${RED}✗${NC} Failed to update correlations"
    exit 1
fi

# ============================================================================
# END OF WEEKLY WORKFLOW
# Add new steps ABOVE this section
# ============================================================================

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  ✓ Weekly Workflow Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "📊 Summary:"
echo "  - S&P 500 list updated"
echo "  - Opportunities scanned and sent"
echo "  - Historical correlations updated"
echo ""
