#!/usr/bin/env python3
"""
Daily Strategy Runner
Automatically runs trading strategies and generates buy/sell alerts
"""

import pandas as pd
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict

from indicators import TechnicalIndicators


@dataclass
class TradingAlert:
    """Represents a trading alert/signal"""
    symbol: str
    signal: str  # 'BUY', 'SELL', 'HOLD'
    strategy_name: str
    confidence: str  # 'HIGH', 'MEDIUM', 'LOW'
    price: float
    timestamp: str
    reason: str
    technical_data: Dict
    
    def to_dict(self) -> Dict:
        """Convert to dictionary with rounded values"""
        data = asdict(self)
        # Round price and all technical data to 2 decimals
        data['price'] = round(data['price'], 2)
        data['technical_data'] = {
            k: round(v, 2) if isinstance(v, float) else v 
            for k, v in data['technical_data'].items()
        }
        return data
    
    def to_telegram_message(self) -> str:
        """Format alert for Telegram"""
        emoji = "🟢" if self.signal == 'BUY' else "🔴" if self.signal == 'SELL' else "⚪"
        conf_emoji = "⭐⭐⭐" if self.confidence == 'HIGH' else "⭐⭐" if self.confidence == 'MEDIUM' else "⭐"
        
        msg = f"{emoji} <b>{self.signal} ALERT</b> {emoji}\n\n"
        msg += f"<b>Symbol:</b> {self.symbol}\n"
        msg += f"<b>Price:</b> ${self.price:.2f}\n"
        msg += f"<b>Strategy:</b> {self.strategy_name}\n"
        msg += f"<b>Confidence:</b> {self.confidence} {conf_emoji}\n\n"
        msg += f"<b>Reason:</b>\n{self.reason}\n\n"
        msg += f"<b>Technical Data:</b>\n"
        for key, value in self.technical_data.items():
            if isinstance(value, float):
                msg += f"  • {key}: {value:.2f}\n"
            else:
                msg += f"  • {key}: {value}\n"
        msg += f"\n<i>Time: {self.timestamp}</i>"
        
        return msg


class StrategyRunner:
    """
    Runs trading strategies daily and generates alerts
    """
    
    def __init__(self, data_dir: str = 'data'):
        self.data_dir = Path(data_dir)
        self.alerts: List[TradingAlert] = []
    
    def discover_symbols(self) -> List[str]:
        """Find all CSV files in data directory"""
        csv_files = list(self.data_dir.glob('*.csv'))
        symbols = [f.stem for f in csv_files]
        return symbols
    
    def load_data(self, symbol: str) -> pd.DataFrame:
        """Load price data for a symbol"""
        file_path = self.data_dir / f'{symbol}.csv'
        if not file_path.exists():
            return pd.DataFrame()
        
        df = pd.read_csv(file_path, index_col='Date', parse_dates=True)
        df = df.sort_index()
        return df
    
    # ==================== STRATEGY DEFINITIONS ====================
    
    def strategy_rsi_macd_confluence(self, symbol: str, df: pd.DataFrame) -> Optional[TradingAlert]:
        """
        RSI + MACD Confluence Strategy
        
        BUY when:
        - RSI < 35 (oversold)
        - MACD crosses above signal
        - Both conditions must be met
        
        SELL when:
        - RSI > 65 (overbought)
        - MACD crosses below signal
        """
        # Add indicators
        indicators = TechnicalIndicators(df)
        indicators.add_rsi(14)
        indicators.add_macd()
        indicators.add_adx()
        
        df = indicators.df
        latest = df.iloc[-1]
        previous = df.iloc[-2]
        
        # Get values
        rsi = latest['RSI_14']
        macd = latest['MACD_12_26_9']
        macd_signal = latest['MACDs_12_26_9']
        macd_prev = previous['MACD_12_26_9']
        macd_signal_prev = previous['MACDs_12_26_9']
        adx = latest['ADX_14']
        
        # Detect MACD crossover
        macd_bullish_cross = macd > macd_signal and macd_prev <= macd_signal_prev
        macd_bearish_cross = macd < macd_signal and macd_prev >= macd_signal_prev
        
        # BUY Signal
        if rsi < 35 and macd_bullish_cross and adx > 20:
            confidence = 'HIGH' if rsi < 30 and adx > 25 else 'MEDIUM'
            reason = (
                f"• RSI is oversold at {rsi:.2f} (< 35)\n"
                f"• MACD just crossed above signal line\n"
                f"• ADX shows strong trend at {adx:.2f}"
            )
            
            return TradingAlert(
                symbol=symbol,
                signal='BUY',
                strategy_name='RSI+MACD Confluence',
                confidence=confidence,
                price=latest['Close'],
                timestamp=datetime.now().isoformat(),
                reason=reason,
                technical_data={
                    'RSI': rsi,
                    'MACD': macd,
                    'Signal': macd_signal,
                    'ADX': adx,
                    'Volume': int(latest['Volume'])
                }
            )
        
        # SELL Signal
        elif rsi > 65 and macd_bearish_cross:
            confidence = 'HIGH' if rsi > 70 else 'MEDIUM'
            reason = (
                f"• RSI is overbought at {rsi:.2f} (> 65)\n"
                f"• MACD just crossed below signal line\n"
                f"• Momentum losing strength"
            )
            
            return TradingAlert(
                symbol=symbol,
                signal='SELL',
                strategy_name='RSI+MACD Confluence',
                confidence=confidence,
                price=latest['Close'],
                timestamp=datetime.now().isoformat(),
                reason=reason,
                technical_data={
                    'RSI': rsi,
                    'MACD': macd,
                    'Signal': macd_signal,
                    'ADX': adx
                }
            )
        
        return None
    
    def strategy_trend_following(self, symbol: str, df: pd.DataFrame) -> Optional[TradingAlert]:
        """
        Trend Following Strategy
        
        BUY when:
        - Price > SMA20 > SMA50 > SMA200 (strong uptrend)
        - RSI between 40-70 (not overbought)
        - ADX > 25 (strong trend)
        
        SELL when:
        - Price < SMA20 (trend broken)
        - OR RSI < 35 (momentum lost)
        """
        # Add indicators
        indicators = TechnicalIndicators(df)
        indicators.add_sma(20)
        indicators.add_sma(50)
        indicators.add_sma(200)
        indicators.add_rsi(14)
        indicators.add_adx()
        
        df = indicators.df
        latest = df.iloc[-1]
        
        # Get values
        price = latest['Close']
        sma20 = latest['SMA_20']
        sma50 = latest['SMA_50']
        sma200 = latest['SMA_200']
        rsi = latest['RSI_14']
        adx = latest['ADX_14']
        
        # BUY Signal - Strong uptrend
        if (price > sma20 > sma50 > sma200 and 
            40 < rsi < 70 and 
            adx > 25):
            
            # Calculate distance from MAs
            dist_sma20 = ((price - sma20) / sma20) * 100
            
            confidence = 'HIGH' if adx > 30 and 45 < rsi < 60 else 'MEDIUM'
            reason = (
                f"• Strong uptrend: Price > SMA20 > SMA50 > SMA200\n"
                f"• Price is {dist_sma20:.2f}% above SMA20\n"
                f"• RSI healthy at {rsi:.2f} (not overbought)\n"
                f"• ADX confirms strong trend at {adx:.2f}"
            )
            
            return TradingAlert(
                symbol=symbol,
                signal='BUY',
                strategy_name='Trend Following',
                confidence=confidence,
                price=price,
                timestamp=datetime.now().isoformat(),
                reason=reason,
                technical_data={
                    'Price': price,
                    'SMA20': sma20,
                    'SMA50': sma50,
                    'SMA200': sma200,
                    'RSI': rsi,
                    'ADX': adx
                }
            )
        
        # SELL Signal - Trend broken
        elif price < sma20 or rsi < 35:
            confidence = 'HIGH' if price < sma20 and rsi < 35 else 'MEDIUM'
            
            reason_parts = []
            if price < sma20:
                reason_parts.append(f"• Trend broken: Price fell below SMA20")
            if rsi < 35:
                reason_parts.append(f"• Momentum lost: RSI dropped to {rsi:.2f}")
            
            reason = "\n".join(reason_parts)
            
            return TradingAlert(
                symbol=symbol,
                signal='SELL',
                strategy_name='Trend Following',
                confidence=confidence,
                price=price,
                timestamp=datetime.now().isoformat(),
                reason=reason,
                technical_data={
                    'Price': price,
                    'SMA20': sma20,
                    'RSI': rsi,
                    'ADX': adx
                }
            )
        
        return None
    
    def strategy_bollinger_mean_reversion(self, symbol: str, df: pd.DataFrame) -> Optional[TradingAlert]:
        """
        Bollinger Band Mean Reversion Strategy
        
        BUY when:
        - Price touches or goes below lower BB
        - RSI < 40
        - Volume spike
        
        SELL when:
        - Price touches or goes above upper BB
        - RSI > 60
        """
        # Add indicators
        indicators = TechnicalIndicators(df)
        indicators.add_bbands(length=20, std=2.0)
        indicators.add_rsi(14)
        
        df = indicators.df
        latest = df.iloc[-1]
        
        # Get BB columns
        bb_lower = [col for col in df.columns if 'BBL' in col][0]
        bb_upper = [col for col in df.columns if 'BBU' in col][0]
        bb_middle = [col for col in df.columns if 'BBM' in col][0]
        
        price = latest['Close']
        lower_band = latest[bb_lower]
        upper_band = latest[bb_upper]
        middle_band = latest[bb_middle]
        rsi = latest['RSI_14']
        
        # Volume analysis
        volume = latest['Volume']
        avg_volume = df['Volume'].tail(20).mean()
        volume_ratio = volume / avg_volume
        
        # BUY Signal - Bounce from lower band
        if price <= lower_band * 1.01 and rsi < 40:
            confidence = 'HIGH' if price < lower_band and rsi < 35 and volume_ratio > 1.5 else 'MEDIUM'
            
            price_to_lower = ((price - lower_band) / lower_band) * 100
            reason = (
                f"• Price at lower Bollinger Band ({price_to_lower:.2f}% from band)\n"
                f"• RSI oversold at {rsi:.2f}\n"
                f"• Volume {volume_ratio:.2f}x average (potential reversal)\n"
                f"• Mean reversion opportunity to ${middle_band:.2f}"
            )
            
            return TradingAlert(
                symbol=symbol,
                signal='BUY',
                strategy_name='BB Mean Reversion',
                confidence=confidence,
                price=price,
                timestamp=datetime.now().isoformat(),
                reason=reason,
                technical_data={
                    'Price': price,
                    'Lower_Band': lower_band,
                    'Middle_Band': middle_band,
                    'Upper_Band': upper_band,
                    'RSI': rsi,
                    'Volume_Ratio': round(volume_ratio, 2)
                }
            )
        
        # SELL Signal - Touch upper band
        elif price >= upper_band * 0.99 and rsi > 60:
            confidence = 'HIGH' if price > upper_band and rsi > 70 else 'MEDIUM'
            
            price_to_upper = ((price - upper_band) / upper_band) * 100
            reason = (
                f"• Price at upper Bollinger Band ({price_to_upper:.2f}% from band)\n"
                f"• RSI overbought at {rsi:.2f}\n"
                f"• Mean reversion expected back to ${middle_band:.2f}"
            )
            
            return TradingAlert(
                symbol=symbol,
                signal='SELL',
                strategy_name='BB Mean Reversion',
                confidence=confidence,
                price=price,
                timestamp=datetime.now().isoformat(),
                reason=reason,
                technical_data={
                    'Price': price,
                    'Upper_Band': upper_band,
                    'Middle_Band': middle_band,
                    'RSI': rsi
                }
            )
        
        return None
    
    def strategy_momentum_breakout(self, symbol: str, df: pd.DataFrame) -> Optional[TradingAlert]:
        """
        Momentum Breakout Strategy
        
        BUY when:
        - Price breaks above 20-day high
        - Volume > 1.5x average
        - ADX > 25 (trending)
        
        SELL when:
        - Price breaks below 20-day low
        - OR RSI < 30
        """
        # Add indicators
        indicators = TechnicalIndicators(df)
        indicators.add_adx()
        indicators.add_rsi(14)
        
        df = indicators.df
        latest = df.iloc[-1]
        
        # Calculate 20-day high/low
        lookback_period = 20
        recent_data = df.tail(lookback_period + 1)
        high_20 = recent_data['High'].iloc[:-1].max()
        low_20 = recent_data['Low'].iloc[:-1].min()
        
        price = latest['Close']
        adx = latest['ADX_14']
        rsi = latest['RSI_14']
        
        # Volume analysis
        volume = latest['Volume']
        avg_volume = df['Volume'].tail(20).mean()
        volume_ratio = volume / avg_volume
        
        # BUY Signal - Breakout above resistance
        if price > high_20 and volume_ratio > 1.5 and adx > 25:
            confidence = 'HIGH' if volume_ratio > 2.0 and adx > 30 else 'MEDIUM'
            
            breakout_pct = ((price - high_20) / high_20) * 100
            reason = (
                f"• Breakout: Price surpassed 20-day high (${high_20:.2f})\n"
                f"• Breakout size: {breakout_pct:.2f}%\n"
                f"• Volume spike: {volume_ratio:.2f}x average (strong confirmation)\n"
                f"• ADX at {adx:.2f} confirms strong trend\n"
                f"• Potential continuation to new highs"
            )
            
            return TradingAlert(
                symbol=symbol,
                signal='BUY',
                strategy_name='Momentum Breakout',
                confidence=confidence,
                price=price,
                timestamp=datetime.now().isoformat(),
                reason=reason,
                technical_data={
                    'Price': price,
                    '20D_High': high_20,
                    'Breakout_%': round(breakout_pct, 2),
                    'Volume_Ratio': round(volume_ratio, 2),
                    'ADX': adx,
                    'RSI': rsi
                }
            )
        
        # SELL Signal - Breakdown below support
        elif price < low_20 or rsi < 30:
            confidence = 'HIGH' if price < low_20 and rsi < 30 else 'MEDIUM'
            
            reason_parts = []
            if price < low_20:
                breakdown_pct = ((low_20 - price) / low_20) * 100
                reason_parts.append(f"• Breakdown: Price fell below 20-day low (${low_20:.2f})")
                reason_parts.append(f"• Breakdown size: {breakdown_pct:.2f}%")
            if rsi < 30:
                reason_parts.append(f"• RSI oversold at {rsi:.2f}")
            
            reason = "\n".join(reason_parts)
            
            return TradingAlert(
                symbol=symbol,
                signal='SELL',
                strategy_name='Momentum Breakout',
                confidence=confidence,
                price=price,
                timestamp=datetime.now().isoformat(),
                reason=reason,
                technical_data={
                    'Price': price,
                    '20D_Low': low_20,
                    'RSI': rsi,
                    'ADX': adx
                }
            )
        
        return None
    
    # ==================== MAIN RUNNER ====================
    
    def run_daily_analysis(self, 
                          strategies: List[str] = None,
                          min_confidence: str = 'MEDIUM') -> List[TradingAlert]:
        """
        Run all strategies on all symbols and generate alerts
        
        Args:
            strategies: List of strategy names to run (None = all)
            min_confidence: Minimum confidence level ('LOW', 'MEDIUM', 'HIGH')
        
        Returns:
            List of trading alerts
        """
        print("\n" + "="*80)
        print("🔍 DAILY STRATEGY ANALYSIS")
        print("="*80)
        
        # Available strategies
        available_strategies = {
            'rsi_macd': self.strategy_rsi_macd_confluence,
            'trend_following': self.strategy_trend_following,
            'mean_reversion': self.strategy_bollinger_mean_reversion,
            'momentum_breakout': self.strategy_momentum_breakout
        }
        
        # Select strategies to run
        if strategies is None:
            strategies_to_run = available_strategies
        else:
            strategies_to_run = {k: v for k, v in available_strategies.items() if k in strategies}
        
        # Discover symbols
        symbols = self.discover_symbols()
        print(f"📊 Analyzing {len(symbols)} symbols: {', '.join(symbols)}")
        print(f"🎯 Running {len(strategies_to_run)} strategies")
        print(f"⭐ Minimum confidence: {min_confidence}\n")
        
        self.alerts = []
        confidence_order = {'LOW': 0, 'MEDIUM': 1, 'HIGH': 2}
        min_conf_level = confidence_order[min_confidence]
        
        # Run strategies on each symbol
        for symbol in symbols:
            print(f"Analyzing {symbol}...", end=" ")
            
            df = self.load_data(symbol)
            if df.empty or len(df) < 250:  # Need enough data
                print("❌ Insufficient data")
                continue
            
            symbol_alerts = []
            
            # Run each strategy
            for strategy_name, strategy_func in strategies_to_run.items():
                try:
                    alert = strategy_func(symbol, df)
                    if alert and confidence_order[alert.confidence] >= min_conf_level:
                        symbol_alerts.append(alert)
                except Exception as e:
                    print(f"\n⚠️  Error in {strategy_name} for {symbol}: {e}")
            
            if symbol_alerts:
                self.alerts.extend(symbol_alerts)
                signals = [f"{a.signal}({a.confidence})" for a in symbol_alerts]
                print(f"🚨 {len(symbol_alerts)} alert(s): {', '.join(signals)}")
            else:
                print("✅ No alerts")
        
        return self.alerts
    
    def save_alerts(self, output_file: str = 'signals/daily_alerts.json'):
        """Save alerts to JSON file"""
        output_path = Path(output_file)
        output_path.parent.mkdir(exist_ok=True)
        
        alerts_data = {
            'generated_at': datetime.now().isoformat(),
            'total_alerts': len(self.alerts),
            'buy_signals': len([a for a in self.alerts if a.signal == 'BUY']),
            'sell_signals': len([a for a in self.alerts if a.signal == 'SELL']),
            'alerts': [alert.to_dict() for alert in self.alerts]
        }
        
        with open(output_path, 'w') as f:
            json.dump(alerts_data, f, indent=2)
        
        print(f"\n✅ Alerts saved to {output_path}")
    
    def print_summary(self):
        """Print summary of alerts"""
        if not self.alerts:
            print("\n" + "="*80)
            print("✅ NO ALERTS TODAY - All positions hold steady")
            print("="*80)
            return
        
        print("\n" + "="*80)
        print("🚨 DAILY TRADING ALERTS SUMMARY")
        print("="*80)
        
        buy_alerts = [a for a in self.alerts if a.signal == 'BUY']
        sell_alerts = [a for a in self.alerts if a.signal == 'SELL']
        
        print(f"\nTotal Alerts: {len(self.alerts)}")
        print(f"  🟢 BUY:  {len(buy_alerts)}")
        print(f"  🔴 SELL: {len(sell_alerts)}")
        
        # Group by confidence
        high_conf = [a for a in self.alerts if a.confidence == 'HIGH']
        med_conf = [a for a in self.alerts if a.confidence == 'MEDIUM']
        
        print(f"\nBy Confidence:")
        print(f"  ⭐⭐⭐ HIGH:   {len(high_conf)}")
        print(f"  ⭐⭐  MEDIUM: {len(med_conf)}")
        
        # Print HIGH confidence alerts
        if high_conf:
            print(f"\n{'='*80}")
            print("⭐⭐⭐ HIGH CONFIDENCE ALERTS ⭐⭐⭐")
            print(f"{'='*80}")
            
            for alert in high_conf:
                emoji = "🟢" if alert.signal == 'BUY' else "🔴"
                print(f"\n{emoji} {alert.signal} - {alert.symbol} @ ${alert.price:.2f}")
                print(f"Strategy: {alert.strategy_name}")
                print(f"Reason:\n{alert.reason}")
        
        print(f"\n{'='*80}")


if __name__ == "__main__":
    # Run daily analysis
    runner = StrategyRunner()
    
    # Run all strategies with MEDIUM+ confidence
    alerts = runner.run_daily_analysis(min_confidence='MEDIUM')
    
    # Print summary
    runner.print_summary()
    
    # Save alerts
    runner.save_alerts()
    
    print("\n" + "="*80)
    print("✅ Daily analysis complete!")
    print("="*80)

