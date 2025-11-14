#!/usr/bin/env python3
"""
Chart Utilities - Centralized chart organization and path management

Provides consistent chart directory structure:
- charts/breakouts/       - Simple breakout charts
- charts/indicators/      - Charts with technical indicators
- charts/abc_patterns/    - ABC pattern charts
- charts/strategies/      - Strategy-specific charts
"""

import os
from pathlib import Path
from typing import Optional


class ChartOrganizer:
    """Manage chart directory structure and file naming"""
    
    # Chart type directories
    BREAKOUTS = "breakouts"
    INDICATORS = "indicators"
    ABC_PATTERNS = "abc_patterns"
    STRATEGIES = "strategies"
    
    def __init__(self, base_dir: str = "charts"):
        """
        Initialize chart organizer
        
        Args:
            base_dir: Base directory for all charts
        """
        self.base_dir = Path(base_dir)
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Create chart subdirectories if they don't exist"""
        subdirs = [
            self.BREAKOUTS,
            self.INDICATORS,
            self.ABC_PATTERNS,
            self.STRATEGIES
        ]
        
        for subdir in subdirs:
            (self.base_dir / subdir).mkdir(parents=True, exist_ok=True)
    
    def get_chart_path(self, 
                      chart_type: str, 
                      symbol: str, 
                      suffix: str = "",
                      extension: str = "png") -> Path:
        """
        Get organized chart path
        
        Args:
            chart_type: Type of chart (breakouts, indicators, abc_patterns, strategies)
            symbol: Symbol name (e.g., TQQQ, AAPL)
            suffix: Optional suffix for filename (e.g., _enhanced, _20250114)
            extension: File extension (default: png)
            
        Returns:
            Path object for the chart file
        """
        # Validate chart type
        valid_types = [self.BREAKOUTS, self.INDICATORS, self.ABC_PATTERNS, self.STRATEGIES]
        if chart_type not in valid_types:
            raise ValueError(f"Invalid chart_type. Must be one of: {valid_types}")
        
        # Build filename
        filename = f"{symbol}{suffix}.{extension}"
        
        # Return full path
        return self.base_dir / chart_type / filename
    
    def get_breakout_path(self, symbol: str, timestamp: bool = False) -> Path:
        """Get path for simple breakout chart"""
        suffix = f"_{self._get_timestamp()}" if timestamp else ""
        return self.get_chart_path(self.BREAKOUTS, symbol, suffix)
    
    def get_indicators_path(self, symbol: str, timestamp: bool = False) -> Path:
        """Get path for chart with technical indicators"""
        suffix = f"_indicators"
        if timestamp:
            suffix += f"_{self._get_timestamp()}"
        return self.get_chart_path(self.INDICATORS, symbol, suffix)
    
    def get_abc_pattern_path(self, 
                            symbol: str, 
                            pattern_type: str,
                            timestamp: bool = False) -> Path:
        """
        Get path for ABC pattern chart
        
        Args:
            symbol: Symbol name
            pattern_type: BULLISH or BEARISH
            timestamp: Whether to include timestamp (default: False for consistency)
        """
        suffix = f"_ABC_{pattern_type}"
        if timestamp:
            suffix += f"_{self._get_timestamp()}"
        return self.get_chart_path(self.ABC_PATTERNS, symbol, suffix)
    
    def get_strategy_path(self, 
                         symbol: str, 
                         strategy_name: str,
                         timestamp: bool = False) -> Path:
        """
        Get path for strategy-specific chart
        
        Args:
            symbol: Symbol name
            strategy_name: Strategy name (e.g., rsi_macd, trend_following)
            timestamp: Whether to include timestamp
        """
        suffix = f"_{strategy_name}"
        if timestamp:
            suffix += f"_{self._get_timestamp()}"
        return self.get_chart_path(self.STRATEGIES, symbol, suffix)
    
    @staticmethod
    def _get_timestamp() -> str:
        """Get timestamp string for filenames"""
        from datetime import datetime
        return datetime.now().strftime('%Y%m%d_%H%M%S')
    
    def list_charts(self, chart_type: Optional[str] = None) -> list:
        """
        List all charts in a directory
        
        Args:
            chart_type: Specific chart type to list (None = all)
            
        Returns:
            List of chart file paths
        """
        if chart_type:
            search_dir = self.base_dir / chart_type
            return sorted(search_dir.glob('*.png'))
        else:
            # Return all charts from all subdirectories
            charts = []
            for subdir in [self.BREAKOUTS, self.INDICATORS, self.ABC_PATTERNS, self.STRATEGIES]:
                charts.extend((self.base_dir / subdir).glob('*.png'))
            return sorted(charts)
    
    def clean_old_charts(self, chart_type: str, keep_latest: int = 5):
        """
        Clean old charts, keeping only the latest N files per symbol
        
        Args:
            chart_type: Type of charts to clean
            keep_latest: Number of latest charts to keep per symbol
        """
        charts_dir = self.base_dir / chart_type
        if not charts_dir.exists():
            return
        
        # Group charts by symbol
        from collections import defaultdict
        charts_by_symbol = defaultdict(list)
        
        for chart_file in charts_dir.glob('*.png'):
            # Extract symbol from filename (before first underscore or dot)
            symbol = chart_file.stem.split('_')[0]
            charts_by_symbol[symbol].append(chart_file)
        
        # Clean old charts for each symbol
        for symbol, chart_files in charts_by_symbol.items():
            # Sort by modification time (newest first)
            chart_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            # Remove old files
            for old_file in chart_files[keep_latest:]:
                old_file.unlink()
                print(f"  🗑️  Removed old chart: {old_file.name}")
    
    def get_summary(self) -> dict:
        """Get summary of chart organization"""
        summary = {
            'base_dir': str(self.base_dir),
            'subdirectories': {},
            'total_charts': 0
        }
        
        for subdir in [self.BREAKOUTS, self.INDICATORS, self.ABC_PATTERNS, self.STRATEGIES]:
            subdir_path = self.base_dir / subdir
            chart_count = len(list(subdir_path.glob('*.png')))
            summary['subdirectories'][subdir] = {
                'path': str(subdir_path),
                'chart_count': chart_count
            }
            summary['total_charts'] += chart_count
        
        return summary
    
    def print_summary(self):
        """Print chart organization summary"""
        summary = self.get_summary()
        
        print("\n" + "="*80)
        print("📊 CHART ORGANIZATION SUMMARY")
        print("="*80)
        print(f"\n📁 Base Directory: {summary['base_dir']}")
        print(f"\n📈 Total Charts: {summary['total_charts']}")
        
        print("\n📂 Subdirectories:")
        for subdir_name, info in summary['subdirectories'].items():
            print(f"   • {subdir_name:20s} - {info['chart_count']:3d} charts")
        
        print("="*80)


# Global instance for easy access
_chart_organizer = None

def get_chart_organizer(base_dir: str = "charts") -> ChartOrganizer:
    """Get global chart organizer instance"""
    global _chart_organizer
    if _chart_organizer is None:
        _chart_organizer = ChartOrganizer(base_dir)
    return _chart_organizer


# Convenience functions
def get_breakout_chart_path(symbol: str, timestamp: bool = False) -> str:
    """Get path for breakout chart"""
    return str(get_chart_organizer().get_breakout_path(symbol, timestamp))

def get_indicators_chart_path(symbol: str, timestamp: bool = False) -> str:
    """Get path for indicators chart"""
    return str(get_chart_organizer().get_indicators_path(symbol, timestamp))

def get_abc_chart_path(symbol: str, pattern_type: str, timestamp: bool = False) -> str:
    """Get path for ABC pattern chart"""
    return str(get_chart_organizer().get_abc_pattern_path(symbol, pattern_type, timestamp))

def get_strategy_chart_path(symbol: str, strategy_name: str, timestamp: bool = False) -> str:
    """Get path for strategy chart"""
    return str(get_chart_organizer().get_strategy_path(symbol, strategy_name, timestamp))


if __name__ == "__main__":
    # Demo usage
    organizer = ChartOrganizer()
    
    print("\n📐 Chart Organizer Demo\n")
    print("Example paths:")
    print(f"  Breakout:    {organizer.get_breakout_path('TQQQ')}")
    print(f"  Indicators:  {organizer.get_indicators_path('AAPL')}")
    print(f"  ABC:         {organizer.get_abc_pattern_path('UBER', 'BULLISH', timestamp=False)}")
    print(f"  Strategy:    {organizer.get_strategy_path('SP500', 'rsi_macd')}")
    
    organizer.print_summary()

