#!/bin/bash
# One-time setup script for local machine
# Usage: ./scripts/setup_local.sh

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Get project directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Daily Market Automation - Local Setup${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Step 1: Check Python version
echo -e "${BLUE}[1/7] Checking Python version...${NC}"
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
REQUIRED_VERSION="3.12"
if [[ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" == "$REQUIRED_VERSION" ]]; then
    echo -e "${GREEN}✓${NC} Python $PYTHON_VERSION (>= 3.12 required)"
else
    echo -e "${RED}✗${NC} Python $PYTHON_VERSION found, but 3.12+ required"
    echo "  Install Python 3.12+: https://www.python.org/downloads/"
    exit 1
fi

# Step 2: Create virtual environment
echo ""
echo -e "${BLUE}[2/7] Creating virtual environment...${NC}"
if [ -d "venv" ]; then
    echo -e "${YELLOW}⚠${NC}  Virtual environment already exists"
    read -p "  Recreate? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf venv
        python3 -m venv venv
        echo -e "${GREEN}✓${NC} Virtual environment recreated"
    else
        echo -e "${BLUE}→${NC} Using existing virtual environment"
    fi
else
    python3 -m venv venv
    echo -e "${GREEN}✓${NC} Virtual environment created"
fi

# Step 3: Activate and install dependencies
echo ""
echo -e "${BLUE}[3/7] Installing dependencies...${NC}"
source venv/bin/activate
pip install --upgrade pip > /dev/null 2>&1
echo "  → Installing base requirements..."
pip install -r requirements-base.txt > /dev/null 2>&1
echo "  → Installing fetch requirements..."
pip install -r requirements-fetch.txt > /dev/null 2>&1
echo "  → Installing pandas-ta..."
pip install --index-url https://pypi.org/simple/ pandas-ta > /dev/null 2>&1
echo -e "${GREEN}✓${NC} All dependencies installed"

# Step 4: Create directories
echo ""
echo -e "${BLUE}[4/7] Creating directory structure...${NC}"
mkdir -p logs
mkdir -p data/market_data
mkdir -p data/metadata
mkdir -p data/cache
mkdir -p signals
mkdir -p charts/breakouts
mkdir -p charts/indicators
mkdir -p charts/abc_patterns
mkdir -p charts/strategies
echo -e "${GREEN}✓${NC} Directory structure created"

# Step 5: Check .env file
echo ""
echo -e "${BLUE}[5/7] Checking environment configuration...${NC}"
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠${NC}  .env file not found"
    echo "  Creating template .env file..."
    cat > .env << EOF
# Telegram Configuration (Required)
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here

# Finnhub API (Optional - for insider trading & advanced features)
FINNHUB_API_KEY=your_finnhub_key_here
EOF
    echo -e "${GREEN}✓${NC} Template .env created"
    echo -e "${RED}  ⚠  IMPORTANT: Edit .env with your actual credentials!${NC}"
else
    echo -e "${GREEN}✓${NC} .env file exists"
fi

# Step 6: Make scripts executable
echo ""
echo -e "${BLUE}[6/7] Making scripts executable...${NC}"
chmod +x scripts/*.sh
chmod +x scripts/*.py
chmod +x src/*.py
echo -e "${GREEN}✓${NC} Scripts are now executable"

# Step 7: Test installation
echo ""
echo -e "${BLUE}[7/7] Testing installation...${NC}"
echo "  → Testing module imports..."
python -c "import pandas; import yfinance; import yaml; print('✓ All modules OK')"
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Installation test passed"
else
    echo -e "${RED}✗${NC} Installation test failed"
    exit 1
fi

# Done!
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  ✓ Setup Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${BLUE}Next Steps:${NC}"
echo ""
echo "1. Configure environment variables:"
echo "   ${YELLOW}nano .env${NC}"
echo "   (Add your TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID)"
echo ""
echo "2. Configure symbols to track:"
echo "   ${YELLOW}nano config/symbols.yaml${NC}"
echo ""
echo "3. Test the system:"
echo "   ${YELLOW}./scripts/run_daily_workflow.sh${NC}"
echo ""
echo "4. Set up automated scheduling (optional):"
echo "   - See LOCAL_SETUP_GUIDE.md for cron/launchd setup"
echo ""
echo -e "${BLUE}Quick Commands:${NC}"
echo "  ${YELLOW}source venv/bin/activate${NC}           # Activate virtual environment"
echo "  ${YELLOW}./scripts/run_daily_workflow.sh${NC}    # Run complete daily workflow"
echo "  ${YELLOW}./scripts/run_weekly_workflow.sh${NC}   # Run weekly S&P 500 scan"
echo "  ${YELLOW}python scripts/analyze_symbol.py AAPL${NC}  # Analyze specific symbol"
echo ""
echo "📖 For detailed documentation, see:"
echo "   ${BLUE}LOCAL_SETUP_GUIDE.md${NC}"
echo ""

