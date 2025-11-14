#!/usr/bin/env python3
"""
Demo: ABC Pattern Chart Generation

Quick demo to generate professional ABC pattern charts
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from visualize_abc_patterns import generate_abc_charts


def main():
    """Generate ABC pattern charts for all symbols"""
    
    print("\n" + "="*80)
    print("🎨 ABC PATTERN CHART DEMO")
    print("="*80)
    print("\nThis will generate professional charts showing:")
    print("  ✓ ABC pattern structure (0-A-B-C)")
    print("  ✓ Entry zones (4 Fibonacci levels)")
    print("  ✓ Target zones (3 take profit levels)")
    print("  ✓ Stop loss levels")
    print("  ✓ Activation line and A2 tracking")
    print("  ✓ Risk/reward visualization")
    print("  ✓ Pattern info box")
    
    # Generate charts for all symbols
    generate_abc_charts(
        data_dir='data',
        output_dir='charts',
        symbols=None  # None = all symbols
    )
    
    print("\n✅ Done! Check the 'charts/' directory for your ABC pattern visualizations.")
    print("\n💡 To generate charts for specific symbols:")
    print("   python examples/demo_abc_charts.py --symbols AAPL TSLA")
    print("\n💡 Or use the CLI directly:")
    print("   python src/visualize_abc_patterns.py --symbols TQQQ")


if __name__ == "__main__":
    # Check if CLI args provided
    import sys
    if len(sys.argv) > 1:
        # Pass to main CLI
        from visualize_abc_patterns import main as cli_main
        cli_main()
    else:
        # Run demo
        main()

