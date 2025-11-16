#!/bin/bash
# Setup FinBERT with GPU Support (Linux with NVIDIA GPU)
# This script installs PyTorch with CUDA support for faster sentiment analysis

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  FinBERT GPU Setup (Linux)${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if venv exists
if [ ! -d "venv" ]; then
    echo -e "${RED}✗${NC} Virtual environment not found!"
    echo "   Run this from project root after running ./scripts/setup_local.sh"
    exit 1
fi

# Activate virtual environment
echo -e "${BLUE}[1/5] Activating virtual environment...${NC}"
source venv/bin/activate

# Check current CUDA availability
echo ""
echo -e "${BLUE}[2/5] Checking for NVIDIA GPU...${NC}"
python -c "import torch; print(f'Current PyTorch: {torch.__version__}'); print(f'CUDA available: {torch.cuda.is_available()}'); print(f'GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"None\"}')" 2>/dev/null || echo "PyTorch not installed yet"

echo ""
echo -e "${BLUE}[3/5] Which CUDA version does your GPU support?${NC}"
echo ""
echo "   1. CUDA 11.8 (Recommended for most GPUs)"
echo "   2. CUDA 12.1 (For newer GPUs - RTX 40 series)"
echo "   3. Skip GPU setup (use CPU only)"
echo ""
read -p "Enter choice (1-3): " CUDA_CHOICE

if [ "$CUDA_CHOICE" = "3" ]; then
    echo ""
    echo "Skipping GPU setup - will use CPU"
    TORCH_INDEX=""
else
    if [ "$CUDA_CHOICE" = "2" ]; then
        TORCH_INDEX="https://download.pytorch.org/whl/cu121"
        CUDA_VER="12.1"
    else
        TORCH_INDEX="https://download.pytorch.org/whl/cu118"
        CUDA_VER="11.8"
    fi
    
    echo ""
    echo -e "${BLUE}[4/5] Installing PyTorch with CUDA $CUDA_VER support...${NC}"
    echo "   This may take 2-5 minutes (downloading ~2GB)..."
    echo ""
    
    # Uninstall existing torch
    pip uninstall -y torch torchvision 2>/dev/null
    
    # Install with CUDA
    pip install torch torchvision --index-url $TORCH_INDEX
    if [ $? -ne 0 ]; then
        echo -e "${RED}✗${NC} Failed to install PyTorch with GPU support"
        echo "   Falling back to CPU version..."
        pip install "torch>=2.1.0"
    fi
fi

if [ "$CUDA_CHOICE" = "3" ] || [ -z "$TORCH_INDEX" ]; then
    echo ""
    echo -e "${BLUE}[4/5] Installing PyTorch (CPU version)...${NC}"
    pip install "torch>=2.1.0"
fi

echo ""
echo -e "${BLUE}[5/5] Installing Transformers library...${NC}"
pip install "transformers>=4.35.0"

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Testing Installation${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Test installation
python -c "import torch; cuda = torch.cuda.is_available(); print(f'CUDA Available: {cuda}'); print(f'Device: {torch.cuda.get_device_name(0) if cuda else \"CPU\"}'); print(f'PyTorch: {torch.__version__}')"

if [ $? -ne 0 ]; then
    echo -e "${RED}✗${NC} Installation test failed"
    exit 1
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Setup Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Next steps:"
echo "  1. Test FinBERT: ${YELLOW}python src/finbert_sentiment.py${NC}"
echo "  2. Run news scanner: ${YELLOW}python scripts/send_news_opportunities.py${NC}"
echo ""
echo "Performance:"
echo "  - With GPU: ~10-50x faster than CPU"
echo "  - Model loads in 2-3 seconds"
echo "  - Each sentiment analysis: ~0.01-0.05 seconds"
echo ""

