#!/usr/bin/env python3
"""
On-demand symbol analysis script
Fetches data, calculates indicators, runs strategies
"""

import sys
import argparse
import json
from pathlib import Path
import yfinance as yf
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from indicators import TechnicalIndicators


def get_value(df_row, col_pattern: str, default=0):
    """Get value from row with case-insensitive column matching"""
    for col in df_row.index:
        if col_pattern.lower() in col.lower():
            val = df_row[col]
            return val if pd.notna(val) else default
    return default


def analyze_symbol(symbol: str, period: str = '1y') -> dict:
    """Run comprehensive analysis on a symbol"""
    
    print(f"📊 Analyzing {symbol}...")
    
    # Fetch data
    ticker = yf.Ticker(symbol)
    df = ticker.history(period=period)
    
    if df.empty:
        raise ValueError(f"No data found for {symbol}")
    
    # Ensure proper column names
    df.columns = df.columns.str.title()
    df.index.name = 'Date'
    
    # Get company info
    info = ticker.info
    company_name = info.get('longName', info.get('shortName', symbol))
    current_price = float(df['Close'].iloc[-1])
    
    print(f"✅ Fetched {len(df)} days of data for {company_name}")
    
    # Calculate indicators
    print(f"📈 Calculating technical indicators...")
    ta = TechnicalIndicators(df)
    df = ta.add_all_indicators()
    
    latest = df.iloc[-1]
    
    # Current technical state
    technical_state = {
        'RSI': round(get_value(latest, 'rsi_14', 50), 2),
        'MACD': round(get_value(latest, 'macd_12_26_9', 0), 3),
        'MACD_Signal': round(get_value(latest, 'macds_12_26_9', 0), 3),
        'ADX': round(get_value(latest, 'adx_14', 0), 2),
        'SMA_20': round(get_value(latest, 'sma_20', current_price), 2),
        'SMA_50': round(get_value(latest, 'sma_50', current_price), 2),
        'SMA_200': round(get_value(latest, 'sma_200', current_price), 2),
        'EMA_12': round(get_value(latest, 'ema_12', current_price), 2),
        'EMA_26': round(get_value(latest, 'ema_26', current_price), 2),
        'BB_Upper': round(get_value(latest, 'bbu_20', current_price), 2),
        'BB_Middle': round(get_value(latest, 'bbm_20', current_price), 2),
        'BB_Lower': round(get_value(latest, 'bbl_20', current_price), 2),
        'Volume': int(get_value(latest, 'volume', 0)),
        'Volume_SMA': int(df['Volume'].rolling(20).mean().iloc[-1]),
    }
    
    print(f"✅ Indicators calculated")
    
    # Run quick strategy checks
    signals = []
    
    # RSI signal
    rsi = technical_state['RSI']
    if rsi < 30:
        signals.append({
            'signal': 'BUY',
            'strategy': 'RSI Oversold',
            'confidence': 'HIGH' if rsi < 25 else 'MEDIUM',
            'reason': f"RSI at {rsi} (oversold zone)"
        })
    elif rsi > 70:
        signals.append({
            'signal': 'SELL',
            'strategy': 'RSI Overbought',
            'confidence': 'HIGH' if rsi > 75 else 'MEDIUM',
            'reason': f"RSI at {rsi} (overbought zone)"
        })
    
    # MACD signal
    macd = technical_state['MACD']
    macd_signal = technical_state['MACD_Signal']
    if macd > macd_signal and macd > 0:
        signals.append({
            'signal': 'BUY',
            'strategy': 'MACD Bullish',
            'confidence': 'HIGH',
            'reason': 'MACD above signal line and positive'
        })
    elif macd < macd_signal and macd < 0:
        signals.append({
            'signal': 'SELL',
            'strategy': 'MACD Bearish',
            'confidence': 'HIGH',
            'reason': 'MACD below signal line and negative'
        })
    
    # Trend signal (Triple SMA alignment)
    sma20 = technical_state['SMA_20']
    sma50 = technical_state['SMA_50']
    sma200 = technical_state['SMA_200']
    adx = technical_state['ADX']
    
    if current_price > sma20 > sma50 > sma200:
        signals.append({
            'signal': 'BUY',
            'strategy': 'Strong Uptrend',
            'confidence': 'HIGH' if adx > 25 else 'MEDIUM',
            'reason': f'Price > SMA20 > SMA50 > SMA200 (ADX: {adx})'
        })
    elif current_price < sma20 < sma50 < sma200:
        signals.append({
            'signal': 'SELL',
            'strategy': 'Strong Downtrend',
            'confidence': 'HIGH' if adx > 25 else 'MEDIUM',
            'reason': f'Price < SMA20 < SMA50 < SMA200 (ADX: {adx})'
        })
    elif current_price > sma20 > sma50:
        signals.append({
            'signal': 'BUY',
            'strategy': 'Uptrend',
            'confidence': 'MEDIUM',
            'reason': 'Price above short-term moving averages'
        })
    elif current_price < sma20 < sma50:
        signals.append({
            'signal': 'SELL',
            'strategy': 'Downtrend',
            'confidence': 'MEDIUM',
            'reason': 'Price below short-term moving averages'
        })
    
    # Bollinger Bands signal
    bb_upper = technical_state['BB_Upper']
    bb_lower = technical_state['BB_Lower']
    
    if current_price <= bb_lower * 1.01:  # Within 1% of lower band
        signals.append({
            'signal': 'BUY',
            'strategy': 'BB Bounce',
            'confidence': 'MEDIUM',
            'reason': f'Price at lower Bollinger Band (${bb_lower:.2f})'
        })
    elif current_price >= bb_upper * 0.99:  # Within 1% of upper band
        signals.append({
            'signal': 'SELL',
            'strategy': 'BB Overbought',
            'confidence': 'MEDIUM',
            'reason': f'Price at upper Bollinger Band (${bb_upper:.2f})'
        })
    
    # Volume signal
    if technical_state['Volume'] > technical_state['Volume_SMA'] * 1.5:
        price_up = current_price > df['Close'].iloc[-2]
        if price_up:
            signals.append({
                'signal': 'BUY',
                'strategy': 'Volume Surge',
                'confidence': 'MEDIUM',
                'reason': 'High volume with price increase'
            })
        else:
            signals.append({
                'signal': 'SELL',
                'strategy': 'Volume Dump',
                'confidence': 'MEDIUM',
                'reason': 'High volume with price decrease'
            })
    
    print(f"✅ Found {len(signals)} signals")
    
    # Price change analysis
    price_change_1d = ((df['Close'].iloc[-1] - df['Close'].iloc[-2]) / df['Close'].iloc[-2]) * 100
    price_change_5d = ((df['Close'].iloc[-1] - df['Close'].iloc[-6]) / df['Close'].iloc[-6]) * 100
    price_change_1m = ((df['Close'].iloc[-1] - df['Close'].iloc[-21]) / df['Close'].iloc[-21]) * 100
    
    # Overall recommendation
    buy_signals = len([s for s in signals if s['signal'] == 'BUY'])
    sell_signals = len([s for s in signals if s['signal'] == 'SELL'])
    
    if buy_signals > sell_signals:
        recommendation = 'BUY' if buy_signals >= 2 else 'HOLD'
        confidence = 'HIGH' if buy_signals >= 3 else 'MEDIUM' if buy_signals >= 2 else 'LOW'
    elif sell_signals > buy_signals:
        recommendation = 'SELL' if sell_signals >= 2 else 'HOLD'
        confidence = 'HIGH' if sell_signals >= 3 else 'MEDIUM' if sell_signals >= 2 else 'LOW'
    else:
        recommendation = 'HOLD'
        confidence = 'LOW'
    
    print(f"✅ Recommendation: {recommendation} (Confidence: {confidence})")
    
    return {
        'symbol': symbol,
        'company_name': company_name,
        'current_price': round(current_price, 2),
        'data_points': len(df),
        'date_range': f"{df.index[0].date()} to {df.index[-1].date()}",
        'price_changes': {
            '1_day': round(price_change_1d, 2),
            '5_day': round(price_change_5d, 2),
            '1_month': round(price_change_1m, 2),
        },
        'technical_indicators': technical_state,
        'signals': signals,
        'recommendation': recommendation,
        'confidence': confidence,
        'buy_signals_count': buy_signals,
        'sell_signals_count': sell_signals,
    }


def main():
    parser = argparse.ArgumentParser(description='Analyze a symbol on-demand')
    parser.add_argument('--symbol', required=True, help='Symbol to analyze')
    parser.add_argument('--period', default='1y', help='Data period (default: 1y)')
    parser.add_argument('--output', help='Output JSON file')
    
    args = parser.parse_args()
    
    try:
        result = analyze_symbol(args.symbol.upper(), args.period)
        
        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w') as f:
                json.dump(result, f, indent=2)
            print(f"✅ Analysis saved to {args.output}")
        else:
            print(json.dumps(result, indent=2))
        
        return 0
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

