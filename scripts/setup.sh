#!/bin/bash
# Setup script for daily market automation

set -e

echo "🚀 Setting up Daily Market Automation..."

# Create virtual environment
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements-fetch.txt

# Create data directory if not exists
mkdir -p data

echo "✅ Setup complete!"
echo ""
echo "To activate the environment, run:"
echo "  source .venv/bin/activate"
echo ""
echo "To run the fetch script:"
echo "  python src/fetch_daily_prices.py"
