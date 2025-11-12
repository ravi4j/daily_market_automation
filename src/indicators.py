#!/usr/bin/env python3
"""
Technical Indicators Module
Uses pandas-ta to calculate 130+ technical indicators
"""

import pandas as pd
import pandas_ta as ta
from typing import Dict, List, Optional
import numpy as np


class TechnicalIndicators:
    """
    Comprehensive technical analysis indicators using pandas-ta

    Categories:
    - Momentum: RSI, MACD, Stochastic, etc.
    - Trend: Moving Averages, ADX, Ichimoku, etc.
    - Volatility: Bollinger Bands, ATR, Keltner Channels, etc.
    - Volume: OBV, CMF, Volume Oscillator, etc.
    - Support/Resistance: Pivot Points, Fibonacci, etc.
    """

    def __init__(self, df: pd.DataFrame):
        """
        Initialize with OHLCV DataFrame

        Args:
            df: DataFrame with columns: Open, High, Low, Close, Volume
        """
        self.df = df.copy()
        self._validate_data()

    def _validate_data(self):
        """Ensure required columns exist"""
        required = ['Open', 'High', 'Low', 'Close', 'Volume']
        missing = [col for col in required if col not in self.df.columns]
        if missing:
            raise ValueError(f"Missing required columns: {missing}")

    # ==================== MOMENTUM INDICATORS ====================

    def add_rsi(self, length: int = 14) -> pd.DataFrame:
        """Relative Strength Index"""
        self.df[f'RSI_{length}'] = ta.rsi(self.df['Close'], length=length)
        return self.df

    def add_macd(self, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
        """Moving Average Convergence Divergence"""
        macd = ta.macd(self.df['Close'], fast=fast, slow=slow, signal=signal)
        self.df = pd.concat([self.df, macd], axis=1)
        return self.df

    def add_stochastic(self, k: int = 14, d: int = 3) -> pd.DataFrame:
        """Stochastic Oscillator"""
        stoch = ta.stoch(self.df['High'], self.df['Low'], self.df['Close'], k=k, d=d)
        self.df = pd.concat([self.df, stoch], axis=1)
        return self.df

    def add_stochrsi(self, length: int = 14, rsi_length: int = 14, k: int = 3, d: int = 3) -> pd.DataFrame:
        """Stochastic RSI"""
        stochrsi = ta.stochrsi(self.df['Close'], length=length, rsi_length=rsi_length, k=k, d=d)
        self.df = pd.concat([self.df, stochrsi], axis=1)
        return self.df

    def add_cci(self, length: int = 20) -> pd.DataFrame:
        """Commodity Channel Index"""
        self.df[f'CCI_{length}'] = ta.cci(self.df['High'], self.df['Low'], self.df['Close'], length=length)
        return self.df

    def add_willr(self, length: int = 14) -> pd.DataFrame:
        """Williams %R"""
        self.df[f'WILLR_{length}'] = ta.willr(self.df['High'], self.df['Low'], self.df['Close'], length=length)
        return self.df

    def add_roc(self, length: int = 12) -> pd.DataFrame:
        """Rate of Change"""
        self.df[f'ROC_{length}'] = ta.roc(self.df['Close'], length=length)
        return self.df

    def add_cmo(self, length: int = 14) -> pd.DataFrame:
        """Chande Momentum Oscillator"""
        self.df[f'CMO_{length}'] = ta.cmo(self.df['Close'], length=length)
        return self.df

    def add_fisher(self, length: int = 9) -> pd.DataFrame:
        """Fisher Transform"""
        fisher = ta.fisher(self.df['High'], self.df['Low'], length=length)
        self.df = pd.concat([self.df, fisher], axis=1)
        return self.df

    def add_ao(self) -> pd.DataFrame:
        """Awesome Oscillator"""
        self.df['AO'] = ta.ao(self.df['High'], self.df['Low'])
        return self.df

    def add_kst(self) -> pd.DataFrame:
        """Know Sure Thing"""
        kst = ta.kst(self.df['Close'])
        self.df = pd.concat([self.df, kst], axis=1)
        return self.df

    def add_tsi(self, fast: int = 13, slow: int = 25) -> pd.DataFrame:
        """True Strength Index"""
        tsi = ta.tsi(self.df['Close'], fast=fast, slow=slow)
        self.df = pd.concat([self.df, tsi], axis=1)
        return self.df

    def add_uo(self) -> pd.DataFrame:
        """Ultimate Oscillator"""
        self.df['UO'] = ta.uo(self.df['High'], self.df['Low'], self.df['Close'])
        return self.df

    # ==================== TREND INDICATORS ====================

    def add_sma(self, length: int = 20) -> pd.DataFrame:
        """Simple Moving Average"""
        self.df[f'SMA_{length}'] = ta.sma(self.df['Close'], length=length)
        return self.df

    def add_ema(self, length: int = 20) -> pd.DataFrame:
        """Exponential Moving Average"""
        self.df[f'EMA_{length}'] = ta.ema(self.df['Close'], length=length)
        return self.df

    def add_wma(self, length: int = 20) -> pd.DataFrame:
        """Weighted Moving Average"""
        self.df[f'WMA_{length}'] = ta.wma(self.df['Close'], length=length)
        return self.df

    def add_hma(self, length: int = 20) -> pd.DataFrame:
        """Hull Moving Average"""
        self.df[f'HMA_{length}'] = ta.hma(self.df['Close'], length=length)
        return self.df

    def add_alma(self, length: int = 20) -> pd.DataFrame:
        """Arnaud Legoux Moving Average"""
        self.df[f'ALMA_{length}'] = ta.alma(self.df['Close'], length=length)
        return self.df

    def add_dema(self, length: int = 20) -> pd.DataFrame:
        """Double Exponential Moving Average"""
        self.df[f'DEMA_{length}'] = ta.dema(self.df['Close'], length=length)
        return self.df

    def add_tema(self, length: int = 20) -> pd.DataFrame:
        """Triple Exponential Moving Average"""
        self.df[f'TEMA_{length}'] = ta.tema(self.df['Close'], length=length)
        return self.df

    def add_adx(self, length: int = 14) -> pd.DataFrame:
        """Average Directional Index"""
        adx = ta.adx(self.df['High'], self.df['Low'], self.df['Close'], length=length)
        self.df = pd.concat([self.df, adx], axis=1)
        return self.df

    def add_aroon(self, length: int = 25) -> pd.DataFrame:
        """Aroon Indicator"""
        aroon = ta.aroon(self.df['High'], self.df['Low'], length=length)
        self.df = pd.concat([self.df, aroon], axis=1)
        return self.df

    def add_psar(self) -> pd.DataFrame:
        """Parabolic SAR"""
        psar = ta.psar(self.df['High'], self.df['Low'], self.df['Close'])
        self.df = pd.concat([self.df, psar], axis=1)
        return self.df

    def add_supertrend(self, length: int = 7, multiplier: float = 3.0) -> pd.DataFrame:
        """SuperTrend"""
        supertrend = ta.supertrend(self.df['High'], self.df['Low'], self.df['Close'],
                                    length=length, multiplier=multiplier)
        self.df = pd.concat([self.df, supertrend], axis=1)
        return self.df

    def add_vortex(self, length: int = 14) -> pd.DataFrame:
        """Vortex Indicator"""
        vortex = ta.vortex(self.df['High'], self.df['Low'], self.df['Close'], length=length)
        self.df = pd.concat([self.df, vortex], axis=1)
        return self.df

    def add_ichimoku(self) -> pd.DataFrame:
        """Ichimoku Cloud"""
        ichimoku = ta.ichimoku(self.df['High'], self.df['Low'], self.df['Close'])[0]
        self.df = pd.concat([self.df, ichimoku], axis=1)
        return self.df

    # ==================== VOLATILITY INDICATORS ====================

    def add_bbands(self, length: int = 20, std: float = 2.0) -> pd.DataFrame:
        """Bollinger Bands"""
        bbands = ta.bbands(self.df['Close'], length=length, std=std)
        self.df = pd.concat([self.df, bbands], axis=1)
        return self.df

    def add_kc(self, length: int = 20, scalar: float = 2.0) -> pd.DataFrame:
        """Keltner Channels"""
        kc = ta.kc(self.df['High'], self.df['Low'], self.df['Close'], length=length, scalar=scalar)
        self.df = pd.concat([self.df, kc], axis=1)
        return self.df

    def add_dc(self, length: int = 20) -> pd.DataFrame:
        """Donchian Channels"""
        dc = ta.donchian(self.df['High'], self.df['Low'], length=length)
        self.df = pd.concat([self.df, dc], axis=1)
        return self.df

    def add_atr(self, length: int = 14) -> pd.DataFrame:
        """Average True Range"""
        self.df[f'ATR_{length}'] = ta.atr(self.df['High'], self.df['Low'], self.df['Close'], length=length)
        return self.df

    def add_natr(self, length: int = 14) -> pd.DataFrame:
        """Normalized Average True Range"""
        self.df[f'NATR_{length}'] = ta.natr(self.df['High'], self.df['Low'], self.df['Close'], length=length)
        return self.df

    def add_ui(self, length: int = 14) -> pd.DataFrame:
        """Ulcer Index (volatility)"""
        self.df[f'UI_{length}'] = ta.ui(self.df['Close'], length=length)
        return self.df

    # ==================== VOLUME INDICATORS ====================

    def add_obv(self) -> pd.DataFrame:
        """On Balance Volume"""
        self.df['OBV'] = ta.obv(self.df['Close'], self.df['Volume'])
        return self.df

    def add_ad(self) -> pd.DataFrame:
        """Accumulation/Distribution"""
        self.df['AD'] = ta.ad(self.df['High'], self.df['Low'], self.df['Close'], self.df['Volume'])
        return self.df

    def add_adosc(self, fast: int = 3, slow: int = 10) -> pd.DataFrame:
        """Accumulation/Distribution Oscillator (Chaikin Oscillator)"""
        self.df[f'ADOSC_{fast}_{slow}'] = ta.adosc(self.df['High'], self.df['Low'],
                                                     self.df['Close'], self.df['Volume'],
                                                     fast=fast, slow=slow)
        return self.df

    def add_cmf(self, length: int = 20) -> pd.DataFrame:
        """Chaikin Money Flow"""
        self.df[f'CMF_{length}'] = ta.cmf(self.df['High'], self.df['Low'],
                                           self.df['Close'], self.df['Volume'],
                                           length=length)
        return self.df

    def add_efi(self, length: int = 13) -> pd.DataFrame:
        """Elder's Force Index"""
        self.df[f'EFI_{length}'] = ta.efi(self.df['Close'], self.df['Volume'], length=length)
        return self.df

    def add_eom(self, length: int = 14) -> pd.DataFrame:
        """Ease of Movement"""
        eom = ta.eom(self.df['High'], self.df['Low'], self.df['Close'],
                     self.df['Volume'], length=length)
        self.df = pd.concat([self.df, eom], axis=1)
        return self.df

    def add_kvo(self, fast: int = 34, slow: int = 55) -> pd.DataFrame:
        """Klinger Volume Oscillator"""
        kvo = ta.kvo(self.df['High'], self.df['Low'], self.df['Close'],
                     self.df['Volume'], fast=fast, slow=slow)
        self.df = pd.concat([self.df, kvo], axis=1)
        return self.df

    def add_mfi(self, length: int = 14) -> pd.DataFrame:
        """Money Flow Index"""
        self.df[f'MFI_{length}'] = ta.mfi(self.df['High'], self.df['Low'],
                                           self.df['Close'], self.df['Volume'],
                                           length=length)
        return self.df

    def add_nvi(self) -> pd.DataFrame:
        """Negative Volume Index"""
        self.df['NVI'] = ta.nvi(self.df['Close'], self.df['Volume'])
        return self.df

    def add_pvi(self) -> pd.DataFrame:
        """Positive Volume Index"""
        self.df['PVI'] = ta.pvi(self.df['Close'], self.df['Volume'])
        return self.df

    def add_pvol(self) -> pd.DataFrame:
        """Price Volume"""
        self.df['PVOL'] = ta.pvol(self.df['Close'], self.df['Volume'])
        return self.df

    def add_pvt(self) -> pd.DataFrame:
        """Price Volume Trend"""
        self.df['PVT'] = ta.pvt(self.df['Close'], self.df['Volume'])
        return self.df

    def add_vwap(self) -> pd.DataFrame:
        """Volume Weighted Average Price"""
        self.df['VWAP'] = ta.vwap(self.df['High'], self.df['Low'], self.df['Close'], self.df['Volume'])
        return self.df

    def add_vwma(self, length: int = 20) -> pd.DataFrame:
        """Volume Weighted Moving Average"""
        self.df[f'VWMA_{length}'] = ta.vwma(self.df['Close'], self.df['Volume'], length=length)
        return self.df

    # ==================== STATISTICS & OTHERS ====================

    def add_zscore(self, length: int = 30) -> pd.DataFrame:
        """Z-Score"""
        self.df[f'ZS_{length}'] = ta.zscore(self.df['Close'], length=length)
        return self.df

    def add_entropy(self, length: int = 10) -> pd.DataFrame:
        """Entropy"""
        self.df[f'ENTP_{length}'] = ta.entropy(self.df['Close'], length=length)
        return self.df

    def add_mad(self, length: int = 30) -> pd.DataFrame:
        """Mean Absolute Deviation"""
        self.df[f'MAD_{length}'] = ta.mad(self.df['Close'], length=length)
        return self.df

    def add_variance(self, length: int = 30) -> pd.DataFrame:
        """Variance"""
        self.df[f'VAR_{length}'] = ta.variance(self.df['Close'], length=length)
        return self.df

    def add_stdev(self, length: int = 30) -> pd.DataFrame:
        """Standard Deviation"""
        self.df[f'STDEV_{length}'] = ta.stdev(self.df['Close'], length=length)
        return self.df

    # ==================== PRESET COMBINATIONS ====================

    def add_common_indicators(self) -> pd.DataFrame:
        """Add most commonly used indicators"""
        print("📊 Adding common indicators...")

        # Trend
        self.add_sma(20)
        self.add_sma(50)
        self.add_sma(200)
        self.add_ema(20)
        self.add_ema(50)

        # Momentum
        self.add_rsi(14)
        self.add_macd()
        self.add_stochastic()

        # Volatility
        self.add_bbands()
        self.add_atr()

        # Volume
        self.add_obv()
        self.add_cmf()
        self.add_mfi()

        # Trend Strength
        self.add_adx()

        print("✅ Common indicators added")
        return self.df

    def add_all_indicators(self) -> pd.DataFrame:
        """Add comprehensive set of indicators (may be slow for large datasets)"""
        print("📊 Adding ALL indicators (this may take a moment)...")

        # Momentum
        self.add_rsi()
        self.add_macd()
        self.add_stochastic()
        self.add_stochrsi()
        self.add_cci()
        self.add_willr()
        self.add_roc()
        self.add_cmo()
        self.add_ao()
        self.add_kst()
        self.add_tsi()
        self.add_uo()

        # Trend
        self.add_sma(20)
        self.add_sma(50)
        self.add_sma(200)
        self.add_ema(12)
        self.add_ema(26)
        self.add_ema(50)
        self.add_ema(200)
        self.add_wma(20)
        self.add_hma(20)
        self.add_dema(20)
        self.add_tema(20)
        self.add_adx()
        self.add_aroon()
        self.add_psar()
        self.add_supertrend()
        self.add_vortex()

        # Volatility
        self.add_bbands()
        self.add_kc()
        self.add_dc()
        self.add_atr()
        self.add_natr()

        # Volume
        self.add_obv()
        self.add_ad()
        self.add_adosc()
        self.add_cmf()
        self.add_efi()
        self.add_mfi()
        self.add_pvt()
        self.add_vwap()
        self.add_vwma()

        print(f"✅ All indicators added! Total columns: {len(self.df.columns)}")
        return self.df

    def get_indicator_summary(self) -> Dict:
        """Get summary of all calculated indicators"""
        indicator_cols = [col for col in self.df.columns
                         if col not in ['Open', 'High', 'Low', 'Close', 'Volume']]

        return {
            'total_indicators': len(indicator_cols),
            'indicator_names': indicator_cols,
            'data_shape': self.df.shape,
            'date_range': f"{self.df.index[0]} to {self.df.index[-1]}"
        }


# ==================== HELPER FUNCTIONS ====================

def calculate_indicators(df: pd.DataFrame, preset: str = 'common') -> pd.DataFrame:
    """
    Convenience function to calculate indicators

    Args:
        df: OHLCV DataFrame
        preset: 'common', 'all', or 'custom'

    Returns:
        DataFrame with indicators
    """
    indicators = TechnicalIndicators(df)

    if preset == 'common':
        return indicators.add_common_indicators()
    elif preset == 'all':
        return indicators.add_all_indicators()
    else:
        # Custom - add your own
        return indicators.df


def get_available_indicators() -> Dict[str, List[str]]:
    """Get list of all available indicators by category"""
    return {
        'Momentum': [
            'RSI', 'MACD', 'Stochastic', 'Stochastic RSI', 'CCI', 'Williams %R',
            'ROC', 'CMO', 'Fisher Transform', 'Awesome Oscillator', 'KST', 'TSI', 'Ultimate Oscillator'
        ],
        'Trend': [
            'SMA', 'EMA', 'WMA', 'HMA', 'ALMA', 'DEMA', 'TEMA',
            'ADX', 'Aroon', 'Parabolic SAR', 'SuperTrend', 'Vortex', 'Ichimoku'
        ],
        'Volatility': [
            'Bollinger Bands', 'Keltner Channels', 'Donchian Channels',
            'ATR', 'NATR', 'Ulcer Index'
        ],
        'Volume': [
            'OBV', 'AD', 'ADOsc', 'CMF', 'EFI', 'EOM', 'KVO', 'MFI',
            'NVI', 'PVI', 'PVOL', 'PVT', 'VWAP', 'VWMA'
        ],
        'Statistics': [
            'Z-Score', 'Entropy', 'MAD', 'Variance', 'Standard Deviation'
        ]
    }


if __name__ == "__main__":
    # Example usage
    print("📊 Technical Indicators Module")
    print("=" * 60)

    available = get_available_indicators()
    for category, indicators in available.items():
        print(f"\n{category} ({len(indicators)} indicators):")
        for indicator in indicators:
            print(f"  • {indicator}")

    print("\n" + "=" * 60)
    print("Total indicators available: ", sum(len(v) for v in available.values()))
