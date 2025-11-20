"""
Intelligent Symbol Selection System
Pluggable strategies - NO HARDCODED SYMBOLS!

Architecture:
- SymbolSelector: Main orchestrator
- SelectionStrategy: Base class for strategies
- Multiple concrete strategies (News, Activity, Quality, etc.)
- Configuration-driven selection
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from pathlib import Path
import pandas as pd
import os
from datetime import datetime, timedelta


class SelectionStrategy(ABC):
    """Base class for symbol selection strategies"""
    
    @abstractmethod
    def select(self, symbols: List[Dict], max_symbols: int, config: Dict) -> List[Dict]:
        """
        Select symbols based on strategy criteria
        
        Args:
            symbols: List of symbol dicts with metadata
            max_symbols: Maximum number to select
            config: Strategy-specific configuration
            
        Returns:
            List of selected symbol dicts with scores
        """
        pass
    
    @abstractmethod
    def name(self) -> str:
        """Strategy name for logging"""
        pass


class NewsBasedStrategy(SelectionStrategy):
    """
    Select symbols with BUY-THE-DIP opportunities
    
    CONTRARIAN/VALUE APPROACH:
    1. Find symbols with NEGATIVE news (price drops, bad headlines)
    2. BUT good fundamentals (solid company)
    3. AND good technicals (oversold, support)
    4. = BUYING OPPORTUNITY at the bottom!
    
    Uses existing NewsMonitor which already implements this logic.
    """
    
    def __init__(self, finnhub_client=None, data_dir: Path = None):
        self.finnhub = finnhub_client
        self.data_dir = data_dir or Path('data/market_data')
        self.cache_file = Path('data/cache/trending_news.json')
        
        # Use existing NewsMonitor (already filters for buy-the-dip opportunities!)
        from src.news_monitor import NewsMonitor
        self.news_monitor = NewsMonitor(enable_correlation=True, use_finbert=True)
    
    def name(self) -> str:
        return "Buy-The-Dip (News)"
    
    def select(self, symbols: List[Dict], max_symbols: int, config: Dict) -> List[Dict]:
        """
        BUY-THE-DIP selection:
        1. Get symbols with price drops (3-10%)
        2. Filter for NEGATIVE news (falls, misses, disappoints)
        3. Check fundamentals (good company despite bad news)
        4. Check technicals (oversold = bottom)
        5. = BUYING OPPORTUNITY!
        
        This uses the battle-tested NewsMonitor logic.
        """
        print("       → Scanning for buy-the-dip opportunities...")
        
        # Step 1: Get symbols with price drops (potential opportunities)
        dropped_symbols = self._get_dropped_symbols(symbols, config)
        print(f"       → Found {len(dropped_symbols)} symbols with price drops (3-10%)")
        
        if not dropped_symbols:
            print(f"       → No symbols with price drops, using active symbols...")
            dropped_symbols = [s['symbol'] for s in symbols[:500]]  # Sample
        
        # Step 2: Use NewsMonitor to scan for buy-the-dip opportunities
        # It checks: negative news + good fundamentals + technical oversold
        try:
            opportunities = self.news_monitor.scan_for_opportunities(dropped_symbols)
            print(f"       → Found {len(opportunities)} buy-the-dip opportunities")
            
            # Convert to our format
            scored_symbols = []
            opp_symbols = {opp['symbol']: opp for opp in opportunities}
            
            for sym in symbols:
                symbol_str = sym['symbol']
                if symbol_str in opp_symbols:
                    opp = opp_symbols[symbol_str]
                    sym['score'] = opp.get('score', 50)
                    sym['reason'] = "buy-the-dip: " + opp.get('reason', 'price drop + news')
                    scored_symbols.append(sym)
            
            # Sort by score
            scored_symbols.sort(key=lambda x: x.get('score', 0), reverse=True)
            return scored_symbols[:max_symbols]
            
        except Exception as e:
            print(f"       ⚠️  NewsMonitor failed: {e}")
            # Fallback: use price-dropped symbols
            result = []
            for sym in symbols:
                if sym['symbol'] in dropped_symbols[:max_symbols]:
                    sym['score'] = 50
                    sym['reason'] = "price drop (fallback)"
                    result.append(sym)
            return result
    
    def _get_dropped_symbols(self, symbols: List[Dict], config: Dict) -> List[str]:
        """
        Get symbols with 3-10% price drops (buy-the-dip candidates)
        Fast - uses local CSV data
        """
        min_drop = config.get('min_price_drop_pct', 3.0)
        max_drop = config.get('max_price_drop_pct', 10.0)
        
        dropped = []
        
        for sym in symbols[:2000]:  # Check up to 2000 symbols
            symbol = sym['symbol']
            
            # Check both stocks and ETFs directories
            for subdir in ['stocks', 'etfs']:
                csv_file = self.data_dir / subdir / f'{symbol}.csv'
                
                if csv_file.exists():
                    try:
                        df = pd.read_csv(csv_file)
                        if len(df) >= 2:
                            prev_close = df['Close'].iloc[-2]
                            latest_close = df['Close'].iloc[-1]
                            
                            if prev_close > 0:
                                pct_change = ((latest_close - prev_close) / prev_close * 100)
                                
                                # Negative change (drop) between min and max
                                if -max_drop <= pct_change <= -min_drop:
                                    dropped.append(symbol)
                                    break
                    except Exception:
                        continue
        
        return dropped
    
    def _get_trending_news_symbols(self) -> set:
        """
        Get symbols mentioned in trending market news
        Uses market-wide news endpoint (1 API call instead of 1000!)
        """
        if not self.finnhub:
            return set()
        
        # Check cache (6 hour TTL)
        if self._is_cache_valid():
            return self._load_cache()
        
        try:
            import finnhub
            client = finnhub.Client(api_key=os.getenv('FINNHUB_API_KEY'))
            
            # Get market-wide news (1 API call!)
            market_news = client.general_news('general', min_id=0)
            
            # Extract symbols mentioned in news
            trending = set()
            for article in market_news[:100]:  # Top 100 articles
                # Finnhub includes 'related' field with stock symbols
                if 'related' in article and article['related']:
                    # Can be comma-separated
                    symbols = article['related'].split(',')
                    trending.update([s.strip() for s in symbols if s.strip()])
            
            # Save to cache
            self._save_cache(list(trending))
            
            return trending
            
        except Exception as e:
            print(f"       ⚠️  Trending news fetch failed: {e}")
            return set()
    
    def _get_active_symbols(self, symbols: List[Dict], config: Dict) -> set:
        """
        Get symbols with volume spikes or price moves from local CSV data
        This is FAST - no API calls!
        """
        min_volume_ratio = config.get('min_volume_ratio', 2.0)
        min_price_move = config.get('min_price_move_pct', 5.0)
        
        active = set()
        
        for sym in symbols[:1000]:  # Limit to first 1000 for speed
            symbol = sym['symbol']
            
            # Check both stocks and ETFs directories
            for subdir in ['stocks', 'etfs']:
                csv_file = self.data_dir / subdir / f'{symbol}.csv'
                
                if csv_file.exists():
                    try:
                        df = pd.read_csv(csv_file)
                        if len(df) < 20:
                            continue
                        
                        df = df.tail(20)
                        
                        # Volume spike?
                        if 'Volume' in df.columns:
                            avg_vol = df['Volume'].iloc[:-1].mean()
                            latest_vol = df['Volume'].iloc[-1]
                            if avg_vol > 0 and latest_vol / avg_vol >= min_volume_ratio:
                                active.add(symbol)
                                break
                        
                        # Price move?
                        if 'Close' in df.columns and len(df) >= 2:
                            prev_close = df['Close'].iloc[-2]
                            latest_close = df['Close'].iloc[-1]
                            if prev_close > 0:
                                pct_change = abs((latest_close - prev_close) / prev_close * 100)
                                if pct_change >= min_price_move:
                                    active.add(symbol)
                                    break
                                    
                    except Exception:
                        continue
        
        return active
    
    def _is_cache_valid(self) -> bool:
        """Check if cache exists and is less than 6 hours old"""
        if not self.cache_file.exists():
            return False
        
        import json
        try:
            with open(self.cache_file, 'r') as f:
                cache_data = json.load(f)
            
            cache_time = datetime.fromisoformat(cache_data.get('timestamp', '2000-01-01'))
            age_hours = (datetime.now() - cache_time).total_seconds() / 3600
            
            return age_hours < 6
        except Exception:
            return False
    
    def _load_cache(self) -> set:
        """Load trending symbols from cache"""
        import json
        try:
            with open(self.cache_file, 'r') as f:
                cache_data = json.load(f)
            print(f"       → Using cached trending news (age: {cache_data.get('age', 'unknown')})")
            return set(cache_data.get('symbols', []))
        except Exception:
            return set()
    
    def _save_cache(self, symbols: List[str]):
        """Save trending symbols to cache"""
        import json
        try:
            self.cache_file.parent.mkdir(parents=True, exist_ok=True)
            cache_data = {
                'timestamp': datetime.now().isoformat(),
                'symbols': symbols,
                'age': '0 hours'
            }
            with open(self.cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
        except Exception as e:
            print(f"       ⚠️  Cache save failed: {e}")


class VolumeSpikesStrategy(SelectionStrategy):
    """Select symbols with unusual volume spikes"""
    
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
    
    def name(self) -> str:
        return "Volume Spikes"
    
    def select(self, symbols: List[Dict], max_symbols: int, config: Dict) -> List[Dict]:
        """Select symbols with >2x average volume"""
        min_spike_ratio = config.get('min_volume_ratio', 2.0)
        lookback_days = config.get('lookback_days', 20)
        
        scored_symbols = []
        
        for sym in symbols:
            symbol = sym['symbol']
            
            # Try both stocks and ETFs directories
            for subdir in ['stocks', 'etfs']:
                csv_file = self.data_dir / subdir / f'{symbol}.csv'
                
                if csv_file.exists():
                    try:
                        df = pd.read_csv(csv_file)
                        if len(df) >= lookback_days + 1:
                            df = df.tail(lookback_days + 1)
                            
                            if 'Volume' in df.columns:
                                avg_volume = df['Volume'].iloc[:-1].mean()
                                latest_volume = df['Volume'].iloc[-1]
                                
                                if avg_volume > 0:
                                    spike_ratio = latest_volume / avg_volume
                                    
                                    if spike_ratio >= min_spike_ratio:
                                        sym['score'] = spike_ratio
                                        sym['reason'] = f"{spike_ratio:.1f}x volume"
                                        scored_symbols.append(sym)
                                        break
                    except Exception:
                        continue
        
        # Sort by volume spike ratio
        scored_symbols.sort(key=lambda x: x.get('score', 0), reverse=True)
        return scored_symbols[:max_symbols]


class PriceMoveStrategy(SelectionStrategy):
    """Select symbols with significant price moves"""
    
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
    
    def name(self) -> str:
        return "Price Moves"
    
    def select(self, symbols: List[Dict], max_symbols: int, config: Dict) -> List[Dict]:
        """Select symbols with >5% price move"""
        min_move_pct = config.get('min_price_move_pct', 5.0)
        
        scored_symbols = []
        
        for sym in symbols:
            symbol = sym['symbol']
            
            # Try both stocks and ETFs directories
            for subdir in ['stocks', 'etfs']:
                csv_file = self.data_dir / subdir / f'{symbol}.csv'
                
                if csv_file.exists():
                    try:
                        df = pd.read_csv(csv_file)
                        if len(df) >= 2:
                            prev_close = df['Close'].iloc[-2]
                            latest_close = df['Close'].iloc[-1]
                            
                            if prev_close > 0:
                                pct_change = abs((latest_close - prev_close) / prev_close * 100)
                                
                                if pct_change >= min_move_pct:
                                    sym['score'] = pct_change
                                    sym['reason'] = f"{pct_change:.1f}% move"
                                    scored_symbols.append(sym)
                                    break
                    except Exception:
                        continue
        
        # Sort by price move percentage
        scored_symbols.sort(key=lambda x: x.get('score', 0), reverse=True)
        return scored_symbols[:max_symbols]


class LiquidityStrategy(SelectionStrategy):
    """Select high-liquidity symbols (market cap + volume)"""
    
    def name(self) -> str:
        return "High Liquidity"
    
    def select(self, symbols: List[Dict], max_symbols: int, config: Dict) -> List[Dict]:
        """Select most liquid symbols (simple: ETFs first, then stocks)"""
        etf_preference = config.get('prefer_etfs', True)
        
        etfs = []
        stocks = []
        
        for sym in symbols:
            asset_type = sym.get('type', '')
            symbol = sym.get('symbol', '')
            
            if asset_type == 'etf' or len(symbol) <= 4:
                etfs.append(sym)
            else:
                stocks.append(sym)
        
        # Combine based on preference
        if etf_preference:
            selected = etfs + stocks
        else:
            selected = stocks + etfs
        
        return selected[:max_symbols]


class SymbolSelector:
    """
    Main orchestrator for intelligent symbol selection
    Uses pluggable strategies defined in configuration
    """
    
    def __init__(self, config: Dict, finnhub_client=None, data_dir: Path = None):
        self.config = config
        self.finnhub = finnhub_client
        self.data_dir = data_dir or Path('data/market_data')
        
        # Initialize available strategies
        self.strategies = {
            'news': NewsBasedStrategy(finnhub_client, self.data_dir),
            'volume_spikes': VolumeSpikesStrategy(self.data_dir),
            'price_moves': PriceMoveStrategy(self.data_dir),
            'liquidity': LiquidityStrategy(),
        }
    
    def select_intelligent(self, all_symbols: List[Dict], max_symbols: int = 600) -> List[str]:
        """
        Intelligently select symbols using configured strategies
        
        Configuration format (in master_config.yaml):
        
        intelligent_selection:
          enabled: true
          strategies:
            - name: news
              weight: 30  # % of total symbols
              config:
                min_news_articles: 3
                lookback_hours: 24
            - name: volume_spikes
              weight: 30
              config:
                min_volume_ratio: 2.0
                lookback_days: 20
            - name: price_moves
              weight: 20
              config:
                min_price_move_pct: 5.0
            - name: liquidity
              weight: 20
              config:
                prefer_etfs: true
        """
        selection_config = self.config.get('intelligent_selection', {})
        
        if not selection_config.get('enabled', True):
            # Fallback to simple selection
            return [s['symbol'] for s in all_symbols[:max_symbols]]
        
        strategy_configs = selection_config.get('strategies', [])
        
        if not strategy_configs:
            # Default strategies if not configured
            strategy_configs = [
                {'name': 'news', 'weight': 20, 'config': {}},
                {'name': 'volume_spikes', 'weight': 20, 'config': {}},
                {'name': 'price_moves', 'weight': 20, 'config': {}},
                {'name': 'liquidity', 'weight': 40, 'config': {}},
            ]
        
        print("\n  🧠 Intelligent Selection Strategies:")
        
        selected_symbols = {}  # symbol -> dict
        
        # Apply each strategy
        for strategy_config in strategy_configs:
            strategy_name = strategy_config['name']
            weight = strategy_config.get('weight', 0)
            strat_config = strategy_config.get('config', {})
            
            if strategy_name not in self.strategies:
                print(f"     ⚠️  Unknown strategy: {strategy_name}")
                continue
            
            strategy = self.strategies[strategy_name]
            target_count = int(max_symbols * weight / 100)
            
            if target_count == 0:
                continue
            
            print(f"     • {strategy.name()}: targeting {target_count} symbols")
            
            try:
                # Get symbols from this strategy
                results = strategy.select(all_symbols, target_count, strat_config)
                
                # Add to selected (avoid duplicates)
                for sym in results:
                    symbol = sym['symbol']
                    if symbol not in selected_symbols:
                        selected_symbols[symbol] = sym
                
                print(f"       ✓ Found {len(results)} symbols")
                
            except Exception as e:
                print(f"       ✗ Strategy failed: {e}")
                continue
        
        # Fill remaining slots with high-liquidity symbols if needed
        if len(selected_symbols) < max_symbols:
            print(f"     • Filling remaining {max_symbols - len(selected_symbols)} slots...")
            liquidity_strategy = self.strategies['liquidity']
            remaining = max_symbols - len(selected_symbols)
            
            # Only add symbols not already selected
            unselected = [s for s in all_symbols if s['symbol'] not in selected_symbols]
            fill_symbols = liquidity_strategy.select(unselected, remaining, {})
            
            for sym in fill_symbols:
                selected_symbols[sym['symbol']] = sym
        
        result = list(selected_symbols.keys())[:max_symbols]
        
        print(f"\n  ✅ Selected {len(result)} symbols intelligently")
        
        return result

