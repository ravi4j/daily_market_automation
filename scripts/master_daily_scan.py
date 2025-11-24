#!/usr/bin/env python3
"""
MASTER DAILY MARKET SCANNER
Unified system that scans entire US market, identifies opportunities, and monitors portfolio
Integrates: FinBERT sentiment, Insider tracking, Technical analysis, Fundamentals
"""

import os
import sys
import yaml
import pandas as pd
import yfinance as yf
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
from dotenv import load_dotenv
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Load environment variables from .env file
load_dotenv(PROJECT_ROOT / '.env')

# Setup logging
LOGS_DIR = PROJECT_ROOT / 'logs'
LOGS_DIR.mkdir(exist_ok=True)

# Create logger
logger = logging.getLogger('master_scanner')
logger.setLevel(logging.DEBUG)

# File handler - detailed logs
log_file = LOGS_DIR / f'scan_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
file_handler = logging.FileHandler(log_file)
file_handler.setLevel(logging.DEBUG)
file_formatter = logging.Formatter('%(asctime)s | %(levelname)-8s | %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
file_handler.setFormatter(file_formatter)

# Console handler - only warnings and errors
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.WARNING)
console_formatter = logging.Formatter('%(levelname)s: %(message)s')
console_handler.setFormatter(console_formatter)

# Add handlers
logger.addHandler(file_handler)
logger.addHandler(console_handler)

logger.info("="*80)
logger.info("MASTER SCANNER - Starting new run")
logger.info(f"Log file: {log_file}")
logger.info("="*80)

# Import existing modules (reuse, don't duplicate)
from src.finnhub_data import FinnhubClient
from src.news_monitor import NewsMonitor
from src.indicators import TechnicalIndicators
from src.insider_tracker import InsiderTracker
from src.finbert_sentiment import get_sentiment_analyzer
from src.premarket_monitor import PreMarketMonitor
from src.premarket_opportunity_scanner import PreMarketOpportunityScanner
from src.strategy_runner import StrategyRunner
from src.abc_strategy import ABCStrategy
from src.symbol_selector import SymbolSelector

# Paths
CONFIG_FILE = PROJECT_ROOT / 'config' / 'master_config.yaml'
DATA_DIR = PROJECT_ROOT / 'data'
METADATA_DIR = DATA_DIR / 'metadata'
MARKET_DATA_DIR = DATA_DIR / 'market_data'
SIGNALS_DIR = PROJECT_ROOT / 'signals'

class MasterScanner:
    """
    Unified market scanner that integrates all features
    """

    def __init__(self, config_path: Path = CONFIG_FILE):
        """Initialize the master scanner"""
        print("=" * 80)
        print("MASTER DAILY MARKET SCANNER - Initializing...")
        print("=" * 80)

        # Load configuration
        self.config = self._load_config(config_path)

        # Initialize components (reuse existing modules)
        self.finnhub = None
        self.news_monitor = None
        self.insider_tracker = None
        self.sentiment_analyzer = None
        self.premarket_monitor = None
        self.premarket_scanner = None
        self.strategy_runner = None
        self.abc_strategy = None

        self._initialize_components()

        # Storage
        self.universe = []          # All symbols to scan
        self.opportunities = []     # Found opportunities
        self.portfolio_status = {}  # Portfolio health

        print("✅ Master Scanner initialized\n")

    def _load_config(self, config_path: Path) -> Dict:
        """Load master configuration"""
        if not config_path.exists():
            print(f"⚠️  Config not found: {config_path}")
            print("   Using default configuration")
            return self._get_default_config()

        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)

        print(f"✅ Loaded config: {config_path}")
        return config

    def _get_default_config(self) -> Dict:
        """Get default configuration if file missing"""
        return {
            'scanning': {
                'strategy': {'tier': 'daily'},
                'filters': {
                    'min_volume': 1000000,
                    'min_price': 5.0,
                    'exchanges': ['NYSE', 'NASDAQ', 'AMEX']
                },
                'max_symbols_per_run': 600
            },
            'scoring': {
                'weights': {
                    'news_sentiment': 30,
                    'technical': 40,
                    'fundamentals': 20,
                    'insider_activity': 10
                },
                'max_opportunities': 5,
                'min_confidence': 70
            },
            'finbert': {'enabled': True},
            'insider': {'enabled': True},
            'alerts': {'telegram': {'enabled': True}}
        }

    def _initialize_components(self):
        """Initialize all analysis components"""
        print("\n🔧 Initializing components...")

        # 1. Finnhub API (for symbols, insider data, fundamentals)
        try:
            api_key = os.getenv('FINNHUB_API_KEY')
            if api_key:
                self.finnhub = FinnhubClient(api_key)
                print("  ✅ Finnhub API connected")
            else:
                print("  ⚠️  Finnhub API key not found (will use fallbacks)")
        except Exception as e:
            print(f"  ⚠️  Finnhub initialization failed: {e}")

        # 2. FinBERT Sentiment Analyzer
        if self.config.get('finbert', {}).get('enabled', True):
            try:
                print("  🤖 Loading FinBERT sentiment analyzer...")
                self.sentiment_analyzer = get_sentiment_analyzer(use_finbert=True)
                print("  ✅ FinBERT ready (ML sentiment analysis)")
            except Exception as e:
                print(f"  ⚠️  FinBERT failed: {e}")
                print("     Will use keyword-based sentiment")

        # 3. News Monitor (integrates FinBERT)
        try:
            use_finbert = self.sentiment_analyzer is not None
            self.news_monitor = NewsMonitor(use_finbert=use_finbert)
            print("  ✅ News monitor ready")
        except Exception as e:
            print(f"  ⚠️  News monitor failed: {e}")

        # 4. Insider Tracker
        if self.config.get('insider', {}).get('enabled', True):
            try:
                self.insider_tracker = InsiderTracker()
                print("  ✅ Insider tracker ready")
            except Exception as e:
                print(f"  ⚠️  Insider tracker failed: {e}")

        # 5. Pre-Market Monitor & Gap Scanner
        try:
            positions = self.config.get('portfolio', {}).get('positions', {})
            self.premarket_monitor = PreMarketMonitor(positions)
            self.premarket_scanner = PreMarketOpportunityScanner()
            print("  ✅ Pre-market gap monitor ready")
        except Exception as e:
            print(f"  ⚠️  Pre-market monitor failed: {e}")

        # 6. Trading Strategies (ABC patterns, RSI+MACD, etc.)
        try:
            self.strategy_runner = StrategyRunner(data_dir=str(MARKET_DATA_DIR))
            self.abc_strategy = ABCStrategy()
            print("  ✅ Trading strategies ready (ABC, RSI+MACD, Momentum, etc.)")
        except Exception as e:
            print(f"  ⚠️  Strategy runner failed: {e}")

    # =========================================================================
    # PHASE 1: FETCH MARKET UNIVERSE
    # =========================================================================

    def _detect_market_crash(self):
        """
        Auto-detect market crashes by checking major indices
        Fully configurable via master_config.yaml
        """
        # Get crash detection config
        crash_config = self.config.get('scanning', {}).get('crash_detection', {})

        if not crash_config.get('enabled', True):
            self.market_crash = False
            return

        try:
            # Get configuration
            indices = crash_config.get('indices', ['SPY', 'QQQ', 'IWM', 'DIA'])
            crash_threshold = crash_config.get('crash_threshold_pct', 2.0)
            correction_threshold = crash_config.get('correction_threshold_pct', 1.0)
            require_all_negative = crash_config.get('check_all_negative', False)

            total_drop = 0
            count = 0
            changes = []

            print(f"\n  🔍 Market health check ({len(indices)} indices)...")

            for symbol in indices:
                try:
                    ticker = yf.Ticker(symbol)
                    data = ticker.history(period='2d')

                    if len(data) >= 2:
                        prev_close = data['Close'].iloc[-2]
                        current = data['Close'].iloc[-1]
                        change_pct = ((current - prev_close) / prev_close * 100)

                        changes.append(change_pct)
                        total_drop += min(0, change_pct)  # Only negative changes
                        count += 1
                except Exception:
                    continue

            if count > 0:
                avg_drop = abs(total_drop / count)

                # Check if all indices must be negative (if configured)
                all_negative = all(c < 0 for c in changes)

                if require_all_negative and not all_negative:
                    print(f"  ✅ Mixed market (some indices up, some down)")
                    self.market_crash = False
                elif avg_drop > crash_threshold:
                    print(f"  🚨 MARKET CRASH DETECTED: {avg_drop:.1f}% average drop")
                    print(f"     → Threshold: {crash_threshold}% | Prioritizing buy-the-dip!")
                    self.market_crash = True
                elif avg_drop > correction_threshold:
                    print(f"  ⚠️  Market correction: {avg_drop:.1f}% average drop")
                    print(f"     → Threshold: {correction_threshold}% | Watching closely")
                    self.market_crash = False
                else:
                    print(f"  ✅ Normal market: {avg_drop:.1f}% average change")
                    self.market_crash = False
            else:
                self.market_crash = False

        except Exception as e:
            print(f"  ⚠️  Market check failed: {e}")
            self.market_crash = False

    def fetch_market_universe(self) -> List[str]:
        """
        Fetch complete list of US market symbols from Finnhub
        Returns tiered list based on scan strategy

        AUTO-DETECTS market crashes and adjusts selection
        """
        print("\n" + "=" * 80)
        print("PHASE 1: FETCHING MARKET UNIVERSE")
        print("=" * 80)

        # Auto-detect market crash
        self._detect_market_crash()

        tier = self.config['scanning']['strategy']['tier']
        print(f"📊 Scan tier: {tier.upper()}")

        # Fetch from Finnhub API
        all_symbols = self._fetch_from_finnhub()

        # Apply tier filtering
        if tier == 'daily':
            # S&P 500 + Top 100 ETFs (~600 symbols)
            filtered = self._filter_tier_daily(all_symbols)
        elif tier == 'weekly':
            # Russell 2000 + All sector ETFs (~2000 symbols)
            filtered = self._filter_tier_weekly(all_symbols)
        elif tier == 'monthly' or tier == 'full':
            # Full market scan
            filtered = all_symbols
        else:
            filtered = self._filter_tier_daily(all_symbols)

        # Apply quality filters
        self.universe = self._apply_filters(filtered)

        print(f"✅ Universe loaded: {len(self.universe)} symbols")
        print(f"   Stocks: {self._count_by_type('stock')}")
        print(f"   ETFs: {self._count_by_type('etf')}")
        print(f"   Indices: {self._count_by_type('index')}\n")

        return self.universe

    def _fetch_from_finnhub(self) -> List[Dict]:
        """Fetch all US symbols from Finnhub API"""
        print("  📡 Fetching symbols from Finnhub API...")

        if not self.finnhub:
            print("  ⚠️  Finnhub not available, using fallback...")
            return self._fetch_fallback_symbols()

        try:
            # Finnhub: Get all US stocks
            import finnhub
            client = finnhub.Client(api_key=os.getenv('FINNHUB_API_KEY'))

            symbols = []

            # Get US stocks
            us_stocks = client.stock_symbols('US')
            for stock in us_stocks:
                if stock.get('type') in ['Common Stock', 'ETP']:  # ETP = ETF
                    symbols.append({
                        'symbol': stock['symbol'],
                        'name': stock.get('description', ''),
                        'type': 'etf' if stock.get('type') == 'ETP' else 'stock',
                        'exchange': stock.get('mic', '')
                    })

            print(f"  ✅ Fetched {len(symbols)} symbols from Finnhub")

            # Save to cache
            self._save_universe_cache(symbols)

            return symbols

        except Exception as e:
            print(f"  ⚠️  Finnhub fetch failed: {e}")
            return self._fetch_fallback_symbols()

    def _fetch_fallback_symbols(self) -> List[Dict]:
        """Fallback: Use cached or S&P 500 list"""
        print("  📂 Using fallback symbol source...")

        # Try cached universe
        cache_file = METADATA_DIR / 'all_us_symbols.csv'
        if cache_file.exists():
            df = pd.read_csv(cache_file)
            symbols = df.to_dict('records')
            print(f"  ✅ Loaded {len(symbols)} symbols from cache")
            return symbols

        # Ultimate fallback: S&P 500
        print("  📊 Using S&P 500 as fallback...")
        sp500_file = METADATA_DIR / 'sp500_comprehensive.txt'

        if sp500_file.exists():
            symbols = []
            with open(sp500_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    # Skip empty lines and comments
                    if not line or line.startswith('#'):
                        continue
                    # Parse CSV format: SYMBOL,Company Name,Sector
                    parts = line.split(',')
                    if parts:
                        symbol = parts[0].strip()
                        name = parts[1].strip() if len(parts) > 1 else ''
                        sector = parts[2].strip() if len(parts) > 2 else ''
                        symbols.append({
                            'symbol': symbol,
                            'name': name,
                            'type': 'stock',
                            'exchange': '',
                            'sector': sector
                        })
            print(f"  ✅ Loaded {len(symbols)} S&P 500 symbols")
            return symbols

        print("  ❌ No symbol source available!")
        return []

    def _save_universe_cache(self, symbols: List[Dict]):
        """Save universe to cache for fallback"""
        try:
            METADATA_DIR.mkdir(parents=True, exist_ok=True)
            df = pd.DataFrame(symbols)
            cache_file = METADATA_DIR / 'all_us_symbols.csv'
            df.to_csv(cache_file, index=False)
            print(f"  💾 Cached {len(symbols)} symbols")
        except Exception as e:
            print(f"  ⚠️  Cache save failed: {e}")

    def _sort_by_volume(self, symbols: List[Dict]) -> List[Dict]:
        """
        Sort symbols by trading volume (highest first)

        Uses volume from FIRST ROW of existing CSV files (latest day's volume).
        Symbols without CSVs get volume = 0 (placed at end, will be created during pre-screening).

        This is SUPER FAST - only reads first row of each CSV!

        Args:
            symbols: List of symbol dicts

        Returns:
            Sorted list (highest volume first)
        """
        from tqdm import tqdm

        print(f"     Reading volumes from CSV first rows for {len(symbols)} symbols...")

        # Get volume for each symbol from first row of CSV
        for sym_dict in tqdm(symbols, desc="     Volumes", unit="symbol", ncols=100, disable=len(symbols) < 100):
            symbol = sym_dict.get('symbol', '')
            asset_type = sym_dict.get('type', 'stock')

            # Determine CSV path
            if asset_type.lower() == 'etf':
                csv_path = MARKET_DATA_DIR / 'etfs' / f"{symbol}.csv"
            else:
                csv_path = MARKET_DATA_DIR / 'stocks' / f"{symbol}.csv"

            # Read ONLY first row to get latest volume (FAST!)
            if csv_path.exists():
                try:
                    df = pd.read_csv(csv_path, nrows=1)  # Only read first data row
                    if 'Volume' in df.columns and len(df) > 0:
                        volume = int(df['Volume'].iloc[0])
                        sym_dict['volume'] = volume
                    else:
                        sym_dict['volume'] = 0
                except:
                    sym_dict['volume'] = 0
            else:
                # No CSV yet - will be created during pre-screening
                sym_dict['volume'] = 0

        # Sort by volume (descending)
        symbols.sort(key=lambda x: x.get('volume', 0), reverse=True)

        print(f"     ✅ Sorted {len(symbols)} symbols by volume")

        # Show top symbols
        with_volume = [s for s in symbols if s.get('volume', 0) > 0]
        if with_volume:
            top_symbol = with_volume[0]
            print(f"        Top: {top_symbol['symbol']} (volume: {top_symbol.get('volume', 0):,.0f})")
            print(f"        Symbols with CSV data: {len(with_volume):,}")
            print(f"        Symbols needing fetch: {len(symbols) - len(with_volume):,}")

        return symbols

    def _filter_tier_daily(self, symbols: List[Dict]) -> List[Dict]:
        """
        INTELLIGENT 600 SELECTION SYSTEM - Pluggable Strategies

        Uses SymbolSelector with configurable strategies (NO HARDCODED SYMBOLS!)

        Strategies configured in master_config.yaml:
        - News-driven (20%): Symbols with breaking news
        - Volume spikes (20%): 2x+ volume
        - Price moves (20%): 5%+ price change
        - High liquidity (40%): ETFs + high-volume stocks

        100% configurable - add/remove/adjust strategies without code changes!
        """
        print("  🧠 Using pluggable intelligent selection strategies...")

        max_symbols = self.config['scanning'].get('max_symbols_per_run', 600)

        # Exchange filtering first (quality baseline)
        filters = self.config['scanning']['intelligent_filters']
        valid_exchanges = set(filters.get('exchanges', ['NYSE', 'NASDAQ', 'AMEX']))
        exchange_mapping = {
            'XNAS': 'NASDAQ', 'XNYS': 'NYSE', 'XASE': 'AMEX',
            'ARCX': 'NYSE', 'BATS': 'BATS',
        }

        quality_symbols = []
        for sym in symbols:
            exchange = sym.get('exchange', '')

            if exchange == 'OOTC':
                continue

            if not exchange:
                quality_symbols.append(sym)
            else:
                mapped = exchange_mapping.get(exchange, exchange)
                if any(valid in mapped for valid in valid_exchanges):
                    quality_symbols.append(sym)

        print(f"     Quality baseline: {len(quality_symbols)} symbols from major exchanges")

        # Sort by volume (highest activity first)
        # Uses volume from CSV first row - FAST!
        print(f"  📊 Sorting by volume (highest activity first)...")
        quality_symbols_sorted = self._sort_by_volume(quality_symbols)

        # Use SymbolSelector with pluggable strategies
        selector = SymbolSelector(
            config=self.config.get('scanning', {}),
            finnhub_client=self.finnhub,
            data_dir=MARKET_DATA_DIR
        )

        selected_symbols = selector.select_intelligent(quality_symbols_sorted, max_symbols)

        # Convert back to dict format
        result = [sym for sym in quality_symbols_sorted if sym['symbol'] in selected_symbols]

        return result

    # NOTE: _score_and_prioritize_symbols() and _has_recent_activity() methods
    # have been replaced by the pluggable SymbolSelector class in src/symbol_selector.py
    # See master_config.yaml for configurable selection strategies

    def _filter_tier_weekly(self, symbols: List[Dict]) -> List[Dict]:
        """Weekly tier: More comprehensive scan"""
        return symbols[:2000]

    def _apply_filters(self, symbols: List[Dict]) -> List[Dict]:
        """
        Return filtered symbol list with full metadata
        Exchange filtering already done in _filter_tier_daily()
        Keep dictionaries so we have type information for reporting
        """
        # Return full symbol dictionaries (not just strings) to preserve type info
        return symbols

    def _count_by_type(self, asset_type: str) -> int:
        """Count symbols by type"""
        # Count by actual type from metadata
        if asset_type == 'etf':
            return sum(1 for s in self.universe if isinstance(s, dict) and s.get('type', '').lower() == 'etf')
        elif asset_type == 'stock':
            return sum(1 for s in self.universe if isinstance(s, dict) and s.get('type', '').lower() == 'stock')
        return len(self.universe)

    def _quick_prescreen(self, symbols: List[Dict]) -> List[str]:
        """
        INTELLIGENT PRE-SCREENING

        Quickly filter entire market for promising candidates based on:
        1. Price action: Recent drops (2%+) = potential buy opportunity
        2. Volume: Above average volume = something happening
        3. Volatility: Movement without crash (not bankruptcy/fraud)
        4. Technical: Not in death spiral (avoid catching falling knives)

        This is FAST - can scan 1000s of symbols in minutes
        Then we do DEEP analysis on the 50-100 that pass

        Also tracks ALL fallers (2%+) for comprehensive report

        Args:
            symbols: List of symbol dictionaries with 'symbol' and 'type' fields

        Returns:
            List of symbol strings (candidates for deep analysis)
        """
        print(f"     Screening {len(symbols)} symbols for:")
        print(f"     • Price drops (2%+ = all fallers)")
        print(f"     • Volume spikes (interest)")
        print(f"     • Healthy technical structure (no knives)")
        print()

        candidates = []
        self.all_fallers = []  # Track ALL symbols with 2%+ drops

        # Thread-safe data structures
        lock = threading.Lock()

        def screen_symbol(sym_dict):
            """Screen a single symbol (for parallel execution)"""
            # Handle both dict and string formats for backward compatibility
            if isinstance(sym_dict, str):
                symbol = sym_dict
                asset_type = 'Stock'  # Default if no type info
            else:
                symbol = sym_dict.get('symbol')
                raw_type = sym_dict.get('type', 'stock')
                asset_type = 'ETF' if raw_type.lower() == 'etf' else 'Stock'

            if not symbol:
                return None

            try:
                # Load price data (uses CSV if available, fetches & saves if needed)
                df = self._load_price_data(symbol)

                if df is None or len(df) < 5:
                    return None

                # Calculate quick metrics (df is sorted ascending, so iloc[-1] is latest)
                recent_close = df['Close'].iloc[-1]
                prev_close = df['Close'].iloc[-2]
                pct_change = ((recent_close - prev_close) / prev_close) * 100

                avg_volume = df['Volume'].tail(10).mean()
                recent_volume = df['Volume'].iloc[-1]
                volume_ratio = recent_volume / avg_volume if avg_volume > 0 else 0

                # INTELLIGENT FILTERING RULES

                # Rule 1: Price drop (but not crash)
                significant_drop = pct_change <= -2  # 2%+ drop (user wants to see all)
                opportunity_drop = -10 <= pct_change <= -3  # 3-10% sweet spot

                # Rule 2: Volume spike (interest)
                volume_spike = volume_ratio > 1.2  # 20%+ above average

                # Rule 3: Price above $5 (avoid penny stocks)
                price_filter = recent_close >= 5.0

                # Rule 4: Decent volume (liquid)
                volume_filter = avg_volume >= 500000  # 500K+ daily volume

                # Rule 5: Not in death spiral (price not down >20% in 10 days)
                not_crashing = pct_change > -20

                # Track ALL fallers 2%+ for comprehensive report
                faller_data = None
                if significant_drop and price_filter and not_crashing:
                    # asset_type already determined at function start
                    faller_data = {
                        'symbol': symbol,
                        'type': asset_type,
                        'pct_change': pct_change,
                        'price': recent_close,
                        'volume': recent_volume,
                        'avg_volume': avg_volume,
                        'volume_ratio': volume_ratio
                    }

                # Check if it meets criteria for deep analysis
                is_candidate = False

                # Pass if it meets criteria for deep analysis (3-10% drop)
                if opportunity_drop and volume_spike and price_filter and volume_filter and not_crashing:
                    is_candidate = True
                # Also track significant fallers for deep analysis
                elif significant_drop and volume_spike and price_filter and volume_filter and not_crashing:
                    is_candidate = True
                # Also include symbols that just had volume spike (even without drop)
                elif volume_ratio > 2.0 and price_filter and volume_filter and not_crashing:
                    # 2x volume = something interesting happening
                    is_candidate = True

                return (is_candidate, faller_data)

            except:
                # Skip symbols we can't fetch data for
                return None

        # Screen symbols in parallel (50 workers for good balance)
        max_workers = 50
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(screen_symbol, symbol): symbol for symbol in symbols}

            with tqdm(total=len(futures), desc="     Pre-screening", unit="symbol", ncols=100) as pbar:
                for future in as_completed(futures):
                    try:
                        result = future.result()
                        if result:
                            is_candidate, faller_data = result

                            with lock:
                                if faller_data:
                                    self.all_fallers.append(faller_data)

                                if is_candidate:
                                    symbol = futures[future]
                                    candidates.append(symbol)
                                    pbar.set_postfix({"candidates": len(candidates)})
                    except:
                        pass
                    finally:
                        pbar.update(1)

        return candidates

    # =========================================================================
    # PHASE 2: SCAN FOR OPPORTUNITIES
    # =========================================================================

    def scan_market(self):
        """
        INTELLIGENT MARKET SCAN

        Two-phase approach:
        1. Quick pre-screen: Filter for price drops, volume spikes, volatility
        2. Deep analysis: Multi-signal scoring on promising candidates

        This way we scan 1000s of symbols quickly, then deeply analyze top 50-100
        """
        print("\n" + "=" * 80)
        print("PHASE 2: INTELLIGENT MARKET SCAN")
        print("=" * 80)

        print(f"🧠 Smart scanning {len(self.universe)} symbols...")
        print(f"   Phase A: Quick pre-screen (filter for opportunities)")
        print(f"   Phase B: Deep analysis (multi-signal scoring)\n")

        # PHASE A: Quick pre-screen
        print("  🔍 Phase A: Pre-screening entire market...")
        candidates = self._quick_prescreen(self.universe)
        print(f"  ✅ Found {len(candidates)} promising candidates\n")

        # PHASE B: Deep analysis on candidates
        print("  🎯 Phase B: Deep analysis of candidates...")
        print(f"     Using multi-signal scoring:")
        weights = self.config['scoring']['weights']
        print(f"     • News Sentiment: {weights['news_sentiment']}%")
        print(f"     • Technical Analysis: {weights['technical']}%")
        print(f"     • Fundamentals: {weights['fundamentals']}%")
        print(f"     • Insider Activity: {weights['insider_activity']}%\n")

        opportunities = []

        # Progress bar for deep analysis
        with tqdm(total=len(candidates), desc="     Deep analysis", unit="symbol", ncols=100) as pbar:
            for symbol in candidates:
                # Extract symbol string if we got a dict (should be string from _quick_prescreen)
                if isinstance(symbol, dict):
                    symbol_str = symbol.get('symbol')
                else:
                    symbol_str = symbol

                try:
                    logger.debug(f"Analyzing {symbol_str}...")
                    opp = self._analyze_symbol(symbol_str)
                    if opp:
                        opportunities.append(opp)
                        logger.info(f"✅ {symbol_str}: Score {opp['composite_score']:.1f} - {opp['confidence']}")
                        pbar.set_postfix({"opportunities": len(opportunities)})
                    else:
                        logger.debug(f"{symbol_str}: No opportunity (scored below threshold or failed analysis)")
                except Exception as e:
                    # Log errors for debugging
                    logger.error(f"❌ Error analyzing {symbol_str}: {type(e).__name__}: {e}")
                    import traceback
                    logger.debug(f"Traceback for {symbol_str}:\n{traceback.format_exc()}")
                finally:
                    pbar.update(1)

        # Sort by composite score
        opportunities.sort(key=lambda x: x['composite_score'], reverse=True)

        # Keep top N
        max_opps = self.config['scoring']['max_opportunities']
        self.opportunities = opportunities[:max_opps]

        print(f"\n✅ Scan complete:")
        print(f"   Scanned: {len(candidates)} symbols")
        print(f"   Found: {len(opportunities)} opportunities")
        print(f"   Top {len(self.opportunities)} selected\n")

        return self.opportunities

    def _analyze_symbol(self, symbol: str) -> Optional[Dict]:
        """
        Analyze single symbol with multi-signal scoring + strategy signals
        Returns opportunity dict or None
        """
        # Fetch price data
        df = self._load_price_data(symbol)
        if df is None or len(df) < 50:
            return None

        # Calculate scores
        news_score = self._score_news_sentiment(symbol)
        technical_score = self._score_technical(symbol, df)
        fundamental_score = self._score_fundamentals(symbol)
        insider_score = self._score_insider_activity(symbol)

        # Get detailed insider data
        insider_data = self._get_insider_details(symbol)

        # Check trading strategies (ABC, RSI+MACD, etc.)
        strategy_signals = self._check_strategies(symbol, df)

        # Composite score (weighted average)
        weights = self.config['scoring']['weights']
        composite = (
            news_score * weights['news_sentiment'] / 100 +
            technical_score * weights['technical'] / 100 +
            fundamental_score * weights['fundamentals'] / 100 +
            insider_score * weights['insider_activity'] / 100
        )

        # Boost score if strategies confirm
        if strategy_signals:
            # Add up to 10 points for strong strategy signals
            strategy_boost = min(10, len(strategy_signals) * 3)
            composite = min(100, composite + strategy_boost)

        # Confidence level
        confidence = self._calculate_confidence(composite)

        # Skip low confidence
        if confidence < self.config['scoring']['min_confidence']:
            return None

        # Recommendation
        recommendation = self._get_recommendation(composite)

        # Trade setup (use strategy if available, otherwise default)
        current_price = df['Close'].iloc[-1]

        if strategy_signals and strategy_signals[0].get('trade_setup'):
            # Use strategy's trade setup
            setup = strategy_signals[0]['trade_setup']
            stop_loss = setup.get('stop_loss', current_price * 0.93)
            target = setup.get('target', current_price * 1.20)
        else:
            # Default setup
            stop_loss = current_price * 0.93  # 7% stop
            target = current_price * 1.20     # 20% target

        risk_reward = (target - current_price) / (current_price - stop_loss) if current_price > stop_loss else 0

        # Build reasons list
        reasons = []
        if news_score > 70:
            reasons.append("Strong news sentiment")
        if technical_score > 70:
            reasons.append("Bullish technicals")
        if fundamental_score > 70:
            reasons.append("Solid fundamentals")
        if insider_score > 70:
            reasons.append("Insider buying")
        if strategy_signals:
            reasons.append(f"{strategy_signals[0]['strategy']} signal")

        return {
            'symbol': symbol,
            'composite_score': composite,
            'confidence': confidence,
            'recommendation': recommendation,
            'scores': {
                'news': news_score,
                'technical': technical_score,
                'fundamentals': fundamental_score,
                'insider': insider_score
            },
            'trade_setup': {
                'entry': current_price,
                'stop_loss': stop_loss,
                'target': target,
                'risk_reward': risk_reward
            },
            'strategy_signals': strategy_signals,
            'insider_activity': insider_data,  # Include detailed insider transactions
            'reasons': reasons,
            'timestamp': datetime.now().isoformat()
        }

    def _get_symbol_type(self, symbol: str) -> str:
        """Determine if symbol is stock, ETF, or index from cached metadata"""
        try:
            # Check cached metadata first
            cache_file = METADATA_DIR / 'all_us_symbols.csv'
            if cache_file.exists():
                df = pd.read_csv(cache_file)
                match = df[df['symbol'] == symbol]
                if not match.empty:
                    return match.iloc[0]['type']
        except:
            pass

        # Default to stock if unknown
        return 'stock'

    def _get_csv_path(self, symbol: str) -> Path:
        """Get CSV file path, organized by type if configured"""
        organize_by_type = self.config.get('data', {}).get('organize_by_type', True)

        if organize_by_type:
            # Organize into subdirectories: stocks/, etfs/, indices/
            symbol_type = self._get_symbol_type(symbol)
            type_dir = MARKET_DATA_DIR / f'{symbol_type}s'  # stocks, etfs, indices
            type_dir.mkdir(parents=True, exist_ok=True)
            return type_dir / f'{symbol}.csv'
        else:
            # Flat structure (legacy)
            return MARKET_DATA_DIR / f'{symbol}.csv'

    def _load_price_data(self, symbol: str) -> Optional[pd.DataFrame]:
        """
        Load historical price data with INCREMENTAL fetching

        Uses existing CSV if available, only fetches new data incrementally.
        This is MUCH faster than re-downloading everything!
        """
        csv_file = self._get_csv_path(symbol)

        # Also check legacy flat location for backwards compatibility
        legacy_csv = MARKET_DATA_DIR / f'{symbol}.csv'

        # Try to load existing CSV (check both locations)
        for check_file in [csv_file, legacy_csv]:
            if check_file.exists():
                try:
                    df = pd.read_csv(check_file, index_col=0, parse_dates=True)
                    # CSV is stored descending (newest first), sort ascending for analysis
                    df = df.sort_index(ascending=True)

                    # Round ALL data to proper precision (fixes old unrounded data)
                    price_cols = ['Open', 'High', 'Low', 'Close', 'Adj Close']
                    for col in price_cols:
                        if col in df.columns:
                            df[col] = df[col].round(2)

                    if 'Volume' in df.columns:
                        df['Volume'] = df['Volume'].round(0).astype('int64')
                    if 'Dividends' in df.columns:
                        df['Dividends'] = df['Dividends'].round(2)
                    if 'Stock Splits' in df.columns:
                        df['Stock Splits'] = df['Stock Splits'].round(2)
                    if 'Capital Gains' in df.columns:
                        df['Capital Gains'] = df['Capital Gains'].round(2)

                    # Check if data is recent (within last 7 days)
                    if not df.empty:
                        last_date = df.index[-1]
                        days_old = (pd.Timestamp.today() - last_date).days

                        if days_old <= 7:
                            # Recent enough - save with proper formatting (descending order)
                            df_save = df.sort_index(ascending=False)
                            csv_file.parent.mkdir(parents=True, exist_ok=True)
                            df_save.to_csv(csv_file)
                            # Return in ascending order for analysis
                            return df
                        elif days_old > 60:
                            # Data is VERY old (>60 days), fetch fresh 2 years instead of huge incremental
                            logger.info(f"{symbol}: CSV is {days_old} days old, fetching fresh 2y data...")
                            fresh_data = self._fetch_incremental(symbol, start_date=None)  # Will use period='2y'
                            
                            if not fresh_data.empty:
                                df = fresh_data  # Replace old data entirely
                            else:
                                # Fetch failed, use old data
                                logger.warning(f"{symbol}: Failed to fetch fresh data, using {days_old}-day-old cache")
                                return df
                        else:
                            # Data is 7-60 days old, fetch incremental update
                            start_date = (last_date + pd.Timedelta(days=1)).strftime('%Y-%m-%d')
                            new_data = self._fetch_incremental(symbol, start_date)

                            if not new_data.empty:
                                # Combine old + new data
                                df = pd.concat([df, new_data]).sort_index(ascending=True)
                                df = df[~df.index.duplicated(keep='last')]

                                # Round the combined data (new data should already be rounded, but ensure consistency)
                                for col in price_cols:
                                    if col in df.columns:
                                        df[col] = df[col].round(2)

                                if 'Volume' in df.columns:
                                    df['Volume'] = df['Volume'].round(0).astype('int64')
                                if 'Dividends' in df.columns:
                                    df['Dividends'] = df['Dividends'].round(2)
                                if 'Stock Splits' in df.columns:
                                    df['Stock Splits'] = df['Stock Splits'].round(2)
                                if 'Capital Gains' in df.columns:
                                    df['Capital Gains'] = df['Capital Gains'].round(2)

                                # Save updated CSV in descending order (newest first)
                                df_save = df.sort_index(ascending=False)
                                csv_file.parent.mkdir(parents=True, exist_ok=True)
                                df_save.to_csv(csv_file)

                                # Remove legacy file if we're organizing by type
                                if check_file == legacy_csv and csv_file != legacy_csv:
                                    try:
                                        legacy_csv.unlink()
                                    except:
                                        pass

                            return df
                except Exception as e:
                    # If error loading/parsing, try next location
                    continue

        # No CSV or error - fetch all historical data (one-time)
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period='2y')  # Get 2 years of data

            if len(df) > 0:
                # Flatten MultiIndex columns if present
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.get_level_values(0)

                df.index.name = 'Date'

                # Save for next time (enables incremental updates later)
                csv_file.parent.mkdir(parents=True, exist_ok=True)
                df.to_csv(csv_file)

                return df
        except:
            pass

        return None

    def _fetch_incremental(self, symbol: str, start_date: str) -> pd.DataFrame:
        """Fetch only new data since start_date (incremental update)"""
        try:
            # Check if trying to fetch future dates
            start_dt = pd.Timestamp(start_date)
            today = pd.Timestamp.today().normalize()

            if start_dt > today:
                return pd.DataFrame()  # No new data yet

            ticker = yf.Ticker(symbol)
            df = ticker.history(start=start_date, interval='1d')

            if not df.empty:
                # Flatten MultiIndex columns if present
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.get_level_values(0)

                df.index.name = 'Date'

            return df
        except:
            return pd.DataFrame()

    def _score_news_sentiment(self, symbol: str) -> float:
        """Score based on news sentiment (0-100)"""
        if not self.news_monitor:
            return 50.0  # Neutral if unavailable

        try:
            opportunities = self.news_monitor.identify_opportunities([symbol])
            if opportunities:
                opp = opportunities[0]
                return opp.get('opportunity_score', 50.0)
        except:
            pass

        return 50.0

    def _score_technical(self, symbol: str, df: pd.DataFrame) -> float:
        """Score based on technical indicators (0-100)"""
        try:
            indicators = TechnicalIndicators(df)

            score = 50.0  # Start neutral

            # RSI (oversold = good)
            rsi = indicators.get_rsi()
            if rsi < 30:
                score += 20
            elif rsi < 40:
                score += 10
            elif rsi > 70:
                score -= 20

            # MACD (bullish cross = good)
            macd_data = indicators.get_macd()
            if macd_data['macd'] > macd_data['signal']:
                score += 15

            # Trend (uptrend = good)
            if indicators.is_uptrend():
                score += 15

            return max(0, min(100, score))

        except:
            return 50.0

    def _score_fundamentals(self, symbol: str) -> float:
        """Score based on fundamental metrics (0-100)"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info

            score = 50.0

            # P/E ratio
            pe = info.get('forwardPE', info.get('trailingPE'))
            if pe and pe < 25:
                score += 10

            # Profit margin
            margin = info.get('profitMargins', 0) * 100
            if margin > 10:
                score += 10

            # Analyst rating
            rating = info.get('recommendationMean')
            if rating and rating < 2.5:  # Strong buy/buy
                score += 15

            return max(0, min(100, score))

        except:
            return 50.0

    def _score_insider_activity(self, symbol: str) -> float:
        """Score based on insider transactions (0-100)"""
        if not self.insider_tracker:
            return 50.0

        try:
            insider_data = self.insider_tracker.get_insider_activity(symbol, days=180)

            if not insider_data:
                return 50.0

            sentiment = insider_data.get('sentiment', 'NEUTRAL')

            # Convert sentiment to score
            sentiment_map = {
                'STRONG_BUY': 85,
                'BUY': 70,
                'NEUTRAL': 50,
                'SELL': 30,
                'STRONG_SELL': 15
            }

            return sentiment_map.get(sentiment, 50.0)

        except:
            return 50.0

    def _get_insider_details(self, symbol: str) -> Dict:
        """Get detailed insider transaction information"""
        if not self.insider_tracker:
            return {
                'sentiment': 'NEUTRAL',
                'num_buys': 0,
                'num_sells': 0,
                'net_value': 0,
                'transactions': [],
                'summary': 'No insider tracker available'
            }

        try:
            # Get insider activity (last 6 months)
            insider_data = self.insider_tracker.get_insider_activity(symbol, days=180)

            if not insider_data:
                return {
                    'sentiment': 'NEUTRAL',
                    'num_buys': 0,
                    'num_sells': 0,
                    'net_value': 0,
                    'transactions': [],
                    'summary': 'No recent insider transactions'
                }

            # Extract key info
            num_buys = insider_data.get('num_buys', 0)
            num_sells = insider_data.get('num_sells', 0)
            sentiment = insider_data.get('sentiment', 'NEUTRAL')
            net_value = insider_data.get('net_value', 0)

            # Get top 5 transactions (most recent or largest)
            all_txns = insider_data.get('all_transactions', [])
            recent_txns = []
            for txn in all_txns[:5]:  # Take first 5
                recent_txns.append({
                    'name': txn.name,
                    'change': txn.change,
                    'date': txn.transaction_date,
                    'price': txn.share_price,
                    'value': txn.transaction_value
                })

            # Build summary
            summary = f"{num_buys} buys, {num_sells} sells (last 6 months)"
            if net_value > 0:
                summary += f" | Net: +${net_value/1e6:.1f}M"
            elif net_value < 0:
                summary += f" | Net: -${abs(net_value)/1e6:.1f}M"

            return {
                'sentiment': sentiment,
                'num_buys': num_buys,
                'num_sells': num_sells,
                'net_value': net_value,
                'largest_buy': insider_data.get('largest_buy'),
                'largest_sell': insider_data.get('largest_sell'),
                'transactions': recent_txns,
                'summary': summary
            }

        except Exception as e:
            logger.debug(f"Error getting insider details for {symbol}: {e}")
            return {
                'sentiment': 'NEUTRAL',
                'num_buys': 0,
                'num_sells': 0,
                'net_value': 0,
                'transactions': [],
                'summary': f'Error: {str(e)}'
            }

    def _check_strategies(self, symbol: str, df: pd.DataFrame) -> List[Dict]:
        """
        Check all trading strategies for signals

        EXTENSIBLE DESIGN: Easy to add more strategies!

        To add a new strategy:
        1. Create strategy class in src/ (e.g., src/macd_crossover_strategy.py)
        2. Initialize in _initialize_components()
        3. Add check here in _check_strategies()

        Returns list of strategy signals (if any)
        """
        signals = []

        if not self.strategy_runner:
            return signals

        try:
            # Strategy 1: ABC Patterns (wave-based entry/exit)
            if self.abc_strategy:
                abc_signals = self.abc_strategy.generate_signals(df)
                for signal in abc_signals:
                    if signal.signal == 'BUY' and signal.confidence in ['HIGH', 'MEDIUM']:
                        signals.append({
                            'strategy': 'ABC Pattern',
                            'signal': signal.signal,
                            'confidence': signal.confidence,
                            'pattern_type': signal.pattern_type,
                            'trade_setup': {
                                'entry': signal.best_entry or signal.current_price,
                                'stop_loss': signal.stop_loss,
                                'target': signal.take_profit_1,
                                'risk_reward': signal.risk_reward
                            },
                            'details': f"{signal.pattern_type} ABC pattern ({signal.retracement_pct:.1f}% retrace)"
                        })

            # Strategy 2: RSI + MACD Confluence
            rsi_macd_signal = self.strategy_runner.strategy_rsi_macd_confluence(symbol, df)
            if rsi_macd_signal and rsi_macd_signal.signal == 'BUY':
                signals.append({
                    'strategy': 'RSI+MACD',
                    'signal': rsi_macd_signal.signal,
                    'confidence': rsi_macd_signal.confidence,
                    'trade_setup': None,  # Uses default
                    'details': rsi_macd_signal.reason
                })

            # Strategy 3: Momentum Breakout
            momentum_signal = self.strategy_runner.strategy_momentum_breakout(symbol, df)
            if momentum_signal and momentum_signal.signal == 'BUY':
                signals.append({
                    'strategy': 'Momentum Breakout',
                    'signal': momentum_signal.signal,
                    'confidence': momentum_signal.confidence,
                    'trade_setup': None,
                    'details': momentum_signal.reason
                })

            # Strategy 4: Bollinger Band Mean Reversion
            bb_signal = self.strategy_runner.strategy_bollinger_mean_reversion(symbol, df)
            if bb_signal and bb_signal.signal == 'BUY':
                signals.append({
                    'strategy': 'Mean Reversion',
                    'signal': bb_signal.signal,
                    'confidence': bb_signal.confidence,
                    'trade_setup': None,
                    'details': bb_signal.reason
                })

            # Strategy 5: Trend Following
            trend_signal = self.strategy_runner.strategy_trend_following(symbol, df)
            if trend_signal and trend_signal.signal == 'BUY':
                signals.append({
                    'strategy': 'Trend Following',
                    'signal': trend_signal.signal,
                    'confidence': trend_signal.confidence,
                    'trade_setup': None,
                    'details': trend_signal.reason
                })

            # TODO: ADD MORE STRATEGIES HERE
            # Strategy 6: YOUR_NEW_STRATEGY
            # if self.your_strategy:
            #     signal = self.your_strategy.generate_signal(symbol, df)
            #     if signal and signal.signal == 'BUY':
            #         signals.append({...})

        except Exception as e:
            # Silent fail - don't break scanning for strategy errors
            pass

        return signals

    def _calculate_confidence(self, score: float) -> float:
        """Calculate confidence level"""
        return score

    def _get_recommendation(self, score: float) -> str:
        """Get recommendation based on score"""
        thresholds = self.config['scoring']['recommendation_thresholds']

        if score >= thresholds['strong_buy']:
            return 'STRONG BUY'
        elif score >= thresholds['buy']:
            return 'BUY'
        elif score >= thresholds['watch']:
            return 'WATCH'
        else:
            return 'SKIP'

    # =========================================================================
    # PHASE 3: MONITOR PORTFOLIO
    # =========================================================================

    def check_portfolio(self):
        """Check portfolio positions for rebalancing needs"""
        print("\n" + "=" * 80)
        print("PHASE 3: PORTFOLIO HEALTH CHECK")
        print("=" * 80)

        positions = self.config.get('portfolio', {}).get('positions', {})

        if not positions:
            print("ℹ️  No positions defined in config\n")
            return

        print(f"📊 Checking {len(positions)} positions...\n")

        for symbol, shares in positions.items():
            status = self._check_position(symbol, shares)
            self.portfolio_status[symbol] = status

            # Print status
            emoji = "✅" if status['healthy'] else "⚠️"
            print(f"{emoji} {symbol}: {status['message']}")

        print()

    def _check_position(self, symbol: str, shares: int) -> Dict:
        """Check single position health"""
        try:
            ticker = yf.Ticker(symbol)
            current_price = ticker.history(period='1d')['Close'].iloc[-1]

            # Simple health check
            return {
                'symbol': symbol,
                'shares': shares,
                'current_price': current_price,
                'value': shares * current_price,
                'healthy': True,
                'message': f"${current_price:.2f} | Value: ${shares * current_price:,.0f}"
            }

        except Exception as e:
            return {
                'symbol': symbol,
                'shares': shares,
                'healthy': False,
                'message': f"Error: {e}"
            }

    # =========================================================================
    # PHASE 4: GENERATE ALERTS
    # =========================================================================

    def generate_alert(self) -> str:
        """Generate consolidated Telegram alert"""
        print("\n" + "=" * 80)
        print("PHASE 5: GENERATING ALERT")
        print("=" * 80)

        alert = self._format_alert_message()

        print("✅ Alert generated\n")

        return alert

    def _format_alert_message(self) -> str:
        """Format simple alert message - just symbols and actions"""
        msg = []

        # Header
        msg.append("📈 DAILY PICKS")
        msg.append(f"{datetime.now().strftime('%Y-%m-%d %H:%M ET')}")
        msg.append("")

        # Just the symbols and key info
        if self.opportunities:
            for i, opp in enumerate(self.opportunities, 1):
                score = opp['composite_score']
                conf_badge = "🟢" if score >= 80 else "🟡" if score >= 60 else "🔴"

                trade = opp['trade_setup']

                # Simple format: Symbol, Action, Entry, Stop, Target
                msg.append(f"{i}. {conf_badge} **{opp['recommendation']}** {opp['symbol']}")
                msg.append(f"   Entry: ${trade['entry']:.2f} | Stop: ${trade['stop_loss']:.2f} | Target: ${trade['target']:.2f}")
                msg.append("")
        else:
            msg.append("No opportunities found today.")
            msg.append("")

        # Portfolio status (if any)
        if self.portfolio_status:
            msg.append("💼 YOUR POSITIONS")
            for symbol, status in self.portfolio_status.items():
                emoji = "✅" if status['healthy'] else "⚠️"
                msg.append(f"{emoji} {symbol}: {status['message']}")
            msg.append("")

        msg.append("Scanned: {0} symbols".format(len(self.universe)))

        return "\n".join(msg)

    def send_alert(self, message: str):
        """Send alert to Telegram"""
        telegram_config = self.config.get('alerts', {}).get('telegram', {})

        if not telegram_config.get('enabled', True):
            print("ℹ️  Telegram alerts disabled\n")
            return

        bot_token = os.getenv(telegram_config.get('bot_token_env', 'TELEGRAM_BOT_TOKEN'))
        chat_id = os.getenv(telegram_config.get('chat_id_env', 'TELEGRAM_CHAT_ID'))

        if not bot_token or not chat_id:
            print("⚠️  Telegram credentials not found")
            print("   Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID environment variables\n")
            return

        try:
            import requests

            # Send text message first
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            payload = {
                'chat_id': chat_id,
                'text': message,
                'parse_mode': 'HTML'
            }
            response = requests.post(url, json=payload)

            if response.status_code == 200:
                print("✅ Alert sent to Telegram")
            else:
                print(f"⚠️  Telegram send failed: {response.status_code}")

            # Send opportunity charts
            self._send_opportunity_charts(bot_token, chat_id)

        except Exception as e:
            print(f"⚠️  Telegram send error: {e}\n")

    def _send_opportunity_charts(self, bot_token: str, chat_id: str):
        """Send opportunity charts to Telegram"""
        if not self.opportunities:
            return

        import requests
        from pathlib import Path
        from datetime import datetime

        # Find charts for today's opportunities
        date_str = datetime.now().strftime("%Y%m%d")
        charts_sent = 0

        try:
            for opp in self.opportunities[:5]:  # Send top 5 charts max
                symbol = opp['symbol']

                # Determine asset type
                asset_type = 'stock'
                for sym_dict in self.universe:
                    if isinstance(sym_dict, dict) and sym_dict.get('symbol') == symbol:
                        asset_type = sym_dict.get('type', 'stock').lower()
                        break

                # Find chart file
                if asset_type == 'etf':
                    chart_path = Path(f'charts/etfs/{symbol}_{date_str}.png')
                else:
                    chart_path = Path(f'charts/stocks/{symbol}_{date_str}.png')

                if chart_path.exists():
                    # Send photo with caption
                    url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"

                    trade_setup = opp.get('trade_setup', {})
                    caption = (
                        f"📊 *{symbol}* - {opp.get('confidence', 'N/A')} Confidence\n"
                        f"Score: {opp.get('composite_score', 0):.1f}/100\n"
                        f"Entry: ${trade_setup.get('entry', 0):.2f} | "
                        f"Target: ${trade_setup.get('target', 0):.2f}\n"
                        f"Stop: ${trade_setup.get('stop_loss', 0):.2f} | "
                        f"R/R: {trade_setup.get('risk_reward', 0):.1f}:1"
                    )

                    with open(chart_path, 'rb') as photo:
                        files = {'photo': photo}
                        data = {
                            'chat_id': chat_id,
                            'caption': caption,
                            'parse_mode': 'Markdown'
                        }
                        response = requests.post(url, files=files, data=data)

                        if response.status_code == 200:
                            charts_sent += 1
                        else:
                            print(f"   ⚠️  Chart send failed for {symbol}: {response.status_code}")

            if charts_sent > 0:
                print(f"📊 {charts_sent} chart(s) sent to Telegram\n")
            else:
                print("   ℹ️  No charts available to send\n")

        except Exception as e:
            print(f"   ⚠️  Chart send error: {e}\n")

    # =========================================================================
    # MAIN EXECUTION
    # =========================================================================

    def _update_all_existing_csvs(self):
        """
        Update ALL existing CSV files incrementally (Phase 0)
        
        This is FAST because:
        - Only updates files that exist (doesn't fetch new symbols)
        - Only fetches data since last date in CSV
        - Runs in parallel with 20 workers
        - Takes ~5-10 minutes for 23,888 symbols
        """
        print("\n" + "=" * 80)
        print("PHASE 0: INCREMENTAL DATA UPDATE FOR ALL SYMBOLS")
        print("=" * 80)
        
        # Find all existing CSVs
        stock_csvs = list(STOCK_DIR.glob('*.csv'))
        etf_csvs = list(ETF_DIR.glob('*.csv'))
        all_csvs = stock_csvs + etf_csvs
        
        print(f"📊 Found {len(all_csvs)} existing CSV files")
        print(f"   Stocks: {len(stock_csvs)}")
        print(f"   ETFs: {len(etf_csvs)}")
        print(f"\n⏳ Updating incrementally (only fetching new data since last date)...\n")
        
        from concurrent.futures import ThreadPoolExecutor, as_completed
        from tqdm import tqdm
        
        updated_count = 0
        skipped_count = 0
        error_count = 0
        
        def update_single_csv(csv_path: Path) -> str:
            """Update a single CSV file incrementally"""
            symbol = csv_path.stem
            
            try:
                # Read existing CSV
                df = pd.read_csv(csv_path, index_col=0, parse_dates=True)
                if df.empty:
                    return 'empty'
                
                # Check how old the data is
                last_date = df.index.max()  # Works with both ascending/descending
                now = pd.Timestamp.now()
                if last_date.tz is not None:
                    now = now.tz_localize('UTC').tz_convert(last_date.tz)
                days_old = (now - last_date).days
                
                # Skip if data is fresh (< 1 day old)
                if days_old < 1:
                    return 'fresh'
                
                # Fetch incremental data
                start_date = last_date + pd.Timedelta(days=1)
                ticker = yf.Ticker(symbol)
                new_data = ticker.history(start=start_date.strftime('%Y-%m-%d'), end=None)
                
                if new_data.empty:
                    return 'no_new_data'
                
                # Combine and deduplicate
                combined = pd.concat([df, new_data])
                combined = combined[~combined.index.duplicated(keep='last')]
                
                # Round to proper precision
                price_cols = ['Open', 'High', 'Low', 'Close', 'Adj Close']
                for col in price_cols:
                    if col in combined.columns:
                        combined[col] = combined[col].round(2)
                
                if 'Volume' in combined.columns:
                    combined['Volume'] = combined['Volume'].round(0).astype('int64')
                if 'Dividends' in combined.columns:
                    combined['Dividends'] = combined['Dividends'].round(2)
                if 'Stock Splits' in combined.columns:
                    combined['Stock Splits'] = combined['Stock Splits'].round(2)
                if 'Capital Gains' in combined.columns:
                    combined['Capital Gains'] = combined['Capital Gains'].round(2)
                
                # Sort descending (newest first) and save
                combined = combined.sort_index(ascending=False)
                combined.to_csv(csv_path)
                
                return 'updated'
                
            except Exception as e:
                logger.debug(f"Error updating {symbol}: {e}")
                return 'error'
        
        # Process in parallel
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = {executor.submit(update_single_csv, csv): csv for csv in all_csvs}
            
            for future in tqdm(as_completed(futures), total=len(all_csvs), desc="Updating CSVs"):
                result = future.result()
                if result == 'updated':
                    updated_count += 1
                elif result == 'fresh':
                    skipped_count += 1
                elif result == 'error':
                    error_count += 1
        
        print(f"\n✅ CSV Update Complete:")
        print(f"   Updated: {updated_count}")
        print(f"   Fresh (skipped): {skipped_count}")
        print(f"   Errors: {error_count}\n")
        
        logger.info(f"CSV Update: {updated_count} updated, {skipped_count} fresh, {error_count} errors")

    def run(self, mode: str = 'daily'):
        """
        Run market scan workflow

        Args:
            mode: 'daily' (after close), 'premarket' (before open), 'intraday' (during market)
        """
        try:
            if mode == 'premarket':
                self._run_premarket_scan()
            elif mode == 'intraday':
                self._run_intraday_scan()
            else:
                self._run_daily_scan()

        except KeyboardInterrupt:
            print("\n\n⚠️  Scan interrupted by user\n")
        except Exception as e:
            print(f"\n\n❌ Scan failed: {e}\n")
            raise

    def _run_daily_scan(self):
        """Daily scan (after market close) - comprehensive analysis"""
        print("\n🌙 DAILY SCAN MODE (After Market Close)")
        print("   Comprehensive analysis of entire market\n")

        # Phase 0: Update ALL existing CSVs incrementally (FAST!)
        self._update_all_existing_csvs()

        # Phase 1: Fetch universe
        self.fetch_market_universe()

        # Phase 2: Scan for opportunities
        self.scan_market()

        # Phase 3: Check portfolio
        self.check_portfolio()

        # Phase 4: Generate opportunity charts FIRST (before Telegram)
        print("\n" + "=" * 80)
        print("PHASE 4: GENERATING OPPORTUNITY CHARTS")
        print("=" * 80)
        self._generate_opportunity_charts()

        # Phase 5: Generate and send alert with charts
        alert = self.generate_alert()
        print("\n" + "=" * 80)
        print("PREVIEW OF ALERT:")
        print("=" * 80)
        print(alert)
        print("=" * 80 + "\n")

        self.send_alert(alert)

        # Save results (reports only, charts already done)
        self._save_results()

        print("✅ DAILY SCAN COMPLETE!\n")

        # Log summary
        logger.info("="*80)
        logger.info("DAILY SCAN COMPLETE")
        logger.info(f"Scanned: {len(self.universe)} symbols")
        logger.info(f"Candidates: {len(self.opportunities) if hasattr(self, 'opportunities') else 0}")
        logger.info(f"Opportunities found: {len(self.opportunities)}")
        logger.info(f"Charts generated: {len(self.generated_chart_paths) if hasattr(self, 'generated_chart_paths') else 0}")
        logger.info(f"Fallers (2%+): {len(self.all_fallers) if hasattr(self, 'all_fallers') else 0}")
        logger.info(f"Log file: {log_file}")
        logger.info("="*80)

    def _run_premarket_scan(self):
        """Pre-market scan (before market open) - gap analysis"""
        print("\n🌅 PRE-MARKET SCAN MODE (Before Market Open)")
        print("   Gap detection and opportunity analysis\n")

        if not self.premarket_monitor or not self.premarket_scanner:
            print("❌ Pre-market monitoring not available\n")
            return

        # Check if in pre-market hours
        if not self.premarket_monitor.is_premarket_hours():
            print("⚠️  Not in pre-market hours (4:00 AM - 9:30 AM ET)")
            print("   Running in demo mode...\n")

        print("=" * 80)
        print("PHASE 1: PRE-MARKET GAP ANALYSIS")
        print("=" * 80)

        # Get symbols to monitor
        positions = self.config.get('portfolio', {}).get('positions', {})

        if positions:
            print(f"\n📊 Checking {len(positions)} portfolio positions for gaps...\n")

            gaps = []
            for symbol in positions.keys():
                gap_data = self.premarket_monitor.get_premarket_price(symbol)
                if gap_data:
                    gaps.append(gap_data)

                    emoji = "🔴" if gap_data['change_pct'] < -2 else "🟢" if gap_data['change_pct'] > 2 else "⚪"
                    print(f"{emoji} {symbol}: {gap_data['premarket_price']} ({gap_data['change_pct']:+.2f}%)")

            print()

        # Scan for gap opportunities
        print("\n" + "=" * 80)
        print("PHASE 2: GAP OPPORTUNITY SCAN")
        print("=" * 80)
        print(f"\n🔍 Checking gaps for yesterday's top opportunities...\n")

        # SMART: Only check gaps for yesterday's top opportunities!
        # These are the symbols you're actually considering to trade
        print(f"  🎯 Loading yesterday's top opportunities...")

        scan_symbols = []

        # Add portfolio positions (highest priority - monitor your holdings)
        if positions:
            scan_symbols.extend(positions.keys())
            print(f"     → {len(positions)} portfolio positions")

        # Load yesterday's top opportunities from saved results
        results_file = SIGNALS_DIR / 'master_scan_results.json'
        if results_file.exists():
            try:
                import json
                with open(results_file, 'r') as f:
                    results = json.load(f)

                opportunities = results.get('opportunities', [])
                if opportunities:
                    # Add top opportunities (these are your trade candidates!)
                    for opp in opportunities[:10]:  # Top 10 opportunities
                        symbol = opp.get('symbol')
                        if symbol and symbol not in scan_symbols:
                            scan_symbols.append(symbol)

                    print(f"     → {len(opportunities[:10])} top opportunities from yesterday")
                else:
                    print(f"     ⚠️  No opportunities in results file")
            except Exception as e:
                print(f"     ⚠️  Could not load results: {e}")
        else:
            print(f"     ⚠️  No results file found (run daily scan first)")

        # Fallback: if no symbols, use major indices
        if not scan_symbols:
            scan_symbols = ['SPY', 'QQQ', 'IWM', 'DIA', 'VTI']
            print(f"     → Using fallback: major indices")

        print(f"\n  ✅ Checking gaps for {len(scan_symbols)} symbols")

        opportunities = self.premarket_scanner.scan_for_opportunities(
            symbols=scan_symbols,  # Already limited to 50
            min_gap_pct=3.0,
            max_opportunities=5
        )

        print(f"\n✅ Found {len(opportunities)} gap opportunities\n")

        # Generate pre-market alert
        alert = self._format_premarket_alert(gaps if positions else [], opportunities)

        print("\n" + "=" * 80)
        print("PREVIEW OF PRE-MARKET ALERT:")
        print("=" * 80)
        print(alert)
        print("=" * 80 + "\n")

        self.send_alert(alert)

        print("✅ PRE-MARKET SCAN COMPLETE!\n")

    def _run_intraday_scan(self):
        """Intraday scan (during market hours) - quick momentum check"""
        print("\n📈 INTRADAY SCAN MODE (Market Hours)")
        print("   Quick momentum and breakout check\n")

        # TODO: Implement intraday scanning
        # - Check for volume spikes
        # - Check for breakouts
        # - Check for sudden moves

        print("⚠️  Intraday scanning coming soon!\n")

    def _format_premarket_alert(self, position_gaps: List[Dict], opportunities: List[Dict]) -> str:
        """Format pre-market alert message"""
        msg = []

        msg.append("🌅 PRE-MARKET ALERT")
        msg.append(f"{datetime.now().strftime('%Y-%m-%d %H:%M ET')}")
        msg.append("=" * 40)

        # Portfolio gaps
        if position_gaps:
            msg.append("\n⚖️ YOUR POSITIONS")
            for gap in position_gaps:
                emoji = "🔴" if gap['change_pct'] < -2 else "🟢" if gap['change_pct'] > 2 else "⚪"
                msg.append(f"{emoji} {gap['symbol']}: ${gap['premarket_price']:.2f} ({gap['change_pct']:+.2f}%)")
                msg.append(f"   Prev Close: ${gap['previous_close']:.2f}")

                # Risk assessment
                if gap['change_pct'] < -5:
                    msg.append(f"   ⚠️  GAP DOWN > 5% - Check stop loss!")
                elif gap['change_pct'] < -3:
                    msg.append(f"   ⚠️  GAP DOWN - Monitor closely")

        # Gap opportunities
        if opportunities:
            msg.append(f"\n🚀 GAP OPPORTUNITIES (Top {len(opportunities)})")

            for i, opp in enumerate(opportunities[:5], 1):
                opp_type = opp.get('opportunity_type', 'GAP')
                confidence = opp.get('confidence', 'MEDIUM')
                badge = "🟢" if confidence == 'HIGH' else "🟡" if confidence == 'MEDIUM' else "⚪"

                msg.append(f"\n{i}. {badge} {opp['symbol']} - {opp_type}")
                msg.append(f"   Gap: {opp['gap_pct']:.2f}% | Score: {opp['score']:.0f}/100")
                msg.append(f"   Entry: ${opp['entry']:.2f} | Target: ${opp['target']:.2f}")
                msg.append(f"   Stop: ${opp['stop']:.2f}")
                reasons = opp.get('reasons', [])
                if reasons:
                    msg.append(f"   Why: {', '.join(reasons[:2])}")  # Show top 2 reasons

        msg.append("\n" + "=" * 40)
        msg.append("⏰ Market opens at 9:30 AM ET")
        msg.append("🤖 Powered by Master Scanner")

        return "\n".join(msg)

    def _save_results(self):
        """Save scan results to JSON AND generate detailed review report"""
        try:
            SIGNALS_DIR.mkdir(parents=True, exist_ok=True)

            # Save JSON results
            results = {
                'timestamp': datetime.now().isoformat(),
                'scan_config': {
                    'tier': self.config['scanning']['strategy']['tier'],
                    'symbols_scanned': len(self.universe)
                },
                'opportunities': self.opportunities,
                'portfolio_status': self.portfolio_status
            }

            import json
            output_file = SIGNALS_DIR / 'master_scan_results.json'
            with open(output_file, 'w') as f:
                json.dump(results, f, indent=2)

            print(f"💾 Results saved: {output_file}")

            # Generate detailed review report
            self._generate_review_report()

            # Generate comprehensive fallers report (ALL 2%+ drops)
            self._generate_all_fallers_report()

        except Exception as e:
            print(f"⚠️  Save failed: {e}")

    def _generate_review_report(self):
        """
        Generate detailed DAILY REVIEW REPORT
        Explains WHY each symbol was selected with full reasoning
        Creates TWO reports:
        1. Full table of ALL scanned symbols (for quick review)
        2. Detailed analysis of top opportunities
        """
        try:
            # Report 1: Full scan table (ALL symbols)
            self._generate_full_scan_table()

            # Report 2: Detailed top opportunities
            report_file = SIGNALS_DIR / f'daily_review_{datetime.now().strftime("%Y%m%d")}.md'

            with open(report_file, 'w') as f:
                # Header
                f.write("# 📊 DAILY MARKET SCAN - DETAILED REVIEW REPORT\n\n")
                f.write(f"**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M ET')}\n\n")
                f.write("---\n\n")

                # Scan Summary
                f.write("## 📈 Scan Summary\n\n")
                f.write(f"- **Symbols Scanned**: {len(self.universe)}\n")
                f.write(f"- **Scan Tier**: {self.config['scanning']['strategy']['tier'].upper()}\n")
                f.write(f"- **Opportunities Found**: {len(self.opportunities)}\n")
                f.write(f"- **Minimum Confidence**: {self.config['scoring']['min_confidence']}\n\n")

                # Scoring Methodology
                f.write("## 🎯 Scoring Methodology\n\n")
                weights = self.config['scoring']['weights']
                f.write("Multi-signal composite scoring (0-100):\n\n")
                f.write(f"- **News Sentiment**: {weights['news_sentiment']}% (FinBERT AI analysis)\n")
                f.write(f"- **Technical Analysis**: {weights['technical']}% (RSI, MACD, trends, volume)\n")
                f.write(f"- **Fundamentals**: {weights['fundamentals']}% (P/E, margins, growth, ratings)\n")
                f.write(f"- **Insider Activity**: {weights['insider_activity']}% (Smart money tracking)\n")
                f.write(f"- **Strategy Confirmation**: Bonus +10 points if strategies align\n\n")

                f.write("---\n\n")

                # Detailed Opportunity Analysis
                f.write("## 🚀 TOP OPPORTUNITIES - DETAILED ANALYSIS\n\n")

                for i, opp in enumerate(self.opportunities, 1):
                    f.write(f"### {i}. {opp['symbol']} - {opp['recommendation']}\n\n")

                    # Overall Score
                    f.write(f"**Composite Score**: {opp['composite_score']:.1f}/100\n")
                    f.write(f"**Confidence**: {opp['confidence']:.1f} ({self._get_confidence_level(opp['confidence'])})\n\n")

                    # Trade Setup
                    trade = opp['trade_setup']
                    f.write("#### 💰 Trade Setup\n\n")
                    f.write(f"- **Entry Price**: ${trade['entry']:.2f}\n")
                    f.write(f"- **Stop Loss**: ${trade['stop_loss']:.2f} ({((trade['stop_loss']-trade['entry'])/trade['entry']*100):.1f}%)\n")
                    f.write(f"- **Target Price**: ${trade['target']:.2f} ({((trade['target']-trade['entry'])/trade['entry']*100):.1f}%)\n")
                    f.write(f"- **Risk/Reward Ratio**: {trade['risk_reward']:.2f}:1\n\n")

                    # Score Breakdown
                    scores = opp['scores']
                    f.write("#### 📊 Score Breakdown\n\n")
                    f.write(f"| Signal | Score | Weight | Contribution |\n")
                    f.write(f"|--------|-------|--------|-------------|\n")
                    f.write(f"| News Sentiment | {scores['news']:.0f}/100 | {weights['news_sentiment']}% | {scores['news']*weights['news_sentiment']/100:.1f} |\n")
                    f.write(f"| Technical Analysis | {scores['technical']:.0f}/100 | {weights['technical']}% | {scores['technical']*weights['technical']/100:.1f} |\n")
                    f.write(f"| Fundamentals | {scores['fundamentals']:.0f}/100 | {weights['fundamentals']}% | {scores['fundamentals']*weights['fundamentals']/100:.1f} |\n")
                    f.write(f"| Insider Activity | {scores['insider']:.0f}/100 | {weights['insider_activity']}% | {scores['insider']*weights['insider_activity']/100:.1f} |\n\n")

                    # Strategy Signals
                    if opp.get('strategy_signals'):
                        f.write("#### 🎯 Strategy Confirmation\n\n")
                        f.write(f"**{len(opp['strategy_signals'])} strategies confirmed this opportunity:**\n\n")
                        for sig in opp['strategy_signals']:
                            f.write(f"- ✅ **{sig['strategy']}**: {sig['signal']} ({sig['confidence']} confidence)\n")
                            if sig.get('details'):
                                f.write(f"  - {sig['details']}\n")
                        f.write("\n")

                    # Reasons (Why Buy)
                    if opp.get('reasons'):
                        f.write("#### 💡 Why This Is An Opportunity\n\n")
                        for reason in opp['reasons']:
                            f.write(f"- ✓ {reason}\n")
                        f.write("\n")

                    # Detailed Analysis
                    f.write("#### 🔍 Detailed Signal Analysis\n\n")

                    # News Sentiment Details
                    f.write(f"**News Sentiment ({scores['news']:.0f}/100)**\n")
                    if scores['news'] > 70:
                        f.write("- Strong positive sentiment or identified buying opportunity from dip\n")
                        f.write("- AI analysis shows favorable risk/reward\n")
                    elif scores['news'] > 50:
                        f.write("- Neutral to positive sentiment\n")
                        f.write("- No major red flags detected\n")
                    else:
                        f.write("- Neutral news environment\n")
                    f.write("\n")

                    # Technical Details
                    f.write(f"**Technical Analysis ({scores['technical']:.0f}/100)**\n")
                    if scores['technical'] > 70:
                        f.write("- Strong technical setup\n")
                        f.write("- Oversold conditions (RSI < 40) or bullish momentum\n")
                        f.write("- Volume confirming price action\n")
                    elif scores['technical'] > 50:
                        f.write("- Moderate technical setup\n")
                        f.write("- Some positive indicators present\n")
                    else:
                        f.write("- Neutral technical picture\n")
                    f.write("\n")

                    # Fundamental Details
                    f.write(f"**Fundamentals ({scores['fundamentals']:.0f}/100)**\n")
                    if scores['fundamentals'] > 70:
                        f.write("- Strong fundamental quality\n")
                        f.write("- Reasonable valuation (P/E), good margins, growth\n")
                        f.write("- Positive analyst sentiment\n")
                    elif scores['fundamentals'] > 50:
                        f.write("- Acceptable fundamental quality\n")
                        f.write("- Company is financially sound\n")
                    else:
                        f.write("- Neutral fundamentals\n")
                    f.write("\n")

                    # Insider Details
                    f.write(f"**Insider Activity ({scores['insider']:.0f}/100)**\n")
                    if scores['insider'] > 70:
                        f.write("- **Smart money is buying!**\n")
                        f.write("- Recent insider purchases detected\n")
                        f.write("- Corporate insiders see value at current price\n")
                    elif scores['insider'] < 40:
                        f.write("- Recent insider selling detected\n")
                        f.write("- Exercise caution\n")
                    else:
                        f.write("- No significant insider activity\n")
                    f.write("\n")

                    f.write("---\n\n")

                # Portfolio Status (if any)
                if self.portfolio_status:
                    f.write("## ⚖️ Portfolio Review\n\n")
                    for symbol, status in self.portfolio_status.items():
                        f.write(f"### {symbol}\n\n")
                        f.write(f"- **Status**: {'✅ Healthy' if status['healthy'] else '⚠️ Needs Attention'}\n")
                        f.write(f"- {status['message']}\n\n")

                # Footer
                f.write("---\n\n")
                f.write("## 📝 How to Use This Report\n\n")
                f.write("1. **Review Each Opportunity**: Read the detailed analysis above\n")
                f.write("2. **Check Your Risk Tolerance**: Compare scores and R/R ratios\n")
                f.write("3. **Verify Strategy Confirmation**: Multiple strategies = higher confidence\n")
                f.write("4. **Do Your Own Research**: This is analysis, not financial advice\n")
                f.write("5. **Set Your Orders**: Use the provided entry, stop, and target prices\n\n")

                f.write("**Disclaimer**: This is an automated analysis tool. Always do your own research and never invest more than you can afford to lose.\n\n")
                f.write(f"*Report generated by Master Scanner v1.0 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")

            print(f"📋 Review report saved: {report_file}")

        except Exception as e:
            print(f"⚠️  Report generation failed: {e}")

    def _get_confidence_level(self, score: float) -> str:
        """Get confidence level text"""
        if score >= 80:
            return "HIGH - Strong conviction trade"
        elif score >= 60:
            return "MEDIUM - Moderate conviction"
        else:
            return "LOW - Proceed with caution"

    def _generate_all_fallers_report(self):
        """
        Generate comprehensive report of ALL symbols that fell 2%+ today
        Includes both stocks and ETFs
        Sorted by percentage drop (worst first)
        """
        try:
            if not hasattr(self, 'all_fallers') or not self.all_fallers:
                print("  ℹ️  No fallers (2%+) found to report")
                return

            fallers_file = SIGNALS_DIR / f'all_fallers_{datetime.now().strftime("%Y%m%d")}.md'

            # Sort by percentage drop (worst first)
            sorted_fallers = sorted(self.all_fallers, key=lambda x: x['pct_change'])

            with open(fallers_file, 'w') as f:
                # Header
                f.write("# 📉 ALL MARKET FALLERS - 2%+ Drops\n\n")
                f.write(f"**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M ET')}\n")
                f.write(f"**Total Fallers**: {len(sorted_fallers)}\n")
                f.write(f"**Stocks**: {sum(1 for x in sorted_fallers if x['type'] == 'Stock')}\n")
                f.write(f"**ETFs**: {sum(1 for x in sorted_fallers if x['type'] == 'ETF')}\n\n")

                f.write("---\n\n")

                f.write("## 📊 COMPLETE LIST (Sortable)\n\n")
                f.write("**Click column headers to sort on GitHub!**\n\n")

                # Table Header
                f.write("| Rank | Symbol | Type | Drop % | Price | Volume | Avg Volume | Vol Ratio |\n")
                f.write("|------|--------|------|--------|-------|--------|------------|----------|\n")

                # Table Rows
                for i, faller in enumerate(sorted_fallers, 1):
                    symbol = faller['symbol']
                    asset_type = faller['type']
                    pct = f"{faller['pct_change']:.2f}%"
                    price = f"${faller['price']:.2f}"
                    volume = f"{faller['volume']:,.0f}"
                    avg_vol = f"{faller['avg_volume']:,.0f}"
                    vol_ratio = f"{faller['volume_ratio']:.2f}x"

                    f.write(f"| {i} | **{symbol}** | {asset_type} | {pct} | {price} | {volume} | {avg_vol} | {vol_ratio} |\n")

                f.write("\n---\n\n")

                # Statistics
                f.write("## 📈 Statistics\n\n")

                # Worst fallers
                f.write("### 🔴 Top 10 Worst Fallers\n\n")
                for i, faller in enumerate(sorted_fallers[:10], 1):
                    f.write(f"{i}. **{faller['symbol']}** ({faller['type']}): {faller['pct_change']:.2f}%\n")

                f.write("\n### 📊 Drop Distribution\n\n")
                drops_2_5 = sum(1 for x in sorted_fallers if -5 < x['pct_change'] <= -2)
                drops_5_10 = sum(1 for x in sorted_fallers if -10 < x['pct_change'] <= -5)
                drops_10_plus = sum(1 for x in sorted_fallers if x['pct_change'] <= -10)

                f.write(f"- **2-5% drops**: {drops_2_5} symbols\n")
                f.write(f"- **5-10% drops**: {drops_5_10} symbols\n")
                f.write(f"- **10%+ drops**: {drops_10_plus} symbols\n\n")

                f.write("---\n\n")
                f.write("*This report shows ALL symbols that fell 2% or more today.*\n")
                f.write("*For detailed analysis of top opportunities, see `daily_review_YYYYMMDD.md`*\n")

            print(f"📉 All fallers report saved: {fallers_file}")

        except Exception as e:
            print(f"⚠️  Failed to generate all fallers report: {e}")

    def _generate_full_scan_table(self):
        """
        Generate FULL SCAN TABLE with ALL analyzed symbols
        Single sortable table for quick review on GitHub
        """
        try:
            table_file = SIGNALS_DIR / f'full_scan_{datetime.now().strftime("%Y%m%d")}.md'

            # Collect ALL opportunities (even ones below threshold for full transparency)
            all_results = []

            # The opportunities list already has the best ones
            # But we want to show ALL symbols that were analyzed
            # For now, we'll show the opportunities we found + note about screened symbols

            with open(table_file, 'w') as f:
                # Header
                f.write("# 📊 FULL MARKET SCAN - ALL SYMBOLS\n\n")
                f.write(f"**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M ET')}\n")
                f.write(f"**Symbols Scanned**: {len(self.universe)}\n")
                f.write(f"**Passed Pre-Screening**: {len(self.opportunities) if hasattr(self, 'candidates_count') else 'N/A'}\n")
                f.write(f"**Met Confidence Threshold**: {len(self.opportunities)}\n\n")

                f.write("---\n\n")

                f.write("## 🎯 QUICK REFERENCE TABLE\n\n")
                f.write("**Sort by any column on GitHub to find what interests you!**\n\n")

                # Table Header
                f.write("| Rank | Symbol | Score | Confidence | Recommendation | Entry | Stop | Target | R/R | News | Tech | Fund | Insider | Strategies | Why |\n")
                f.write("|------|--------|-------|------------|----------------|-------|------|--------|-----|------|------|------|---------|------------|-----|\n")

                # Table Rows - All opportunities
                for i, opp in enumerate(self.opportunities, 1):
                    symbol = opp['symbol']
                    score = opp['composite_score']
                    conf = self._get_confidence_badge(opp['confidence'])
                    rec = self._get_recommendation_badge(opp['recommendation'])

                    trade = opp['trade_setup']
                    entry = f"${trade['entry']:.2f}"
                    stop = f"${trade['stop_loss']:.2f}"
                    target = f"${trade['target']:.2f}"
                    rr = f"{trade['risk_reward']:.1f}"

                    scores = opp['scores']
                    news = f"{scores['news']:.0f}"
                    tech = f"{scores['technical']:.0f}"
                    fund = f"{scores['fundamentals']:.0f}"
                    insider = f"{scores['insider']:.0f}"

                    # Strategy count
                    strategies = len(opp.get('strategy_signals', []))
                    strat_text = f"{strategies} ✓" if strategies > 0 else "-"

                    # Reasons (truncated)
                    reasons = opp.get('reasons', [])
                    why = ", ".join(reasons[:2]) if reasons else "Multi-signal opportunity"
                    if len(reasons) > 2:
                        why += "..."

                    f.write(f"| {i} | **{symbol}** | {score:.1f} | {conf} | {rec} | {entry} | {stop} | {target} | {rr} | {news} | {tech} | {fund} | {insider} | {strat_text} | {why} |\n")

                f.write("\n---\n\n")

                # Legend
                f.write("## 📖 Column Definitions\n\n")
                f.write("- **Rank**: Ranked by composite score (higher = better)\n")
                f.write("- **Score**: Composite score (0-100) combining all signals\n")
                f.write("- **Confidence**: HIGH (80+), MEDIUM (60-79), LOW (<60)\n")
                f.write("- **Recommendation**: STRONG BUY (85+), BUY (70+), WATCH (55+), SKIP (<55)\n")
                f.write("- **Entry**: Recommended entry price\n")
                f.write("- **Stop**: Stop loss price (risk management)\n")
                f.write("- **Target**: Target price (profit taking)\n")
                f.write("- **R/R**: Risk/Reward ratio (target/risk)\n")
                f.write("- **News**: News sentiment score (0-100)\n")
                f.write("- **Tech**: Technical analysis score (0-100)\n")
                f.write("- **Fund**: Fundamental analysis score (0-100)\n")
                f.write("- **Insider**: Insider activity score (0-100)\n")
                f.write("- **Strategies**: Number of trading strategies confirming\n")
                f.write("- **Why**: Brief summary of opportunity\n\n")

                # How to use on GitHub
                f.write("## 💡 How to Use This Table on GitHub\n\n")
                f.write("1. **Click any column header** to sort by that column\n")
                f.write("2. **Sort by Score** - See highest scoring opportunities first\n")
                f.write("3. **Sort by R/R** - Find best risk/reward ratios\n")
                f.write("4. **Sort by Tech** - Find best technical setups\n")
                f.write("5. **Sort by Strategies** - Find multi-strategy confirmations\n")
                f.write("6. **Filter by Confidence** - Look for HIGH badges\n\n")

                # Pre-screening info
                f.write("## 🔍 Pre-Screening Results\n\n")
                f.write(f"**Total Universe**: {len(self.universe)} symbols from Finnhub API\n\n")
                f.write("**Pre-Screening Criteria**:\n")
                f.write("- ✓ Price drop 3-10% (opportunity zone)\n")
                f.write("- ✓ Volume spike 1.2x+ (activity)\n")
                f.write("- ✓ Price > $5 (no penny stocks)\n")
                f.write("- ✓ Volume > 500K (liquidity)\n")
                f.write("- ✓ Drop < 20% (not crashing)\n\n")

                f.write(f"**Result**: {len(self.opportunities)} symbols passed pre-screening and met confidence threshold ({self.config['scoring']['min_confidence']}+)\n\n")

                # Footer
                f.write("---\n\n")
                f.write(f"*Table generated by Master Scanner v1.0 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")
                f.write("\n**Disclaimer**: Automated analysis tool. Do your own research.\n")

            print(f"📊 Full scan table saved: {table_file}")
            print(f"   View on GitHub for sortable columns!")

        except Exception as e:
            print(f"⚠️  Table generation failed: {e}")

    def _get_confidence_badge(self, score: float) -> str:
        """Get confidence badge for table"""
        if score >= 80:
            return "🟢 HIGH"
        elif score >= 60:
            return "🟡 MED"
        else:
            return "🔴 LOW"

    def _get_recommendation_badge(self, rec: str) -> str:
        """Get recommendation badge for table"""
        if rec == "STRONG BUY":
            return "🚀 STRONG BUY"
        elif rec == "BUY":
            return "✅ BUY"
        elif rec == "WATCH":
            return "👀 WATCH"
        else:
            return "⏸️ SKIP"

    def _generate_opportunity_charts(self):
        """
        Generate visual analysis charts for top opportunities.
        Creates comprehensive charts showing:
        - Price action with candlesticks
        - Entry/Stop/Target zones
        - Technical indicators (RSI, MACD, Volume)
        - ABC patterns if detected
        - Support/Resistance levels
        - Intraday buy signals
        """
        try:
            if not self.opportunities:
                print("  ℹ️  No opportunities to chart")
                return

            # Import chart generator
            from src.opportunity_chart_generator import OpportunityChartGenerator

            generator = OpportunityChartGenerator()

            # Generate charts for top opportunities (max 10)
            top_opportunities = self.opportunities[:10]

            print(f"\n📊 GENERATING OPPORTUNITY CHARTS")
            print(f"   Creating charts for top {len(top_opportunities)} opportunities...")

            chart_count = 0
            failed_count = 0

            for opp in tqdm(top_opportunities, desc="     Charts", unit="chart", ncols=100):
                try:
                    symbol = opp['symbol']

                    # Determine asset type (check if it's in ETF or stock folder)
                    asset_type = 'stock'  # Default
                    for sym_dict in self.universe:
                        if isinstance(sym_dict, dict) and sym_dict.get('symbol') == symbol:
                            asset_type = sym_dict.get('type', 'stock').lower()
                            break

                    # Load CSV data
                    df = self._load_price_data(symbol)
                    if df is None or len(df) < 20:
                        failed_count += 1
                        continue

                    # Prepare opportunity data for chart
                    opportunity_data = {
                        'composite_score': opp.get('composite_score', 0),
                        'confidence': opp.get('confidence', 'UNKNOWN'),
                        'risk_reward_ratio': opp.get('risk_reward', 0),
                        'entry_price': opp.get('current_price', 0),  # Use current price as entry
                        'stop_loss': opp.get('stop_loss'),
                        'target_price': opp.get('target_price')
                    }

                    # Generate chart with asset type for proper folder organization
                    chart_path = generator.generate_opportunity_chart(
                        symbol, df, opportunity_data,
                        asset_type=asset_type,
                        lookback_days=60
                    )

                    chart_count += 1

                except Exception as e:
                    failed_count += 1
                    # Silent fail for individual charts
                    pass

            print(f"   ✅ Generated {chart_count} charts")
            if failed_count > 0:
                print(f"   ⚠️  Failed: {failed_count} charts")
            print(f"   📁 Charts saved in:")
            print(f"      - charts/stocks/ (stock opportunities)")
            print(f"      - charts/etfs/ (ETF opportunities)")

        except Exception as e:
            print(f"⚠️  Chart generation failed: {e}")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Master Daily Market Scanner')
    parser.add_argument('--mode', type=str, default='daily',
                       choices=['daily', 'premarket', 'intraday'],
                       help='Scan mode: daily (after close), premarket (before open), intraday (during hours)')
    parser.add_argument('--config', type=str, default=None,
                       help='Path to config file (default: config/master_config.yaml)')

    args = parser.parse_args()

    config_path = Path(args.config) if args.config else CONFIG_FILE

    scanner = MasterScanner(config_path)
    scanner.run(mode=args.mode)


if __name__ == '__main__':
    main()
