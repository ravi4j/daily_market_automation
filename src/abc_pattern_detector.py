#!/usr/bin/env python3
"""
ABC Pattern Detector

Detects ABC wave patterns with Fibonacci retracements and extensions.
Based on swing high/low analysis similar to TradingView's pivot detection.

Pattern Structure:
- BULLISH: 0 (Low) -> A (High) -> B (Higher Low) -> C (Target)
- BEARISH: 0 (High) -> A (Low) -> B (Lower High) -> C (Target)

Entry Zones (Fibonacci levels from B to A2):
- 0.500, 0.559, 0.618, 0.667

Target Zones (Extensions from 0-A move):
- 1.618, 1.809, 2.000
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ABCPattern:
    """Represents an ABC pattern"""
    # Pattern points
    point_0: float
    point_a: float
    point_b: float
    point_c: Optional[float] = None
    
    # Bar indices
    bar_0: int = 0
    bar_a: int = 0
    bar_b: int = 0
    bar_c: Optional[int] = None
    
    # Pattern characteristics
    trend: str = "BULLISH"  # BULLISH or BEARISH
    activated: bool = False
    c_reached: bool = False
    
    # Trading levels
    entry_levels: List[float] = None
    stop_loss: float = None
    take_profits: List[float] = None
    
    # A2 - New high/low after activation
    a2_price: Optional[float] = None
    a2_bar: Optional[int] = None
    
    # Metrics
    retracement_ratio: float = 0.0
    risk_reward: float = 0.0
    
    def __post_init__(self):
        if self.entry_levels is None:
            self.entry_levels = []
        if self.take_profits is None:
            self.take_profits = []


class ABCPatternDetector:
    """Detects and analyzes ABC patterns in price data"""
    
    def __init__(self, swing_length: int = 10, min_retrace: float = 0.382, 
                 max_retrace: float = 0.786, stop_loss_pips: int = 20):
        """
        Initialize ABC Pattern Detector
        
        Args:
            swing_length: Lookback period for swing detection
            min_retrace: Minimum retracement (default: 38.2%)
            max_retrace: Maximum retracement (default: 78.6%)
            stop_loss_pips: Stop loss distance in pips
        """
        self.swing_length = swing_length
        self.min_retrace = min_retrace
        self.max_retrace = max_retrace
        self.stop_loss_pips = stop_loss_pips
    
    def find_swing_highs_lows(self, df: pd.DataFrame) -> Tuple[List[Tuple], List[Tuple]]:
        """
        Find swing highs and lows using pivot detection
        
        Returns:
            Tuple of (swing_highs, swing_lows) where each is a list of (index, price)
        """
        swing_highs = []
        swing_lows = []
        
        high_col = self._get_col(df, 'high')
        low_col = self._get_col(df, 'low')
        
        if not high_col or not low_col:
            return swing_highs, swing_lows
        
        highs = df[high_col].values
        lows = df[low_col].values
        
        # Detect swing highs
        for i in range(self.swing_length, len(df) - self.swing_length):
            is_pivot_high = True
            current_high = highs[i]
            
            # Check left side
            for j in range(i - self.swing_length, i):
                if highs[j] >= current_high:
                    is_pivot_high = False
                    break
            
            # Check right side
            if is_pivot_high:
                for j in range(i + 1, i + self.swing_length + 1):
                    if highs[j] >= current_high:
                        is_pivot_high = False
                        break
            
            if is_pivot_high:
                swing_highs.append((i, current_high))
        
        # Detect swing lows
        for i in range(self.swing_length, len(df) - self.swing_length):
            is_pivot_low = True
            current_low = lows[i]
            
            # Check left side
            for j in range(i - self.swing_length, i):
                if lows[j] <= current_low:
                    is_pivot_low = False
                    break
            
            # Check right side
            if is_pivot_low:
                for j in range(i + 1, i + self.swing_length + 1):
                    if lows[j] <= current_low:
                        is_pivot_low = False
                        break
            
            if is_pivot_low:
                swing_lows.append((i, current_low))
        
        return swing_highs, swing_lows
    
    def detect_abc_patterns(self, df: pd.DataFrame) -> List[ABCPattern]:
        """
        Detect ABC patterns in the dataframe
        
        Returns:
            List of detected ABC patterns
        """
        patterns = []
        
        swing_highs, swing_lows = self.find_swing_highs_lows(df)
        
        if len(swing_highs) < 2 or len(swing_lows) < 2:
            return patterns
        
        # Detect BULLISH patterns: 0 (Low) -> A (High) -> B (Higher Low)
        bullish = self._detect_bullish_patterns(swing_lows, swing_highs)
        patterns.extend(bullish)
        
        # Detect BEARISH patterns: 0 (High) -> A (Low) -> B (Lower High)
        bearish = self._detect_bearish_patterns(swing_highs, swing_lows)
        patterns.extend(bearish)
        
        return patterns
    
    def _detect_bullish_patterns(self, swing_lows: List[Tuple], 
                                 swing_highs: List[Tuple]) -> List[ABCPattern]:
        """Detect bullish ABC patterns"""
        patterns = []
        
        if len(swing_lows) < 2 or len(swing_highs) < 1:
            return patterns
        
        # Look for: Low0 -> HighA -> LowB (where LowB > Low0)
        for i in range(len(swing_lows) - 1):
            bar_0, price_0 = swing_lows[i]
            
            # Find next high after point 0
            for high_idx, (bar_a, price_a) in enumerate(swing_highs):
                if bar_a <= bar_0:
                    continue
                
                # Find next low after point A
                for j in range(i + 1, len(swing_lows)):
                    bar_b, price_b = swing_lows[j]
                    
                    if bar_b <= bar_a:
                        continue
                    
                    # Check if B is higher than 0 (higher low)
                    if price_b <= price_0:
                        continue
                    
                    # Calculate retracement
                    move_0a = price_a - price_0
                    retrace_ab = price_a - price_b
                    retrace_ratio = retrace_ab / move_0a if move_0a > 0 else 0
                    
                    # Check if retracement is within valid range
                    if self.min_retrace <= retrace_ratio <= self.max_retrace:
                        pattern = ABCPattern(
                            point_0=price_0,
                            point_a=price_a,
                            point_b=price_b,
                            bar_0=bar_0,
                            bar_a=bar_a,
                            bar_b=bar_b,
                            trend="BULLISH",
                            retracement_ratio=retrace_ratio
                        )
                        patterns.append(pattern)
                        break  # Found valid B, move to next 0-A pair
                
                break  # Use first valid A after 0
        
        return patterns
    
    def _detect_bearish_patterns(self, swing_highs: List[Tuple], 
                                 swing_lows: List[Tuple]) -> List[ABCPattern]:
        """Detect bearish ABC patterns"""
        patterns = []
        
        if len(swing_highs) < 2 or len(swing_lows) < 1:
            return patterns
        
        # Look for: High0 -> LowA -> HighB (where HighB < High0)
        for i in range(len(swing_highs) - 1):
            bar_0, price_0 = swing_highs[i]
            
            # Find next low after point 0
            for low_idx, (bar_a, price_a) in enumerate(swing_lows):
                if bar_a <= bar_0:
                    continue
                
                # Find next high after point A
                for j in range(i + 1, len(swing_highs)):
                    bar_b, price_b = swing_highs[j]
                    
                    if bar_b <= bar_a:
                        continue
                    
                    # Check if B is lower than 0 (lower high)
                    if price_b >= price_0:
                        continue
                    
                    # Calculate retracement
                    move_0a = price_0 - price_a
                    retrace_ab = price_b - price_a
                    retrace_ratio = retrace_ab / move_0a if move_0a > 0 else 0
                    
                    # Check if retracement is within valid range
                    if self.min_retrace <= retrace_ratio <= self.max_retrace:
                        pattern = ABCPattern(
                            point_0=price_0,
                            point_a=price_a,
                            point_b=price_b,
                            bar_0=bar_0,
                            bar_a=bar_a,
                            bar_b=bar_b,
                            trend="BEARISH",
                            retracement_ratio=retrace_ratio
                        )
                        patterns.append(pattern)
                        break  # Found valid B, move to next 0-A pair
                
                break  # Use first valid A after 0
        
        return patterns
    
    def calculate_entry_levels(self, pattern: ABCPattern, 
                               df: pd.DataFrame) -> ABCPattern:
        """
        Calculate entry levels based on BC zone (B to A2)
        Fibonacci levels: 0.5, 0.559, 0.618, 0.667
        """
        # Check if pattern is activated and A2 exists
        if not pattern.activated or pattern.a2_price is None:
            return pattern
        
        range_ba2 = abs(pattern.a2_price - pattern.point_b)
        
        if pattern.trend == "BULLISH":
            pattern.entry_levels = [
                pattern.point_b + range_ba2 * 0.500,
                pattern.point_b + range_ba2 * 0.559,
                pattern.point_b + range_ba2 * 0.618,
                pattern.point_b + range_ba2 * 0.667
            ]
        else:  # BEARISH
            pattern.entry_levels = [
                pattern.point_b - range_ba2 * 0.500,
                pattern.point_b - range_ba2 * 0.559,
                pattern.point_b - range_ba2 * 0.618,
                pattern.point_b - range_ba2 * 0.667
            ]
        
        return pattern
    
    def calculate_targets(self, pattern: ABCPattern) -> ABCPattern:
        """
        Calculate take profit targets
        Extensions: 1.618, 1.809, 2.000
        """
        move_0a = abs(pattern.point_a - pattern.point_0)
        
        if pattern.trend == "BULLISH":
            pattern.take_profits = [
                pattern.point_b + move_0a * 1.618,
                pattern.point_b + move_0a * 1.809,
                pattern.point_b + move_0a * 2.000
            ]
        else:  # BEARISH
            pattern.take_profits = [
                pattern.point_b - move_0a * 1.618,
                pattern.point_b - move_0a * 1.809,
                pattern.point_b - move_0a * 2.000
            ]
        
        return pattern
    
    def calculate_stop_loss(self, pattern: ABCPattern, 
                           pip_size: float = 0.0001) -> ABCPattern:
        """Calculate stop loss level"""
        sl_distance = self.stop_loss_pips * pip_size * 10
        
        if pattern.trend == "BULLISH":
            pattern.stop_loss = pattern.point_b - sl_distance
        else:  # BEARISH
            pattern.stop_loss = pattern.point_b + sl_distance
        
        return pattern
    
    def check_activation(self, pattern: ABCPattern, df: pd.DataFrame, 
                        current_idx: int) -> ABCPattern:
        """
        Check if pattern is activated (close breaks point A)
        """
        if pattern.activated:
            return pattern
        
        close_col = self._get_col(df, 'close')
        high_col = self._get_col(df, 'high')
        low_col = self._get_col(df, 'low')
        
        if not close_col:
            return pattern
        
        current_close = df[close_col].iloc[current_idx]
        prev_close = df[close_col].iloc[current_idx - 1] if current_idx > 0 else current_close
        
        # Check for activation (close-based)
        if pattern.trend == "BULLISH":
            if current_close > pattern.point_a and prev_close <= pattern.point_a:
                pattern.activated = True
                pattern.a2_price = df[high_col].iloc[current_idx]
                pattern.a2_bar = current_idx
        else:  # BEARISH
            if current_close < pattern.point_a and prev_close >= pattern.point_a:
                pattern.activated = True
                pattern.a2_price = df[low_col].iloc[current_idx]
                pattern.a2_bar = current_idx
        
        return pattern
    
    def update_a2(self, pattern: ABCPattern, df: pd.DataFrame, 
                  current_idx: int) -> ABCPattern:
        """
        Update A2 (new high/low after activation)
        """
        if not pattern.activated or pattern.c_reached:
            return pattern
        
        high_col = self._get_col(df, 'high')
        low_col = self._get_col(df, 'low')
        
        current_high = df[high_col].iloc[current_idx]
        current_low = df[low_col].iloc[current_idx]
        
        if pattern.trend == "BULLISH":
            if current_high > pattern.a2_price:
                pattern.a2_price = current_high
                pattern.a2_bar = current_idx
        else:  # BEARISH
            if current_low < pattern.a2_price:
                pattern.a2_price = current_low
                pattern.a2_bar = current_idx
        
        return pattern
    
    def check_targets_reached(self, pattern: ABCPattern, df: pd.DataFrame, 
                            current_idx: int) -> ABCPattern:
        """Check if any targets have been reached"""
        if not pattern.activated or len(pattern.take_profits) == 0:
            return pattern
        
        high_col = self._get_col(df, 'high')
        low_col = self._get_col(df, 'low')
        
        current_high = df[high_col].iloc[current_idx]
        current_low = df[low_col].iloc[current_idx]
        
        # Check if C (first target at 1.618) is reached
        if not pattern.c_reached:
            target_1618 = pattern.take_profits[0]
            
            if pattern.trend == "BULLISH" and current_high >= target_1618:
                pattern.c_reached = True
                pattern.point_c = current_high
                pattern.bar_c = current_idx
            elif pattern.trend == "BEARISH" and current_low <= target_1618:
                pattern.c_reached = True
                pattern.point_c = current_low
                pattern.bar_c = current_idx
        
        return pattern
    
    def calculate_risk_reward(self, pattern: ABCPattern) -> ABCPattern:
        """Calculate risk/reward ratio for the pattern"""
        if not pattern.entry_levels or not pattern.take_profits or not pattern.stop_loss:
            return pattern
        
        entry = pattern.entry_levels[0]  # Use first entry level
        target = pattern.take_profits[0]  # Use first target
        
        risk = abs(entry - pattern.stop_loss)
        reward = abs(target - entry)
        
        pattern.risk_reward = reward / risk if risk > 0 else 0
        
        return pattern
    
    def _get_col(self, df: pd.DataFrame, pattern: str) -> Optional[str]:
        """Get column name by pattern (case-insensitive)"""
        pattern_lower = pattern.lower()
        for col in df.columns:
            if pattern_lower in col.lower():
                return col
        return None
    
    def analyze_pattern(self, pattern: ABCPattern, df: pd.DataFrame, 
                       pip_size: float = 0.0001) -> ABCPattern:
        """
        Complete analysis of a pattern
        - Calculate entry levels
        - Calculate targets
        - Calculate stop loss
        - Calculate risk/reward
        """
        pattern = self.calculate_targets(pattern)
        pattern = self.calculate_stop_loss(pattern, pip_size)
        
        if pattern.activated and pattern.a2_price:
            pattern = self.calculate_entry_levels(pattern, df)
            pattern = self.calculate_risk_reward(pattern)
        
        return pattern
    
    def get_current_patterns(self, df: pd.DataFrame, 
                           max_patterns: int = 3) -> List[ABCPattern]:
        """
        Get most recent valid ABC patterns
        
        Returns:
            List of active patterns (not invalidated)
        """
        patterns = self.detect_abc_patterns(df)
        
        if not patterns:
            return []
        
        # Analyze each pattern
        analyzed_patterns = []
        for pattern in patterns:
            # Check activation status
            for i in range(pattern.bar_a + 1, len(df)):
                pattern = self.check_activation(pattern, df, i)
                if pattern.activated:
                    pattern = self.update_a2(pattern, df, i)
                pattern = self.check_targets_reached(pattern, df, i)
            
            # Analyze pattern
            pattern = self.analyze_pattern(pattern, df)
            analyzed_patterns.append(pattern)
        
        # Sort by bar_b (most recent first) and limit
        analyzed_patterns.sort(key=lambda p: p.bar_b, reverse=True)
        
        return analyzed_patterns[:max_patterns]

