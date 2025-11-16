#!/usr/bin/env python3
"""
Auto-Add to Portfolio
Automatically trigger on-demand analysis for high-score opportunities
"""

import os
import sys
import json
import yaml
import time
from datetime import datetime, timedelta
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.analyze_symbol import analyze_symbol
from scripts.send_analysis_to_telegram import send_analysis
from scripts.add_symbol_to_config import add_symbol_to_config
from scripts.fetch_symbol_data import fetch_symbol_data


def load_config():
    """Load auto-analysis configuration"""
    config_path = PROJECT_ROOT / "config" / "auto_analysis.yaml"

    if not config_path.exists():
        print(f"⚠️  Config not found: {config_path}")
        print("Using default configuration")
        return {
            'auto_analysis': {
                'enabled': True,
                'min_score': 80,
                'max_per_scan': 5,
                'strategies': ['rsi_macd', 'trend_following', 'abc_patterns'],
                'auto_add_to_portfolio': False,
                'min_confidence_for_add': 'HIGH',
                'send_telegram_report': True,
                'cooldown_hours': 24,
                'priority_sectors': []
            }
        }

    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def load_opportunities():
    """Load opportunities from news scanner and S&P 500 scanner"""
    opportunities = []

    # Load from news scanner (portfolio)
    news_file = PROJECT_ROOT / "signals" / "news_opportunities.json"
    if news_file.exists():
        with open(news_file, 'r') as f:
            data = json.load(f)
            if 'opportunities' in data:
                for opp in data['opportunities']:
                    opp['source'] = 'portfolio_news'
                    opportunities.append(opp)

    # Load from S&P 500 scanner
    sp500_file = PROJECT_ROOT / "signals" / "sp500_opportunities.json"
    if sp500_file.exists():
        with open(sp500_file, 'r') as f:
            data = json.load(f)
            if 'opportunities' in data:
                for opp in data['opportunities']:
                    opp['source'] = 'sp500_scan'
                    opportunities.append(opp)

    return opportunities


def load_cooldown_cache():
    """Load cache of recently analyzed symbols"""
    cache_file = PROJECT_ROOT / "data" / "cache" / "auto_analysis_cache.json"

    if not cache_file.exists():
        return {}

    try:
        with open(cache_file, 'r') as f:
            return json.load(f)
    except:
        return {}


def save_cooldown_cache(cache):
    """Save cache of analyzed symbols"""
    cache_file = PROJECT_ROOT / "data" / "cache" / "auto_analysis_cache.json"
    cache_file.parent.mkdir(parents=True, exist_ok=True)

    with open(cache_file, 'w') as f:
        json.dump(cache, f, indent=2)


def is_in_cooldown(symbol, cache, cooldown_hours):
    """Check if symbol is in cooldown period"""
    if symbol not in cache:
        return False

    last_analyzed = datetime.fromisoformat(cache[symbol]['last_analyzed'])
    cooldown_until = last_analyzed + timedelta(hours=cooldown_hours)

    return datetime.now() < cooldown_until


def filter_opportunities(opportunities, config, cache):
    """Filter opportunities based on configuration"""
    auto_config = config['auto_analysis']

    # Filter by minimum score
    min_score = auto_config['min_score']
    filtered = [opp for opp in opportunities if opp.get('score', 0) >= min_score]

    print(f"📊 Found {len(filtered)} opportunities with score >= {min_score}")

    # Filter by cooldown
    cooldown_hours = auto_config['cooldown_hours']
    filtered = [opp for opp in filtered
                if not is_in_cooldown(opp['symbol'], cache, cooldown_hours)]

    print(f"   {len(filtered)} are not in cooldown period")

    # Sort by score (highest first)
    filtered.sort(key=lambda x: x.get('score', 0), reverse=True)

    # Prioritize sectors if specified
    priority_sectors = auto_config.get('priority_sectors', [])
    if priority_sectors:
        priority = [opp for opp in filtered if opp.get('sector') in priority_sectors]
        others = [opp for opp in filtered if opp.get('sector') not in priority_sectors]
        filtered = priority + others

    # Limit to max_per_scan
    max_per_scan = auto_config['max_per_scan']
    filtered = filtered[:max_per_scan]

    print(f"   Top {len(filtered)} selected for analysis (max: {max_per_scan})")

    return filtered


def run_auto_analysis(opportunity, config, cache):
    """Run automated analysis for a single opportunity"""
    symbol = opportunity['symbol']
    score = opportunity.get('score', 0)
    source = opportunity.get('source', 'unknown')

    print(f"\n{'='*80}")
    print(f"📊 Analyzing {symbol} (Score: {score:.1f}/100, Source: {source})")
    print(f"{'='*80}")

    auto_config = config['auto_analysis']

    try:
        # Ensure CSV data exists
        print(f"\n1️⃣  Ensuring data is available...")
        csv_path = fetch_symbol_data(symbol, period='2y', force=False)

        if not csv_path:
            print(f"❌ Failed to fetch data for {symbol}")
            return False

        # Run technical analysis
        print(f"\n2️⃣  Running technical analysis...")
        analysis = analyze_symbol(symbol)

        if not analysis:
            print(f"❌ Failed to analyze {symbol}")
            return False

        # Combine with opportunity data
        analysis['opportunity_score'] = score
        analysis['opportunity_source'] = source
        analysis['news_sentiment'] = opportunity.get('sentiment', 'neutral')
        analysis['insider_activity'] = opportunity.get('insider_activity', 'none')

        # Save combined analysis
        output_dir = PROJECT_ROOT / "signals" / "auto_analysis"
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = output_dir / f"{symbol}_{timestamp}.json"

        with open(output_file, 'w') as f:
            json.dump(analysis, f, indent=2)

        print(f"✅ Analysis saved: {output_file.name}")

        # Send Telegram report
        if auto_config['send_telegram_report']:
            print(f"\n3️⃣  Sending Telegram report...")
            success = send_analysis(symbol, include_charts=True)
            if success:
                print(f"✅ Telegram report sent")
            else:
                print(f"⚠️  Failed to send Telegram report")

        # Auto-add to portfolio if conditions met
        if auto_config.get('auto_add_to_portfolio', False):
            min_confidence = auto_config.get('min_confidence_for_add', 'HIGH')

            # Check if any strategy has required confidence
            should_add = False
            for sig in analysis.get('signals', []):
                if sig.get('confidence', '') == min_confidence:
                    should_add = True
                    break

            if should_add:
                print(f"\n4️⃣  Auto-adding to portfolio...")
                added = add_symbol_to_config(symbol)
                if added:
                    print(f"✅ {symbol} added to config/symbols.yaml")
                else:
                    print(f"ℹ️  {symbol} already in portfolio")

        # Update cooldown cache
        cache[symbol] = {
            'last_analyzed': datetime.now().isoformat(),
            'score': score,
            'source': source
        }
        save_cooldown_cache(cache)

        print(f"\n✅ {symbol} analysis complete!")
        return True

    except Exception as e:
        print(f"❌ Error analyzing {symbol}: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main function"""
    print("="*80)
    print("🤖 AUTO-ADD TO PORTFOLIO")
    print("Automatically analyze high-score opportunities")
    print("="*80)
    print()

    # Load configuration
    print("📋 Loading configuration...")
    config = load_config()
    auto_config = config['auto_analysis']

    if not auto_config['enabled']:
        print("⚠️  Auto-analysis is DISABLED in config/auto_analysis.yaml")
        print("   Set 'enabled: true' to enable")
        return

    print(f"✅ Config loaded:")
    print(f"   - Min score: {auto_config['min_score']}")
    print(f"   - Max per scan: {auto_config['max_per_scan']}")
    print(f"   - Auto-add to portfolio: {auto_config.get('auto_add_to_portfolio', False)}")
    print(f"   - Cooldown: {auto_config['cooldown_hours']} hours")
    print()

    # Load opportunities
    print("📰 Loading opportunities...")
    opportunities = load_opportunities()

    if not opportunities:
        print("ℹ️  No opportunities found")
        print("   Run news scanner or S&P 500 scanner first")
        return

    print(f"✅ Found {len(opportunities)} total opportunities")
    print()

    # Load cooldown cache
    cache = load_cooldown_cache()

    # Filter opportunities
    print("🔍 Filtering opportunities...")
    to_analyze = filter_opportunities(opportunities, config, cache)

    if not to_analyze:
        print("\nℹ️  No opportunities meet criteria")
        print("   Either scores too low or symbols in cooldown")
        return

    print(f"\n✅ {len(to_analyze)} symbols selected for analysis:")
    for i, opp in enumerate(to_analyze, 1):
        print(f"   {i}. {opp['symbol']:6s} - Score: {opp.get('score', 0):.1f}/100 ({opp.get('source', 'unknown')})")

    # Run analysis for each
    print("\n" + "="*80)
    print("🚀 Starting automated analysis...")
    print("="*80)

    success_count = 0
    for opp in to_analyze:
        success = run_auto_analysis(opp, config, cache)
        if success:
            success_count += 1

        # Rate limiting - wait between analyses
        if opp != to_analyze[-1]:  # Not the last one
            print("\n⏳ Waiting 5 seconds before next analysis...")
            time.sleep(5)

    # Summary
    print("\n" + "="*80)
    print("📊 AUTO-ANALYSIS COMPLETE")
    print("="*80)
    print(f"✅ Analyzed: {success_count}/{len(to_analyze)} symbols")

    if success_count > 0:
        print(f"\n📁 Results saved to: signals/auto_analysis/")
        if auto_config['send_telegram_report']:
            print(f"📱 Telegram reports sent")
        if auto_config.get('auto_add_to_portfolio', False):
            print(f"📝 Check config/symbols.yaml for auto-added symbols")

    print("\n" + "="*80)


if __name__ == "__main__":
    main()
