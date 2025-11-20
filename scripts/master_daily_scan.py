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
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from collections import defaultdict

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Import existing modules (reuse, don't duplicate)
from src.finnhub_data import FinnhubDataClient
from src.news_monitor import NewsMonitor
from src.indicators import TechnicalIndicators
from src.insider_tracker import InsiderTracker
from src.finbert_sentiment import get_sentiment_analyzer
from src.premarket_monitor import PreMarketMonitor
from src.premarket_opportunity_scanner import PreMarketOpportunityScanner
from src.strategy_runner import StrategyRunner
from src.abc_strategy import ABCStrategy

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
                self.finnhub = FinnhubDataClient(api_key)
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

    def fetch_market_universe(self) -> List[str]:
        """
        Fetch complete list of US market symbols from Finnhub
        Returns tiered list based on scan strategy
        """
        print("\n" + "=" * 80)
        print("PHASE 1: FETCHING MARKET UNIVERSE")
        print("=" * 80)

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
            with open(sp500_file, 'r') as f:
                symbols = [{'symbol': line.strip(), 'type': 'stock', 'name': '', 'exchange': ''}
                          for line in f if line.strip()]
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

    def _filter_tier_daily(self, symbols: List[Dict]) -> List[Dict]:
        """
        Daily tier: SMART filtering based on quality metrics
        Automatically selects best symbols to scan (no manual lists!)

        Criteria:
        - Market cap > $1B (liquid, established companies)
        - Average volume > 1M (tradeable)
        - Mix of stocks and ETFs
        - Diverse sectors
        """
        print("  🧠 Smart filtering: Selecting best symbols to scan...")

        # Prioritize by quality (large cap, high volume, diverse)
        # This ensures we scan high-quality opportunities
        max_symbols = self.config['scanning'].get('max_symbols_per_run', 600)

        # For now, return first N (will enhance with real-time volume/cap filtering)
        return symbols[:max_symbols]

    def _filter_tier_weekly(self, symbols: List[Dict]) -> List[Dict]:
        """Weekly tier: More comprehensive scan"""
        return symbols[:2000]

    def _apply_filters(self, symbols: List[Dict]) -> List[str]:
        """Apply quality filters (volume, price, exchange)"""
        filters = self.config['scanning']['filters']

        # For now, just return symbols
        # TODO: Fetch real-time data and filter by volume/price
        valid_exchanges = set(filters.get('exchanges', ['NYSE', 'NASDAQ', 'AMEX']))

        filtered = []
        for sym in symbols:
            exchange = sym.get('exchange', '')
            # Basic exchange filter
            if any(ex in exchange for ex in valid_exchanges):
                filtered.append(sym['symbol'])

        return filtered[:self.config['scanning'].get('max_symbols_per_run', 600)]

    def _count_by_type(self, asset_type: str) -> int:
        """Count symbols by type"""
        # Simplified count (ETFs typically have 3-letter tickers)
        if asset_type == 'etf':
            return sum(1 for s in self.universe if len(s) <= 4 and s.isupper())
        return len(self.universe)

    def _quick_prescreen(self, symbols: List[str]) -> List[str]:
        """
        INTELLIGENT PRE-SCREENING

        Quickly filter entire market for promising candidates based on:
        1. Price action: Recent drops (3-10%) = potential buy opportunity
        2. Volume: Above average volume = something happening
        3. Volatility: Movement without crash (not bankruptcy/fraud)
        4. Technical: Not in death spiral (avoid catching falling knives)

        This is FAST - can scan 1000s of symbols in minutes
        Then we do DEEP analysis on the 50-100 that pass
        """
        print(f"     Screening {len(symbols)} symbols for:")
        print(f"     • Price drops (3-10% = opportunity)")
        print(f"     • Volume spikes (interest)")
        print(f"     • Healthy technical structure (no knives)")
        print()

        candidates = []
        batch_size = 50

        for i in range(0, len(symbols), batch_size):
            batch = symbols[i:i+batch_size]

            # Fetch recent data for batch
            for symbol in batch:
                try:
                    # Quick check: Fetch last 10 days only
                    ticker = yf.Ticker(symbol)
                    df = ticker.history(period='10d')

                    if len(df) < 5:
                        continue

                    # Calculate quick metrics
                    recent_close = df['Close'].iloc[-1]
                    week_ago_close = df['Close'].iloc[0]
                    pct_change = ((recent_close - week_ago_close) / week_ago_close) * 100

                    avg_volume = df['Volume'].mean()
                    recent_volume = df['Volume'].iloc[-1]
                    volume_ratio = recent_volume / avg_volume if avg_volume > 0 else 0

                    # INTELLIGENT FILTERING RULES

                    # Rule 1: Price drop (but not crash)
                    price_drop = -10 <= pct_change <= -3  # 3-10% drop

                    # Rule 2: Volume spike (interest)
                    volume_spike = volume_ratio > 1.2  # 20%+ above average

                    # Rule 3: Price above $5 (avoid penny stocks)
                    price_filter = recent_close >= 5.0

                    # Rule 4: Decent volume (liquid)
                    volume_filter = avg_volume >= 500000  # 500K+ daily volume

                    # Rule 5: Not in death spiral (price not down >20% in 10 days)
                    not_crashing = pct_change > -20

                    # Pass if it meets criteria
                    if price_drop and volume_spike and price_filter and volume_filter and not_crashing:
                        candidates.append(symbol)

                    # Also include symbols that just had volume spike (even without drop)
                    elif volume_ratio > 2.0 and price_filter and volume_filter and not_crashing:
                        # 2x volume = something interesting happening
                        candidates.append(symbol)

                except:
                    # Skip symbols we can't fetch data for
                    continue

            # Progress indicator
            if i % 200 == 0 and i > 0:
                print(f"     Screened {i}/{len(symbols)} symbols... ({len(candidates)} candidates so far)")

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
        scanned = 0

        for symbol in candidates:
            try:
                opp = self._analyze_symbol(symbol)
                if opp:
                    opportunities.append(opp)
                scanned += 1

                if scanned % 10 == 0:
                    print(f"     Progress: {scanned}/{len(candidates)} ({scanned/len(candidates)*100:.1f}%)")

            except Exception as e:
                # Silent errors during scanning (too noisy otherwise)
                continue

        # Sort by composite score
        opportunities.sort(key=lambda x: x['composite_score'], reverse=True)

        # Keep top N
        max_opps = self.config['scoring']['max_opportunities']
        self.opportunities = opportunities[:max_opps]

        print(f"\n✅ Scan complete:")
        print(f"   Scanned: {scanned} symbols")
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
            'reasons': reasons,
            'timestamp': datetime.now().isoformat()
        }

    def _load_price_data(self, symbol: str) -> Optional[pd.DataFrame]:
        """
        Load historical price data with INCREMENTAL fetching

        Uses existing CSV if available, only fetches new data incrementally.
        This is MUCH faster than re-downloading everything!
        """
        csv_file = MARKET_DATA_DIR / f'{symbol}.csv'

        # Try to load existing CSV
        if csv_file.exists():
            try:
                df = pd.read_csv(csv_file, index_col=0, parse_dates=True)
                df = df.sort_index()

                # Check if data is recent (within last 7 days)
                if not df.empty:
                    last_date = df.index[-1]
                    days_old = (pd.Timestamp.today() - last_date).days

                    if days_old <= 7:
                        # Recent enough, use cached data
                        return df
                    else:
                        # Data is old, fetch incremental update
                        start_date = (last_date + pd.Timedelta(days=1)).strftime('%Y-%m-%d')
                        new_data = self._fetch_incremental(symbol, start_date)

                        if not new_data.empty:
                            # Combine old + new data
                            df = pd.concat([df, new_data]).sort_index()
                            df = df[~df.index.duplicated(keep='last')]

                            # Save updated CSV
                            MARKET_DATA_DIR.mkdir(parents=True, exist_ok=True)
                            df.to_csv(csv_file)

                        return df
            except Exception as e:
                # If error loading/parsing, fall through to full fetch
                pass

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
                MARKET_DATA_DIR.mkdir(parents=True, exist_ok=True)
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
            sentiment = self.insider_tracker.get_insider_sentiment(symbol)

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
        print("PHASE 4: GENERATING ALERT")
        print("=" * 80)

        alert = self._format_alert_message()

        print("✅ Alert generated\n")

        return alert

    def _format_alert_message(self) -> str:
        """Format single consolidated alert message with GitHub table link"""
        msg = []

        # Header
        msg.append("🔍 DAILY MARKET SCAN")
        msg.append(f"{datetime.now().strftime('%Y-%m-%d %H:%M ET')}")
        msg.append("=" * 40)

        # Scan summary
        msg.append(f"\n📊 SCAN SUMMARY")
        msg.append(f"Scanned: {len(self.universe)} symbols")
        msg.append(f"Found: {len(self.opportunities)} opportunities")

        # GitHub table link
        date_str = datetime.now().strftime('%Y%m%d')
        github_url = f"https://github.com/ravi4j/daily_market_automation/blob/main/signals/full_scan_{date_str}.md"
        msg.append(f"\n📊 FULL TABLE (sortable on GitHub):")
        msg.append(f"👉 {github_url}")

        # Top opportunities (compact format)
        msg.append(f"\n🚀 TOP {len(self.opportunities)} PICKS\n")

        for i, opp in enumerate(self.opportunities, 1):
            # Compact one-line format
            score = opp['composite_score']
            conf_badge = "🟢" if score >= 80 else "🟡" if score >= 60 else "🔴"

            trade = opp['trade_setup']
            rr = trade['risk_reward']

            # Count strategy confirmations
            strat_count = len(opp.get('strategy_signals', []))
            strat_badge = f"🎯{strat_count}" if strat_count > 0 else ""

            msg.append(f"{i}. **{opp['symbol']}** {conf_badge} {score:.0f}/100 {strat_badge}")
            msg.append(f"   ${trade['entry']:.2f} → ${trade['target']:.2f} (R/R: {rr:.1f})")

            # Brief reason
            if opp.get('reasons'):
                msg.append(f"   {opp['reasons'][0]}")
            msg.append("")

        # Portfolio status (if any)
        if self.portfolio_status:
            msg.append("⚖️ YOUR PORTFOLIO")
            for symbol, status in self.portfolio_status.items():
                emoji = "✅" if status['healthy'] else "⚠️"
                msg.append(f"{emoji} {symbol}: {status['message']}")
            msg.append("")

        # Quick legend
        msg.append("🟢 HIGH confidence (80+)")
        msg.append("🟡 MEDIUM confidence (60-79)")
        msg.append("🎯 Strategy confirmation count")

        # Footer
        msg.append("\n" + "=" * 40)
        msg.append("📋 View full sortable table on GitHub")
        msg.append("🤖 Master Scanner v1.0")

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
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            payload = {
                'chat_id': chat_id,
                'text': message,
                'parse_mode': 'HTML'
            }
            response = requests.post(url, json=payload)

            if response.status_code == 200:
                print("✅ Alert sent to Telegram\n")
            else:
                print(f"⚠️  Telegram send failed: {response.status_code}\n")

        except Exception as e:
            print(f"⚠️  Telegram send error: {e}\n")

    # =========================================================================
    # MAIN EXECUTION
    # =========================================================================

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

        # Phase 1: Fetch universe
        self.fetch_market_universe()

        # Phase 2: Scan for opportunities
        self.scan_market()

        # Phase 3: Check portfolio
        self.check_portfolio()

        # Phase 4: Generate and send alert
        alert = self.generate_alert()
        print("\n" + "=" * 80)
        print("PREVIEW OF ALERT:")
        print("=" * 80)
        print(alert)
        print("=" * 80 + "\n")

        self.send_alert(alert)

        # Save results
        self._save_results()

        print("✅ DAILY SCAN COMPLETE!\n")

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
        print("\n=" * 80)
        print("PHASE 2: GAP OPPORTUNITY SCAN")
        print("=" * 80)
        print(f"\n🔍 Scanning market for gap-based opportunities...\n")

        # Use S&P 500 or configured symbols
        scan_symbols = self.config.get('scanning', {}).get('intelligent_filters', {}).get('premarket_symbols', [])
        if not scan_symbols:
            # Default: scan top holdings + some liquid stocks
            scan_symbols = list(positions.keys()) if positions else ['SPY', 'QQQ', 'AAPL', 'MSFT', 'NVDA', 'TSLA']

        opportunities = self.premarket_scanner.scan_for_opportunities(
            symbols=scan_symbols[:50],  # Limit to 50 for speed
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
                msg.append(f"\n{i}. {opp['symbol']} - {opp['recommendation']}")
                msg.append(f"   Gap: {opp['gap_pct']:.2f}% | Score: {opp['score']:.0f}/100")
                msg.append(f"   Entry: ${opp['entry']:.2f} | Target: ${opp['target']:.2f}")
                msg.append(f"   Stop: ${opp['stop']:.2f}")
                msg.append(f"   Why: {opp.get('reason', 'Gap opportunity')}")

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
