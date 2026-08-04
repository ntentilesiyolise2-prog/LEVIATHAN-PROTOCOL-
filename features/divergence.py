# leviathan/features/divergence.py
import pandas as pd
import ta

class DivergenceDetector:
    def compute(self, df: pd.DataFrame) -> dict:
        if df is None or len(df) < 50: return {}
        close = df['Close']; features = {}
        rsi = ta.rsi(close, length=14)
        if len(rsi) >= 20:
            price_lows = self._find_swing_lows(close)
            rsi_lows = self._find_swing_lows(rsi)
            if len(price_lows) >= 2 and len(rsi_lows) >= 2:
                p1,p2 = price_lows[-2], price_lows[-1]
                r1,r2 = rsi_lows[-2], rsi_lows[-1]
                if p1 < p2 and r1 > r2:
                    features["divergence_bullish_rsi"] = True
                elif p1 > p2 and r1 < r2:
                    features["divergence_bearish_rsi"] = True
        macd = ta.macd(close)
        if len(macd) >= 20:
            price_highs = self._find_swing_highs(close)
            macd_highs = self._find_swing_highs(macd)
            if len(price_highs) >= 2 and len(macd_highs) >= 2:
                p1,p2 = price_highs[-2], price_highs[-1]
                m1,m2 = macd_highs[-2], macd_highs[-1]
                if p1 < p2 and m1 > m2:
                    features["divergence_bullish_macd"] = True
                elif p1 > p2 and m1 < m2:
                    features["divergence_bearish_macd"] = True
        return features

    def _find_swing_lows(self, series):
        lows = []
        for i in range(2, len(series)-2):
            if series.iloc[i] < series.iloc[i-1] and series.iloc[i] < series.iloc[i-2] and series.iloc[i] < series.iloc[i+1] and series.iloc[i] < series.iloc[i+2]:
                lows.append(series.iloc[i])
        return lows

    def _find_swing_highs(self, series):
        highs = []
        for i in range(2, len(series)-2):
            if series.iloc[i] > series.iloc[i-1] and series.iloc[i] > series.iloc[i-2] and series.iloc[i] > series.iloc[i+1] and series.iloc[i] > series.iloc[i+2]:
                highs.append(series.iloc[i])
        return highs
