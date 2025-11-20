"""
Sector Performance Analysis - TradingView Heatmap Data
Generates sector-wise performance data for intelligent symbol selection
NO HTML visualization - pure data for strategy use
"""
import yfinance as yf
import pandas as pd
from typing import Dict, List, Tuple
from pathlib import Path
import json
from datetime import datetime

class SectorHeatmap:
    """
    TradingView-style sector heatmap analyzer
    Shows sector performance, rotation, and market conditions
    """
    
    # S&P 500 Sector ETFs (Standard & Poor's GICS Sectors)
    SECTOR_ETFS = {
        'Technology': 'XLK',
        'Healthcare': 'XLV',
        'Financials': 'XLF',
        'Consumer Discretionary': 'XLY',
        'Industrials': 'XLI',
        'Communication Services': 'XLC',
        'Consumer Staples': 'XLP',
        'Energy': 'XLE',
        'Utilities': 'XLU',
        'Real Estate': 'XLRE',
        'Materials': 'XLB'
    }
    
    # Market indices for context
    MARKET_INDICES = {
        'S&P 500': 'SPY',
        'Nasdaq 100': 'QQQ',
        'Dow Jones': 'DIA',
        'Russell 2000': 'IWM'
    }
    
    def __init__(self):
        self.sector_data = {}
        self.market_data = {}
        
    def fetch_sector_performance(self, period: str = '1d') -> Dict:
        """
        Fetch performance data for all sectors
        
        Args:
            period: '1d', '5d', '1mo', '3mo', 'ytd', '1y'
            
        Returns:
            Dict with sector performance data
        """
        print(f"\n📊 Fetching sector performance ({period})...")
        
        results = {}
        
        # Fetch sector ETFs
        for sector, etf in self.SECTOR_ETFS.items():
            try:
                ticker = yf.Ticker(etf)
                hist = ticker.history(period=period if period != 'ytd' else '1y')
                
                if len(hist) >= 2:
                    first_close = hist['Close'].iloc[0]
                    last_close = hist['Close'].iloc[-1]
                    change_pct = ((last_close - first_close) / first_close) * 100
                    
                    results[sector] = {
                        'etf': etf,
                        'change_pct': round(change_pct, 2),
                        'last_price': round(last_close, 2),
                        'volume': int(hist['Volume'].iloc[-1])
                    }
                    
            except Exception as e:
                print(f"  ⚠️  Error fetching {sector} ({etf}): {e}")
                continue
        
        # Fetch market indices for context
        for index, symbol in self.MARKET_INDICES.items():
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period=period if period != 'ytd' else '1y')
                
                if len(hist) >= 2:
                    first_close = hist['Close'].iloc[0]
                    last_close = hist['Close'].iloc[-1]
                    change_pct = ((last_close - first_close) / first_close) * 100
                    
                    results[f"_INDEX_{index}"] = {
                        'etf': symbol,
                        'change_pct': round(change_pct, 2),
                        'last_price': round(last_close, 2),
                        'volume': int(hist['Volume'].iloc[-1])
                    }
                    
            except Exception as e:
                print(f"  ⚠️  Error fetching {index} ({symbol}): {e}")
                continue
        
        self.sector_data = results
        print(f"  ✅ Fetched {len(results)} sectors/indices\n")
        return results
    
    def detect_sector_rotation(self) -> Dict:
        """
        Detect sector rotation patterns
        Returns hot/cold sectors and rotation signals
        """
        if not self.sector_data:
            return {}
        
        # Separate sectors and indices
        sectors = {k: v for k, v in self.sector_data.items() if not k.startswith('_INDEX_')}
        indices = {k.replace('_INDEX_', ''): v for k, v in self.sector_data.items() if k.startswith('_INDEX_')}
        
        # Sort sectors by performance
        sorted_sectors = sorted(sectors.items(), key=lambda x: x[1]['change_pct'], reverse=True)
        
        # Categorize sectors
        hot_sectors = [s for s in sorted_sectors if s[1]['change_pct'] > 1.0][:3]
        cold_sectors = [s for s in sorted_sectors if s[1]['change_pct'] < -1.0][-3:]
        neutral_sectors = [s for s in sorted_sectors if -1.0 <= s[1]['change_pct'] <= 1.0]
        
        # Detect rotation pattern
        market_avg = sum(v['change_pct'] for v in sectors.values()) / len(sectors)
        
        rotation_signal = "NEUTRAL"
        if market_avg > 1.0:
            rotation_signal = "RISK_ON"  # Cyclical sectors outperforming
        elif market_avg < -1.0:
            rotation_signal = "RISK_OFF"  # Defensive sectors outperforming
        
        return {
            'hot_sectors': hot_sectors,
            'cold_sectors': cold_sectors,
            'neutral_sectors': neutral_sectors,
            'market_avg': round(market_avg, 2),
            'rotation_signal': rotation_signal,
            'indices': indices
        }
    
    def generate_heatmap_html(self, output_dir: Path) -> str:
        """
        Generate TradingView-style HTML heatmap
        """
        if not self.sector_data:
            return ""
        
        rotation = self.detect_sector_rotation()
        
        # Generate HTML
        html = """
<!DOCTYPE html>
<html>
<head>
    <title>Market Sector Heatmap - TradingView Style</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            background: #131722;
            color: #d1d4dc;
            margin: 20px;
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        .timestamp {
            color: #787b86;
            font-size: 14px;
        }
        .heatmap {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 10px;
            margin: 20px 0;
        }
        .sector-box {
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            transition: transform 0.2s;
            cursor: pointer;
        }
        .sector-box:hover {
            transform: scale(1.05);
        }
        .sector-name {
            font-size: 16px;
            font-weight: bold;
            margin-bottom: 10px;
        }
        .sector-change {
            font-size: 24px;
            font-weight: bold;
        }
        .sector-etf {
            font-size: 12px;
            color: #787b86;
            margin-top: 5px;
        }
        .positive {
            background: linear-gradient(135deg, #16a34a 0%, #15803d 100%);
        }
        .negative {
            background: linear-gradient(135deg, #dc2626 0%, #991b1b 100%);
        }
        .neutral {
            background: linear-gradient(135deg, #6b7280 0%, #4b5563 100%);
        }
        .indices {
            display: flex;
            justify-content: space-around;
            margin: 30px 0;
            padding: 20px;
            background: #1e222d;
            border-radius: 8px;
        }
        .index-box {
            text-align: center;
        }
        .index-name {
            font-size: 14px;
            color: #787b86;
        }
        .index-value {
            font-size: 20px;
            font-weight: bold;
            margin-top: 5px;
        }
        .summary {
            margin: 30px 0;
            padding: 20px;
            background: #1e222d;
            border-radius: 8px;
        }
        .summary h3 {
            margin-top: 0;
            color: #2962ff;
        }
        .rotation-badge {
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-weight: bold;
            margin-left: 10px;
        }
        .risk-on {
            background: #16a34a;
            color: white;
        }
        .risk-off {
            background: #dc2626;
            color: white;
        }
        .neutral-badge {
            background: #6b7280;
            color: white;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 Market Sector Heatmap</h1>
        <p class="timestamp">Generated: {timestamp}</p>
    </div>
    
    <div class="summary">
        <h3>Market Overview 
            <span class="rotation-badge {rotation_class}">{rotation_signal}</span>
        </h3>
        <p><strong>Market Average:</strong> {market_avg}%</p>
        <p><strong>Hot Sectors:</strong> {hot_sectors}</p>
        <p><strong>Cold Sectors:</strong> {cold_sectors}</p>
    </div>
    
    <h2>📍 Major Indices</h2>
    <div class="indices">
        {indices_html}
    </div>
    
    <h2>🎨 Sector Performance</h2>
    <div class="heatmap">
        {sectors_html}
    </div>
    
    <div class="summary">
        <p style="text-align: center; color: #787b86; font-size: 12px;">
            Inspired by <a href="https://www.tradingview.com/heatmap/" target="_blank" style="color: #2962ff;">TradingView Heatmap</a>
        </p>
    </div>
</body>
</html>
"""
        
        # Generate indices HTML
        indices_html = ""
        for name, data in rotation['indices'].items():
            color_class = 'positive' if data['change_pct'] > 0 else 'negative'
            sign = '+' if data['change_pct'] > 0 else ''
            indices_html += f"""
        <div class="index-box">
            <div class="index-name">{name}</div>
            <div class="index-value" style="color: {'#16a34a' if data['change_pct'] > 0 else '#dc2626'}">
                {sign}{data['change_pct']}%
            </div>
            <div class="index-name">{data['etf']}</div>
        </div>
"""
        
        # Generate sectors HTML
        sectors = {k: v for k, v in self.sector_data.items() if not k.startswith('_INDEX_')}
        sectors_html = ""
        
        for sector, data in sorted(sectors.items(), key=lambda x: x[1]['change_pct'], reverse=True):
            change = data['change_pct']
            
            if change > 0.5:
                color_class = 'positive'
            elif change < -0.5:
                color_class = 'negative'
            else:
                color_class = 'neutral'
            
            sign = '+' if change > 0 else ''
            
            sectors_html += f"""
        <div class="sector-box {color_class}">
            <div class="sector-name">{sector}</div>
            <div class="sector-change">{sign}{change}%</div>
            <div class="sector-etf">{data['etf']}</div>
        </div>
"""
        
        # Format rotation signal
        rotation_class = {
            'RISK_ON': 'risk-on',
            'RISK_OFF': 'risk-off',
            'NEUTRAL': 'neutral-badge'
        }.get(rotation['rotation_signal'], 'neutral-badge')
        
        # Format hot/cold sectors
        hot_sectors_str = ', '.join([s[0] for s in rotation['hot_sectors']]) or 'None'
        cold_sectors_str = ', '.join([s[0] for s in rotation['cold_sectors']]) or 'None'
        
        # Fill template
        html = html.format(
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            rotation_signal=rotation['rotation_signal'].replace('_', ' '),
            rotation_class=rotation_class,
            market_avg=rotation['market_avg'],
            hot_sectors=hot_sectors_str,
            cold_sectors=cold_sectors_str,
            indices_html=indices_html,
            sectors_html=sectors_html
        )
        
        # Save HTML
        output_path = output_dir / 'sector_heatmap.html'
        output_path.write_text(html)
        
        print(f"  ✅ Heatmap saved: {output_path}")
        return str(output_path)
    
    def generate_json_report(self, output_dir: Path) -> str:
        """Generate JSON report for programmatic use"""
        if not self.sector_data:
            return ""
        
        rotation = self.detect_sector_rotation()
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'market_overview': {
                'market_avg': rotation['market_avg'],
                'rotation_signal': rotation['rotation_signal']
            },
            'indices': rotation['indices'],
            'sectors': {k: v for k, v in self.sector_data.items() if not k.startswith('_INDEX_')},
            'hot_sectors': [{'sector': s[0], 'change': s[1]['change_pct']} for s in rotation['hot_sectors']],
            'cold_sectors': [{'sector': s[0], 'change': s[1]['change_pct']} for s in rotation['cold_sectors']]
        }
        
        output_path = output_dir / 'sector_analysis.json'
        output_path.write_text(json.dumps(report, indent=2))
        
        print(f"  ✅ JSON report saved: {output_path}")
        return str(output_path)


def main():
    """Demo: Generate sector heatmap"""
    from pathlib import Path
    
    print("=" * 80)
    print("SECTOR HEATMAP GENERATOR (TradingView Style)")
    print("=" * 80)
    
    heatmap = SectorHeatmap()
    
    # Fetch data
    heatmap.fetch_sector_performance(period='1d')
    
    # Analyze rotation
    rotation = heatmap.detect_sector_rotation()
    
    print(f"\n📊 MARKET ANALYSIS:")
    print(f"   Market Average: {rotation['market_avg']}%")
    print(f"   Rotation Signal: {rotation['rotation_signal']}")
    print(f"\n🔥 HOT SECTORS:")
    for sector, data in rotation['hot_sectors']:
        print(f"   • {sector}: +{data['change_pct']}% ({data['etf']})")
    print(f"\n🥶 COLD SECTORS:")
    for sector, data in rotation['cold_sectors']:
        print(f"   • {sector}: {data['change_pct']}% ({data['etf']})")
    
    # Generate outputs
    signals_dir = Path(__file__).parent.parent / 'signals'
    signals_dir.mkdir(exist_ok=True)
    
    print(f"\n📁 GENERATING OUTPUTS:")
    heatmap.generate_heatmap_html(signals_dir)
    heatmap.generate_json_report(signals_dir)
    
    print(f"\n✅ Done! Open signals/sector_heatmap.html in your browser")


if __name__ == '__main__':
    main()

