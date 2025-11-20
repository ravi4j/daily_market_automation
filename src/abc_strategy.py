#!/usr/bin/env python3
"""
ABC Pattern Trading Strategy

Generates trading signals based on ABC wave patterns with Fibonacci levels.
Integrates with the existing trading system for daily alerts.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from src.abc_pattern_detector import ABCPatternDetector, ABCPattern


@dataclass
class ABCTradingSignal:
    """ABC Pattern Trading Signal"""
    symbol: str
    timestamp: datetime
    signal: str  # BUY, SELL, HOLD
    confidence: str  # LOW, MEDIUM, HIGH
    pattern_type: str  # BULLISH or BEARISH
    
    # Current state
    current_price: float
    pattern_activated: bool
    c_reached: bool
    
    # Entry information
    entry_levels: List[float]
    best_entry: Optional[float]
    
    # Risk management
    stop_loss: float
    take_profit_1: float
    take_profit_2: float
    take_profit_3: float
    risk_reward: float
    
    # Pattern details
    point_0: float
    point_a: float
    point_b: float
    point_c: Optional[float]
    a2_price: Optional[float]
    retracement_pct: float
    
    # Technical data
    technical_data: Dict
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        result = asdict(self)
        # Round floats to 2 decimal places
        for key, value in result.items():
            if isinstance(value, float):
                result[key] = round(value, 2)
            elif isinstance(value, list) and value and isinstance(value[0], float):
                result[key] = [round(v, 2) for v in value]
        
        # Convert datetime to string
        if isinstance(result.get('timestamp'), datetime):
            result['timestamp'] = result['timestamp'].isoformat()
        
        return result


class ABCStrategy:
    """ABC Pattern Trading Strategy"""
    
    def __init__(self, swing_length: int = 10, min_retrace: float = 0.382,
                 max_retrace: float = 0.786, stop_loss_pips: int = 20,
                 min_risk_reward: float = 2.5):
        """
        Initialize ABC Strategy
        
        Args:
            swing_length: Lookback for swing detection
            min_retrace: Minimum retracement ratio
            max_retrace: Maximum retracement ratio
            stop_loss_pips: Stop loss distance in pips
            min_risk_reward: Minimum R:R ratio for trade
        """
        self.detector = ABCPatternDetector(
            swing_length=swing_length,
            min_retrace=min_retrace,
            max_retrace=max_retrace,
            stop_loss_pips=stop_loss_pips
        )
        self.min_risk_reward = min_risk_reward
    
    def generate_signal(self, symbol: str, df: pd.DataFrame,
                       pip_size: float = 0.0001) -> Optional[ABCTradingSignal]:
        """
        Generate trading signal based on ABC patterns
        
        Returns:
            ABCTradingSignal if valid pattern found, None otherwise
        """
        # Get current patterns
        patterns = self.detector.get_current_patterns(df, max_patterns=1)
        
        if not patterns:
            return None
        
        # Use most recent pattern
        pattern = patterns[0]
        
        # Get current price
        close_col = self._get_col(df, 'close')
        current_price = float(df[close_col].iloc[-1])
        
        # Determine signal
        signal, confidence = self._evaluate_signal(pattern, current_price, df)
        
        # Get technical data
        technical_data = self._get_technical_data(df)
        
        # Create trading signal
        trading_signal = ABCTradingSignal(
            symbol=symbol,
            timestamp=datetime.now(),
            signal=signal,
            confidence=confidence,
            pattern_type=pattern.trend,
            current_price=current_price,
            pattern_activated=pattern.activated,
            c_reached=pattern.c_reached,
            entry_levels=pattern.entry_levels if pattern.entry_levels else [],
            best_entry=pattern.entry_levels[0] if pattern.entry_levels else None,
            stop_loss=pattern.stop_loss if pattern.stop_loss else 0.0,
            take_profit_1=pattern.take_profits[0] if pattern.take_profits else 0.0,
            take_profit_2=pattern.take_profits[1] if len(pattern.take_profits) > 1 else 0.0,
            take_profit_3=pattern.take_profits[2] if len(pattern.take_profits) > 2 else 0.0,
            risk_reward=pattern.risk_reward,
            point_0=pattern.point_0,
            point_a=pattern.point_a,
            point_b=pattern.point_b,
            point_c=pattern.point_c,
            a2_price=pattern.a2_price,
            retracement_pct=pattern.retracement_ratio * 100,
            technical_data=technical_data
        )
        
        return trading_signal
    
    def _evaluate_signal(self, pattern: ABCPattern, current_price: float,
                        df: pd.DataFrame) -> tuple:
        """
        Evaluate pattern and return (signal, confidence)
        
        Returns:
            Tuple of (signal: str, confidence: str)
        """
        # Pattern not activated yet
        if not pattern.activated:
            return "HOLD", "LOW"
        
        # Check if risk/reward is acceptable
        if pattern.risk_reward < self.min_risk_reward:
            return "HOLD", "LOW"
        
        # Pattern activated but C already reached - no new trade
        if pattern.c_reached:
            return "HOLD", "LOW"
        
        # Check if price is in entry zone
        if not pattern.entry_levels:
            return "HOLD", "LOW"
        
        in_entry_zone = False
        if pattern.trend == "BULLISH":
            # Check if current price is near or below any entry level
            for entry in pattern.entry_levels:
                if current_price <= entry * 1.01:  # Within 1% of entry
                    in_entry_zone = True
                    break
        else:  # BEARISH
            # Check if current price is near or above any entry level
            for entry in pattern.entry_levels:
                if current_price >= entry * 0.99:  # Within 1% of entry
                    in_entry_zone = True
                    break
        
        # Determine signal
        if pattern.trend == "BULLISH":
            signal = "BUY" if in_entry_zone else "HOLD"
        else:  # BEARISH
            signal = "SELL" if in_entry_zone else "HOLD"
        
        # Determine confidence
        confidence = self._calculate_confidence(pattern, current_price, df, in_entry_zone)
        
        return signal, confidence
    
    def _calculate_confidence(self, pattern: ABCPattern, current_price: float,
                             df: pd.DataFrame, in_entry_zone: bool) -> str:
        """Calculate confidence level based on multiple factors"""
        confidence_score = 0
        
        # Factor 1: Risk/Reward ratio (0-3 points)
        if pattern.risk_reward >= 4.0:
            confidence_score += 3
        elif pattern.risk_reward >= 3.0:
            confidence_score += 2
        elif pattern.risk_reward >= 2.5:
            confidence_score += 1
        
        # Factor 2: Retracement ratio (0-2 points)
        # Sweet spot is 0.5-0.618 (golden ratio zone)
        if 0.5 <= pattern.retracement_ratio <= 0.618:
            confidence_score += 2
        elif 0.45 <= pattern.retracement_ratio <= 0.7:
            confidence_score += 1
        
        # Factor 3: In entry zone (0-2 points)
        if in_entry_zone:
            confidence_score += 2
        
        # Factor 4: Volume confirmation (0-2 points)
        volume_col = self._get_col(df, 'volume')
        if volume_col:
            current_volume = df[volume_col].iloc[-1]
            avg_volume = df[volume_col].rolling(20).mean().iloc[-1]
            if current_volume > avg_volume * 1.2:
                confidence_score += 2
            elif current_volume > avg_volume:
                confidence_score += 1
        
        # Factor 5: Trend alignment (0-1 point)
        sma50_col = self._get_col(df, 'sma_50')
        if sma50_col:
            sma50 = df[sma50_col].iloc[-1]
            if pattern.trend == "BULLISH" and current_price > sma50:
                confidence_score += 1
            elif pattern.trend == "BEARISH" and current_price < sma50:
                confidence_score += 1
        
        # Convert score to confidence level
        # Max score: 10
        if confidence_score >= 8:
            return "HIGH"
        elif confidence_score >= 5:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _get_technical_data(self, df: pd.DataFrame) -> Dict:
        """Extract current technical indicators"""
        latest = df.iloc[-1]
        
        technical_data = {
            'RSI': self._get_value(latest, 'rsi_14', 50),
            'MACD': self._get_value(latest, 'macd_12', 0),
            'ADX': self._get_value(latest, 'adx_14', 0),
            'SMA_20': self._get_value(latest, 'sma_20', 0),
            'SMA_50': self._get_value(latest, 'sma_50', 0),
            'Volume': int(self._get_value(latest, 'volume', 0)),
        }
        
        return technical_data
    
    def _get_value(self, row, pattern: str, default=0):
        """Get value from row with pattern matching"""
        for col in row.index:
            if pattern.lower() in col.lower():
                val = row[col]
                return val if pd.notna(val) else default
        return default
    
    def _get_col(self, df: pd.DataFrame, pattern: str) -> Optional[str]:
        """Get column name by pattern"""
        pattern_lower = pattern.lower()
        for col in df.columns:
            if pattern_lower in col.lower():
                return col
        return None
    
    def format_telegram_message(self, signal: ABCTradingSignal) -> str:
        """
        Format ABC signal as Telegram message
        
        Returns:
            Formatted message string
        """
        emoji = "🟢" if signal.signal == "BUY" else "🔴" if signal.signal == "SELL" else "⚪"
        conf_emoji = {"HIGH": "⭐⭐⭐", "MEDIUM": "⭐⭐", "LOW": "⭐"}.get(signal.confidence, "⭐")
        
        message = f"{emoji} <b>ABC Pattern: {signal.signal} {conf_emoji}</b>\n\n"
        message += f"<b>{signal.symbol}</b> - {signal.pattern_type} Setup\n"
        message += f"💰 Current Price: ${signal.current_price:.2f}\n\n"
        
        # Pattern status
        message += "<b>📊 Pattern Status:</b>\n"
        message += f"  • Activated: {'✅ Yes' if signal.pattern_activated else '❌ Not yet'}\n"
        message += f"  • Point C Reached: {'✅ Yes' if signal.c_reached else '❌ No'}\n"
        message += f"  • Retracement: {signal.retracement_pct:.1f}%\n\n"
        
        # Pattern structure
        message += "<b>🎯 Pattern Structure:</b>\n"
        message += f"  • Point 0: ${signal.point_0:.2f}\n"
        message += f"  • Point A: ${signal.point_a:.2f}\n"
        message += f"  • Point B: ${signal.point_b:.2f}\n"
        if signal.a2_price:
            message += f"  • Point A2: ${signal.a2_price:.2f} (New {('High' if signal.pattern_type == 'BULLISH' else 'Low')})\n"
        if signal.point_c:
            message += f"  • Point C: ${signal.point_c:.2f}\n"
        message += "\n"
        
        # Entry levels
        if signal.entry_levels and signal.pattern_activated:
            message += "<b>📍 BC Entry Zones (B→A2):</b>\n"
            labels = ["0.5 (Aggressive)", "0.559 (Optimal)", "0.618 (Golden)", "0.667 (Conservative)"]
            for i, (entry, label) in enumerate(zip(signal.entry_levels, labels)):
                distance = ((entry - signal.current_price) / signal.current_price) * 100
                dist_emoji = "🎯" if abs(distance) < 1 else "📌"
                message += f"  {dist_emoji} Entry {i+1}: ${entry:.2f} ({label})\n"
                message += f"     Distance: {distance:+.2f}%\n"
            message += "\n"
        
        # Risk management
        message += "<b>🛡️ Risk Management:</b>\n"
        message += f"  • Stop Loss: ${signal.stop_loss:.2f}\n"
        message += f"  • TP1 (1.618): ${signal.take_profit_1:.2f}\n"
        message += f"  • TP2 (1.809): ${signal.take_profit_2:.2f}\n"
        message += f"  • TP3 (2.000): ${signal.take_profit_3:.2f}\n"
        message += f"  • Risk:Reward: 1:{signal.risk_reward:.1f}\n\n"
        
        # Technical confirmation
        message += "<b>📈 Technical Data:</b>\n"
        message += f"  • RSI: {signal.technical_data.get('RSI', 0):.1f}\n"
        message += f"  • MACD: {signal.technical_data.get('MACD', 0):.3f}\n"
        message += f"  • ADX: {signal.technical_data.get('ADX', 0):.1f}\n"
        message += f"  • Volume: {signal.technical_data.get('Volume', 0):,}\n\n"
        
        # Trading instructions
        if signal.signal in ["BUY", "SELL"]:
            message += "<b>💡 Trading Plan:</b>\n"
            if signal.entry_levels:
                message += f"1. Set limit orders at entry zones\n"
                message += f"2. Place stop loss at ${signal.stop_loss:.2f}\n"
                message += f"3. Target TP1 for 50% position\n"
                message += f"4. Move SL to breakeven at TP1\n"
                message += f"5. Trail remaining 50% to TP2/TP3\n"
        
        message += f"\n<i>Confidence: {signal.confidence} | {signal.timestamp.strftime('%Y-%m-%d %H:%M')}</i>"
        
        return message


def main():
    """Test ABC strategy"""
    import sys
    from pathlib import Path
    
    # Add parent directory to path
    sys.path.insert(0, str(Path(__file__).parent))
    
    from indicators import TechnicalIndicators
    
    # Load sample data
    data_file = Path(__file__).parent.parent / "data" / "AAPL.csv"
    if not data_file.exists():
        print("❌ Sample data not found")
        return
    
    df = pd.read_csv(data_file, parse_dates=['Date']).set_index('Date')
    # CSV is stored descending (newest first), sort ascending for analysis
    df = df.sort_index(ascending=True)
    df.columns = df.columns.str.title()
    
    # Add indicators
    print("📈 Calculating indicators...")
    ta = TechnicalIndicators(df)
    df = ta.add_all_indicators()
    
    # Generate signal
    print("🎯 Detecting ABC patterns...")
    strategy = ABCStrategy()
    signal = strategy.generate_signal("AAPL", df)
    
    if signal:
        print("\n✅ ABC Pattern Detected!")
        print(f"Signal: {signal.signal}")
        print(f"Confidence: {signal.confidence}")
        print(f"Pattern: {signal.pattern_type}")
        print(f"Current Price: ${signal.current_price:.2f}")
        print(f"Risk:Reward: 1:{signal.risk_reward:.1f}")
        
        print("\n📱 Telegram Message:")
        print(strategy.format_telegram_message(signal))
    else:
        print("❌ No valid ABC patterns found")


if __name__ == "__main__":
    main()

