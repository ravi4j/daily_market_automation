#!/usr/bin/env python3
"""
Strategy Generator - Automatically create and test strategies for all indicators

This module generates trading strategies based on individual indicators and combinations,
then backtests them to find the most profitable ones.
"""

from dataclasses import dataclass
from typing import List, Dict, Callable, Optional
import pandas as pd
import numpy as np


@dataclass
class StrategyTemplate:
    """Template for generating a trading strategy"""
    name: str
    description: str
    category: str  # momentum, trend, volatility, volume
    signal_function: Callable
    required_indicators: List[str]
    default_params: Dict


class StrategyGenerator:
    """Generate trading strategies from technical indicators"""
    
    def __init__(self):
        self.strategies = []
        self._register_all_strategies()
    
    def _register_all_strategies(self):
        """Register all built-in strategy templates"""
        
        # ==================== MOMENTUM STRATEGIES ====================
        
        # RSI Strategies
        self.strategies.append(StrategyTemplate(
            name="RSI_Oversold_Bounce",
            description="Buy when RSI crosses above 30 (oversold), sell above 70",
            category="momentum",
            signal_function=self._rsi_oversold_bounce,
            required_indicators=["RSI_14"],
            default_params={"oversold": 30, "overbought": 70}
        ))
        
        self.strategies.append(StrategyTemplate(
            name="RSI_Momentum",
            description="Buy when RSI > 50 and rising, sell when < 50",
            category="momentum",
            signal_function=self._rsi_momentum,
            required_indicators=["RSI_14"],
            default_params={"threshold": 50}
        ))
        
        self.strategies.append(StrategyTemplate(
            name="RSI_Extreme",
            description="Contrarian: buy extreme oversold (<20), sell extreme overbought (>80)",
            category="momentum",
            signal_function=self._rsi_extreme,
            required_indicators=["RSI_14"],
            default_params={"extreme_oversold": 20, "extreme_overbought": 80}
        ))
        
        # Stochastic Strategies
        self.strategies.append(StrategyTemplate(
            name="Stochastic_CrossOver",
            description="Buy when %K crosses above %D in oversold zone",
            category="momentum",
            signal_function=self._stochastic_crossover,
            required_indicators=["STOCHk_14_3_3", "STOCHd_14_3_3"],
            default_params={"oversold": 20, "overbought": 80}
        ))
        
        # MACD Strategies
        self.strategies.append(StrategyTemplate(
            name="MACD_CrossOver",
            description="Buy when MACD crosses above signal, sell when crosses below",
            category="momentum",
            signal_function=self._macd_crossover,
            required_indicators=["MACD_12_26_9", "MACDs_12_26_9"],
            default_params={}
        ))
        
        self.strategies.append(StrategyTemplate(
            name="MACD_Histogram",
            description="Buy when histogram turns positive and growing",
            category="momentum",
            signal_function=self._macd_histogram,
            required_indicators=["MACDh_12_26_9"],
            default_params={}
        ))
        
        self.strategies.append(StrategyTemplate(
            name="MACD_Zero_Cross",
            description="Buy when MACD crosses above zero line",
            category="momentum",
            signal_function=self._macd_zero_cross,
            required_indicators=["MACD_12_26_9"],
            default_params={}
        ))
        
        # CCI Strategy
        self.strategies.append(StrategyTemplate(
            name="CCI_Reversal",
            description="Buy when CCI crosses above -100, sell above +100",
            category="momentum",
            signal_function=self._cci_reversal,
            required_indicators=["CCI_14"],
            default_params={"oversold": -100, "overbought": 100}
        ))
        
        # Williams %R Strategy
        self.strategies.append(StrategyTemplate(
            name="Williams_R",
            description="Buy when Williams %R crosses above -80",
            category="momentum",
            signal_function=self._williams_r,
            required_indicators=["WILLR_14"],
            default_params={"oversold": -80, "overbought": -20}
        ))
        
        # ROC Strategy
        self.strategies.append(StrategyTemplate(
            name="ROC_Momentum",
            description="Buy when Rate of Change turns positive",
            category="momentum",
            signal_function=self._roc_momentum,
            required_indicators=["ROC_10"],
            default_params={}
        ))
        
        # ==================== TREND STRATEGIES ====================
        
        # Moving Average Crossovers
        self.strategies.append(StrategyTemplate(
            name="SMA_Golden_Cross",
            description="Buy when 50 SMA crosses above 200 SMA (golden cross)",
            category="trend",
            signal_function=self._sma_golden_cross,
            required_indicators=["SMA_50", "SMA_200"],
            default_params={}
        ))
        
        self.strategies.append(StrategyTemplate(
            name="EMA_Fast_Cross",
            description="Buy when 12 EMA crosses above 26 EMA",
            category="trend",
            signal_function=self._ema_fast_cross,
            required_indicators=["EMA_12", "EMA_26"],
            default_params={}
        ))
        
        self.strategies.append(StrategyTemplate(
            name="SMA_Triple_Cross",
            description="Buy when 20 > 50 > 200 SMA (all aligned)",
            category="trend",
            signal_function=self._sma_triple_cross,
            required_indicators=["SMA_20", "SMA_50", "SMA_200"],
            default_params={}
        ))
        
        self.strategies.append(StrategyTemplate(
            name="Price_Above_SMA",
            description="Buy when price crosses above 20 SMA with momentum",
            category="trend",
            signal_function=self._price_above_sma,
            required_indicators=["SMA_20"],
            default_params={}
        ))
        
        # ADX Strategies
        self.strategies.append(StrategyTemplate(
            name="ADX_Strong_Trend",
            description="Buy when ADX > 25 and +DI > -DI (strong uptrend)",
            category="trend",
            signal_function=self._adx_strong_trend,
            required_indicators=["ADX_14", "DMP_14", "DMN_14"],
            default_params={"adx_threshold": 25}
        ))
        
        self.strategies.append(StrategyTemplate(
            name="ADX_Trend_Start",
            description="Buy when ADX crosses above 20 (trend starting)",
            category="trend",
            signal_function=self._adx_trend_start,
            required_indicators=["ADX_14", "DMP_14", "DMN_14"],
            default_params={}
        ))
        
        # Aroon Strategy
        self.strategies.append(StrategyTemplate(
            name="Aroon_Crossover",
            description="Buy when Aroon Up crosses above Aroon Down",
            category="trend",
            signal_function=self._aroon_crossover,
            required_indicators=["AROOND_25", "AROONU_25"],
            default_params={}
        ))
        
        # Supertrend Strategy
        self.strategies.append(StrategyTemplate(
            name="Supertrend_Follow",
            description="Buy when Supertrend turns bullish",
            category="trend",
            signal_function=self._supertrend_follow,
            required_indicators=["SUPERT_7_3.0", "SUPERTd_7_3.0"],
            default_params={}
        ))
        
        # ==================== VOLATILITY STRATEGIES ====================
        
        # Bollinger Bands Strategies
        self.strategies.append(StrategyTemplate(
            name="BB_Bounce",
            description="Buy when price touches lower band and bounces",
            category="volatility",
            signal_function=self._bb_bounce,
            required_indicators=["BBL_20_2.0", "BBM_20_2.0", "BBU_20_2.0"],
            default_params={}
        ))
        
        self.strategies.append(StrategyTemplate(
            name="BB_Squeeze_Breakout",
            description="Buy when bands squeeze then price breaks upper band",
            category="volatility",
            signal_function=self._bb_squeeze_breakout,
            required_indicators=["BBL_20_2.0", "BBM_20_2.0", "BBU_20_2.0"],
            default_params={}
        ))
        
        self.strategies.append(StrategyTemplate(
            name="BB_Width_Expansion",
            description="Buy when BB width starts expanding with price momentum",
            category="volatility",
            signal_function=self._bb_width_expansion,
            required_indicators=["BBL_20_2.0", "BBU_20_2.0"],
            default_params={}
        ))
        
        # Keltner Channel Strategy
        self.strategies.append(StrategyTemplate(
            name="Keltner_Breakout",
            description="Buy when price breaks above upper Keltner Channel",
            category="volatility",
            signal_function=self._keltner_breakout,
            required_indicators=["KCLe_20_2", "KCBe_20_2", "KCUe_20_2"],
            default_params={}
        ))
        
        # ATR Strategy
        self.strategies.append(StrategyTemplate(
            name="ATR_Volatility_Breakout",
            description="Buy when price moves > 2x ATR from recent low",
            category="volatility",
            signal_function=self._atr_volatility_breakout,
            required_indicators=["ATRr_14"],
            default_params={}
        ))
        
        # ==================== VOLUME STRATEGIES ====================
        
        # OBV Strategy
        self.strategies.append(StrategyTemplate(
            name="OBV_Trend",
            description="Buy when OBV is rising with price",
            category="volume",
            signal_function=self._obv_trend,
            required_indicators=["OBV"],
            default_params={}
        ))
        
        # Volume SMA Strategy
        self.strategies.append(StrategyTemplate(
            name="Volume_Surge",
            description="Buy when volume > 2x average with price up",
            category="volume",
            signal_function=self._volume_surge,
            required_indicators=["Volume"],
            default_params={"multiplier": 2}
        ))
        
        # MFI Strategy
        self.strategies.append(StrategyTemplate(
            name="MFI_Flow",
            description="Buy when MFI crosses above 20 (money flowing in)",
            category="volume",
            signal_function=self._mfi_flow,
            required_indicators=["MFI_14"],
            default_params={}
        ))
        
        # ==================== COMBINATION STRATEGIES ====================
        
        self.strategies.append(StrategyTemplate(
            name="Trend_Momentum_Combo",
            description="Buy when trend (ADX) + momentum (RSI) aligned",
            category="combination",
            signal_function=self._trend_momentum_combo,
            required_indicators=["ADX_14", "DMP_14", "DMN_14", "RSI_14"],
            default_params={}
        ))
        
        self.strategies.append(StrategyTemplate(
            name="MA_MACD_Combo",
            description="Buy when price > SMA and MACD bullish",
            category="combination",
            signal_function=self._ma_macd_combo,
            required_indicators=["SMA_20", "MACD_12_26_9", "MACDs_12_26_9"],
            default_params={}
        ))
        
        self.strategies.append(StrategyTemplate(
            name="BB_RSI_Combo",
            description="Buy when at BB lower band with oversold RSI",
            category="combination",
            signal_function=self._bb_rsi_combo,
            required_indicators=["BBL_20_2.0", "BBM_20_2.0", "RSI_14"],
            default_params={}
        ))
    
    # ==================== STRATEGY IMPLEMENTATIONS ====================
    
    def _get_col(self, df: pd.DataFrame, pattern: str) -> Optional[str]:
        """Find column name matching pattern (case-insensitive, handles pandas-ta suffixes)"""
        pattern_lower = pattern.lower()
        for col in df.columns:
            if pattern_lower in col.lower():
                return col
        return None
    
    def _rsi_oversold_bounce(self, df: pd.DataFrame, params: Dict) -> pd.Series:
        """RSI oversold bounce strategy"""
        rsi_col = self._get_col(df, 'rsi')
        if not rsi_col:
            return pd.Series(0, index=df.index)
        
        rsi = df[rsi_col]
        signals = pd.Series(0, index=df.index)
        signals[rsi < params['oversold']] = 1  # Buy oversold
        signals[rsi > params['overbought']] = -1  # Sell overbought
        return signals
    
    def _rsi_momentum(self, df: pd.DataFrame, params: Dict) -> pd.Series:
        """RSI momentum strategy"""
        rsi_col = self._get_col(df, 'rsi')
        if not rsi_col:
            return pd.Series(0, index=df.index)
        
        rsi = df[rsi_col]
        rsi_diff = rsi.diff()
        signals = pd.Series(0, index=df.index)
        signals[(rsi > params['threshold']) & (rsi_diff > 0)] = 1
        signals[rsi < params['threshold']] = -1
        return signals
    
    def _rsi_extreme(self, df: pd.DataFrame, params: Dict) -> pd.Series:
        """RSI extreme contrarian strategy"""
        rsi_col = self._get_col(df, 'rsi')
        if not rsi_col:
            return pd.Series(0, index=df.index)
        
        rsi = df[rsi_col]
        signals = pd.Series(0, index=df.index)
        signals[rsi < params['extreme_oversold']] = 1
        signals[rsi > params['extreme_overbought']] = -1
        return signals
    
    def _stochastic_crossover(self, df: pd.DataFrame, params: Dict) -> pd.Series:
        """Stochastic crossover strategy"""
        k_col = self._get_col(df, 'stochk')
        d_col = self._get_col(df, 'stochd')
        if not k_col or not d_col:
            return pd.Series(0, index=df.index)
        
        k = df[k_col]
        d = df[d_col]
        signals = pd.Series(0, index=df.index)
        
        # Buy when %K crosses above %D in oversold zone
        cross_up = (k > d) & (k.shift(1) <= d.shift(1)) & (k < params['oversold'])
        cross_down = (k < d) & (k.shift(1) >= d.shift(1)) & (k > params['overbought'])
        
        signals[cross_up] = 1
        signals[cross_down] = -1
        return signals
    
    def _macd_crossover(self, df: pd.DataFrame, params: Dict) -> pd.Series:
        """MACD crossover strategy"""
        macd_col = self._get_col(df, 'macd_12')
        signal_col = self._get_col(df, 'macds_12')
        if not macd_col or not signal_col:
            return pd.Series(0, index=df.index)
        
        macd = df[macd_col]
        signal = df[signal_col]
        signals = pd.Series(0, index=df.index)
        
        cross_up = (macd > signal) & (macd.shift(1) <= signal.shift(1))
        cross_down = (macd < signal) & (macd.shift(1) >= signal.shift(1))
        
        signals[cross_up] = 1
        signals[cross_down] = -1
        return signals
    
    def _macd_histogram(self, df: pd.DataFrame, params: Dict) -> pd.Series:
        """MACD histogram strategy"""
        hist_col = self._get_col(df, 'macdh')
        if not hist_col:
            return pd.Series(0, index=df.index)
        
        hist = df[hist_col]
        hist_diff = hist.diff()
        signals = pd.Series(0, index=df.index)
        
        signals[(hist > 0) & (hist_diff > 0)] = 1  # Positive and growing
        signals[(hist < 0) & (hist_diff < 0)] = -1  # Negative and falling
        return signals
    
    def _macd_zero_cross(self, df: pd.DataFrame, params: Dict) -> pd.Series:
        """MACD zero line crossover"""
        macd_col = self._get_col(df, 'macd_12')
        if not macd_col:
            return pd.Series(0, index=df.index)
        
        macd = df[macd_col]
        signals = pd.Series(0, index=df.index)
        
        signals[(macd > 0) & (macd.shift(1) <= 0)] = 1
        signals[(macd < 0) & (macd.shift(1) >= 0)] = -1
        return signals
    
    def _cci_reversal(self, df: pd.DataFrame, params: Dict) -> pd.Series:
        """CCI reversal strategy"""
        cci_col = self._get_col(df, 'cci')
        if not cci_col:
            return pd.Series(0, index=df.index)
        
        cci = df[cci_col]
        signals = pd.Series(0, index=df.index)
        signals[cci < params['oversold']] = 1
        signals[cci > params['overbought']] = -1
        return signals
    
    def _williams_r(self, df: pd.DataFrame, params: Dict) -> pd.Series:
        """Williams %R strategy"""
        willr_col = self._get_col(df, 'willr')
        if not willr_col:
            return pd.Series(0, index=df.index)
        
        willr = df[willr_col]
        signals = pd.Series(0, index=df.index)
        signals[willr < params['oversold']] = 1
        signals[willr > params['overbought']] = -1
        return signals
    
    def _roc_momentum(self, df: pd.DataFrame, params: Dict) -> pd.Series:
        """Rate of Change momentum"""
        roc_col = self._get_col(df, 'roc')
        if not roc_col:
            return pd.Series(0, index=df.index)
        
        roc = df[roc_col]
        signals = pd.Series(0, index=df.index)
        signals[(roc > 0) & (roc.shift(1) <= 0)] = 1
        signals[(roc < 0) & (roc.shift(1) >= 0)] = -1
        return signals
    
    def _sma_golden_cross(self, df: pd.DataFrame, params: Dict) -> pd.Series:
        """Golden cross: 50 SMA crosses 200 SMA"""
        sma50_col = self._get_col(df, 'sma_50')
        sma200_col = self._get_col(df, 'sma_200')
        if not sma50_col or not sma200_col:
            return pd.Series(0, index=df.index)
        
        sma50 = df[sma50_col]
        sma200 = df[sma200_col]
        signals = pd.Series(0, index=df.index)
        
        signals[(sma50 > sma200) & (sma50.shift(1) <= sma200.shift(1))] = 1
        signals[(sma50 < sma200) & (sma50.shift(1) >= sma200.shift(1))] = -1
        return signals
    
    def _ema_fast_cross(self, df: pd.DataFrame, params: Dict) -> pd.Series:
        """Fast EMA crossover"""
        ema12_col = self._get_col(df, 'ema_12')
        ema26_col = self._get_col(df, 'ema_26')
        if not ema12_col or not ema26_col:
            return pd.Series(0, index=df.index)
        
        ema12 = df[ema12_col]
        ema26 = df[ema26_col]
        signals = pd.Series(0, index=df.index)
        
        signals[(ema12 > ema26) & (ema12.shift(1) <= ema26.shift(1))] = 1
        signals[(ema12 < ema26) & (ema12.shift(1) >= ema26.shift(1))] = -1
        return signals
    
    def _sma_triple_cross(self, df: pd.DataFrame, params: Dict) -> pd.Series:
        """Triple SMA alignment"""
        sma20_col = self._get_col(df, 'sma_20')
        sma50_col = self._get_col(df, 'sma_50')
        sma200_col = self._get_col(df, 'sma_200')
        if not all([sma20_col, sma50_col, sma200_col]):
            return pd.Series(0, index=df.index)
        
        sma20 = df[sma20_col]
        sma50 = df[sma50_col]
        sma200 = df[sma200_col]
        signals = pd.Series(0, index=df.index)
        
        signals[(sma20 > sma50) & (sma50 > sma200)] = 1
        signals[(sma20 < sma50) & (sma50 < sma200)] = -1
        return signals
    
    def _price_above_sma(self, df: pd.DataFrame, params: Dict) -> pd.Series:
        """Price crosses above SMA"""
        sma20_col = self._get_col(df, 'sma_20')
        close_col = self._get_col(df, 'close')
        if not sma20_col or not close_col:
            return pd.Series(0, index=df.index)
        
        close = df[close_col]
        sma20 = df[sma20_col]
        signals = pd.Series(0, index=df.index)
        
        signals[(close > sma20) & (close.shift(1) <= sma20.shift(1))] = 1
        signals[(close < sma20) & (close.shift(1) >= sma20.shift(1))] = -1
        return signals
    
    def _adx_strong_trend(self, df: pd.DataFrame, params: Dict) -> pd.Series:
        """ADX strong trend strategy"""
        adx_col = self._get_col(df, 'adx')
        dmp_col = self._get_col(df, 'dmp')
        dmn_col = self._get_col(df, 'dmn')
        if not all([adx_col, dmp_col, dmn_col]):
            return pd.Series(0, index=df.index)
        
        adx = df[adx_col]
        dmp = df[dmp_col]
        dmn = df[dmn_col]
        signals = pd.Series(0, index=df.index)
        
        signals[(adx > params['adx_threshold']) & (dmp > dmn)] = 1
        signals[(adx > params['adx_threshold']) & (dmp < dmn)] = -1
        return signals
    
    def _adx_trend_start(self, df: pd.DataFrame, params: Dict) -> pd.Series:
        """ADX trend start strategy"""
        adx_col = self._get_col(df, 'adx')
        dmp_col = self._get_col(df, 'dmp')
        dmn_col = self._get_col(df, 'dmn')
        if not all([adx_col, dmp_col, dmn_col]):
            return pd.Series(0, index=df.index)
        
        adx = df[adx_col]
        dmp = df[dmp_col]
        dmn = df[dmn_col]
        signals = pd.Series(0, index=df.index)
        
        adx_cross = (adx > 20) & (adx.shift(1) <= 20)
        signals[adx_cross & (dmp > dmn)] = 1
        signals[adx_cross & (dmp < dmn)] = -1
        return signals
    
    def _aroon_crossover(self, df: pd.DataFrame, params: Dict) -> pd.Series:
        """Aroon crossover strategy"""
        aroon_up_col = self._get_col(df, 'aroonu')
        aroon_down_col = self._get_col(df, 'aroond')
        if not aroon_up_col or not aroon_down_col:
            return pd.Series(0, index=df.index)
        
        aroon_up = df[aroon_up_col]
        aroon_down = df[aroon_down_col]
        signals = pd.Series(0, index=df.index)
        
        signals[(aroon_up > aroon_down) & (aroon_up.shift(1) <= aroon_down.shift(1))] = 1
        signals[(aroon_up < aroon_down) & (aroon_up.shift(1) >= aroon_down.shift(1))] = -1
        return signals
    
    def _supertrend_follow(self, df: pd.DataFrame, params: Dict) -> pd.Series:
        """Supertrend following strategy"""
        direction_col = self._get_col(df, 'supertd')
        if not direction_col:
            return pd.Series(0, index=df.index)
        
        direction = df[direction_col]
        signals = pd.Series(0, index=df.index)
        
        signals[(direction == 1) & (direction.shift(1) == -1)] = 1
        signals[(direction == -1) & (direction.shift(1) == 1)] = -1
        return signals
    
    def _bb_bounce(self, df: pd.DataFrame, params: Dict) -> pd.Series:
        """Bollinger Band bounce strategy"""
        bbl_col = self._get_col(df, 'bbl_20')
        bbm_col = self._get_col(df, 'bbm_20')
        close_col = self._get_col(df, 'close')
        if not all([bbl_col, bbm_col, close_col]):
            return pd.Series(0, index=df.index)
        
        close = df[close_col]
        bbl = df[bbl_col]
        bbm = df[bbm_col]
        signals = pd.Series(0, index=df.index)
        
        # Buy when price touches lower band and moves back up
        touch_lower = close <= bbl * 1.01
        bounce = close > close.shift(1)
        signals[touch_lower & bounce] = 1
        signals[close > bbm * 1.02] = -1
        return signals
    
    def _bb_squeeze_breakout(self, df: pd.DataFrame, params: Dict) -> pd.Series:
        """Bollinger Band squeeze breakout"""
        bbl_col = self._get_col(df, 'bbl_20')
        bbu_col = self._get_col(df, 'bbu_20')
        close_col = self._get_col(df, 'close')
        if not all([bbl_col, bbu_col, close_col]):
            return pd.Series(0, index=df.index)
        
        close = df[close_col]
        bbu = df[bbu_col]
        bbl = df[bbl_col]
        bb_width = (bbu - bbl) / bbl
        signals = pd.Series(0, index=df.index)
        
        # Squeeze: BB width in lowest 20%
        squeeze = bb_width < bb_width.rolling(50).quantile(0.2)
        breakout = close > bbu
        signals[squeeze.shift(1) & breakout] = 1
        return signals
    
    def _bb_width_expansion(self, df: pd.DataFrame, params: Dict) -> pd.Series:
        """Bollinger Band width expansion"""
        bbl_col = self._get_col(df, 'bbl_20')
        bbu_col = self._get_col(df, 'bbu_20')
        close_col = self._get_col(df, 'close')
        if not all([bbl_col, bbu_col, close_col]):
            return pd.Series(0, index=df.index)
        
        close = df[close_col]
        bbu = df[bbu_col]
        bbl = df[bbl_col]
        bb_width = (bbu - bbl) / bbl
        width_expanding = bb_width > bb_width.shift(1)
        price_rising = close > close.shift(1)
        
        signals = pd.Series(0, index=df.index)
        signals[width_expanding & price_rising] = 1
        return signals
    
    def _keltner_breakout(self, df: pd.DataFrame, params: Dict) -> pd.Series:
        """Keltner Channel breakout"""
        kcu_col = self._get_col(df, 'kcue_20')
        close_col = self._get_col(df, 'close')
        if not kcu_col or not close_col:
            return pd.Series(0, index=df.index)
        
        close = df[close_col]
        kcu = df[kcu_col]
        signals = pd.Series(0, index=df.index)
        
        signals[(close > kcu) & (close.shift(1) <= kcu.shift(1))] = 1
        return signals
    
    def _atr_volatility_breakout(self, df: pd.DataFrame, params: Dict) -> pd.Series:
        """ATR volatility breakout"""
        atr_col = self._get_col(df, 'atrr_14')
        close_col = self._get_col(df, 'close')
        if not atr_col or not close_col:
            return pd.Series(0, index=df.index)
        
        close = df[close_col]
        atr = df[atr_col]
        low_10 = close.rolling(10).min()
        move = close - low_10
        
        signals = pd.Series(0, index=df.index)
        signals[move > 2 * atr] = 1
        return signals
    
    def _obv_trend(self, df: pd.DataFrame, params: Dict) -> pd.Series:
        """OBV trend strategy"""
        obv_col = self._get_col(df, 'obv')
        close_col = self._get_col(df, 'close')
        if not obv_col or not close_col:
            return pd.Series(0, index=df.index)
        
        obv = df[obv_col]
        close = df[close_col]
        obv_ma = obv.rolling(20).mean()
        
        signals = pd.Series(0, index=df.index)
        signals[(obv > obv_ma) & (close > close.shift(1))] = 1
        signals[(obv < obv_ma) & (close < close.shift(1))] = -1
        return signals
    
    def _volume_surge(self, df: pd.DataFrame, params: Dict) -> pd.Series:
        """Volume surge strategy"""
        volume_col = self._get_col(df, 'volume')
        close_col = self._get_col(df, 'close')
        if not volume_col or not close_col:
            return pd.Series(0, index=df.index)
        
        volume = df[volume_col]
        close = df[close_col]
        vol_ma = volume.rolling(20).mean()
        
        signals = pd.Series(0, index=df.index)
        surge = volume > params['multiplier'] * vol_ma
        price_up = close > close.shift(1)
        signals[surge & price_up] = 1
        return signals
    
    def _mfi_flow(self, df: pd.DataFrame, params: Dict) -> pd.Series:
        """Money Flow Index strategy"""
        mfi_col = self._get_col(df, 'mfi')
        if not mfi_col:
            return pd.Series(0, index=df.index)
        
        mfi = df[mfi_col]
        signals = pd.Series(0, index=df.index)
        signals[(mfi > 20) & (mfi.shift(1) <= 20)] = 1
        signals[(mfi < 80) & (mfi.shift(1) >= 80)] = -1
        return signals
    
    def _trend_momentum_combo(self, df: pd.DataFrame, params: Dict) -> pd.Series:
        """Trend + Momentum combination"""
        adx_col = self._get_col(df, 'adx')
        dmp_col = self._get_col(df, 'dmp')
        dmn_col = self._get_col(df, 'dmn')
        rsi_col = self._get_col(df, 'rsi')
        if not all([adx_col, dmp_col, dmn_col, rsi_col]):
            return pd.Series(0, index=df.index)
        
        adx = df[adx_col]
        dmp = df[dmp_col]
        dmn = df[dmn_col]
        rsi = df[rsi_col]
        
        signals = pd.Series(0, index=df.index)
        signals[(adx > 25) & (dmp > dmn) & (rsi > 50)] = 1
        signals[(adx > 25) & (dmp < dmn) & (rsi < 50)] = -1
        return signals
    
    def _ma_macd_combo(self, df: pd.DataFrame, params: Dict) -> pd.Series:
        """MA + MACD combination"""
        sma20_col = self._get_col(df, 'sma_20')
        macd_col = self._get_col(df, 'macd_12')
        signal_col = self._get_col(df, 'macds_12')
        close_col = self._get_col(df, 'close')
        if not all([sma20_col, macd_col, signal_col, close_col]):
            return pd.Series(0, index=df.index)
        
        close = df[close_col]
        sma20 = df[sma20_col]
        macd = df[macd_col]
        signal = df[signal_col]
        
        signals = pd.Series(0, index=df.index)
        signals[(close > sma20) & (macd > signal)] = 1
        signals[(close < sma20) & (macd < signal)] = -1
        return signals
    
    def _bb_rsi_combo(self, df: pd.DataFrame, params: Dict) -> pd.Series:
        """Bollinger Bands + RSI combination"""
        bbl_col = self._get_col(df, 'bbl_20')
        bbm_col = self._get_col(df, 'bbm_20')
        rsi_col = self._get_col(df, 'rsi')
        close_col = self._get_col(df, 'close')
        if not all([bbl_col, bbm_col, rsi_col, close_col]):
            return pd.Series(0, index=df.index)
        
        close = df[close_col]
        bbl = df[bbl_col]
        bbm = df[bbm_col]
        rsi = df[rsi_col]
        
        signals = pd.Series(0, index=df.index)
        signals[(close <= bbl * 1.01) & (rsi < 30)] = 1
        signals[close > bbm * 1.02] = -1
        return signals
    
    def get_all_strategies(self) -> List[StrategyTemplate]:
        """Get all registered strategies"""
        return self.strategies
    
    def get_strategies_by_category(self, category: str) -> List[StrategyTemplate]:
        """Get strategies filtered by category"""
        return [s for s in self.strategies if s.category == category]
    
    def generate_signal(self, strategy: StrategyTemplate, df: pd.DataFrame, 
                       params: Optional[Dict] = None) -> pd.Series:
        """Generate trading signals for a given strategy"""
        if params is None:
            params = strategy.default_params
        return strategy.signal_function(df, params)

