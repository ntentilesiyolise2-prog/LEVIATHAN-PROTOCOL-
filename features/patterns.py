# leviathan/features/patterns.py
import pandas as pd
import numpy as np
from typing import Dict, Any, List

class PatternDetector:
    def detect(self, df: pd.DataFrame) -> Dict[str, Any]:
        if df is None or len(df) < 30: return {}
        close = df['Close']; high = df['High']; low = df['Low']
        features = {}
        swing_highs = self._find_swing_highs(high)
        swing_lows = self._find_swing_lows(low)
        if len(swing_highs) >= 3:
            h1,h2,h3 = swing_highs[-3], swing_highs[-2], swing_highs[-1]
            if h2 > h1 and h2 > h3 and abs(h1 - h3) / h2 < 0.05:
                features["pattern_head_shoulders"] = "BEARISH"
                features["pattern_hs_confidence"] = 70
        if len(swing_lows) >= 3:
            l1,l2,l3 = swing_lows[-3], swing_lows[-2], swing_lows[-1]
            if l2 < l1 and l2 < l3 and abs(l1 - l3) / l2 < 0.05:
                features["pattern_inverse_head_shoulders"] = "BULLISH"
                features["pattern_ihs_confidence"] = 70
        if len(swing_highs) >= 2:
            if abs(swing_highs[-1] - swing_highs[-2]) / swing_highs[-2] < 0.02:
                features["pattern_double_top"] = "BEARISH"
        if len(swing_lows) >= 2:
            if abs(swing_lows[-1] - swing_lows[-2]) / swing_lows[-2] < 0.02:
                features["pattern_double_bottom"] = "BULLISH"
        recent_high = high.iloc[-20:].max()
        recent_low = low.iloc[-20:].min()
        range_pct = (recent_high - recent_low) / recent_low
        if range_pct < 0.02 and len(close) > 50:
            features["pattern_triangle"] = "BREAKOUT_PENDING"
            features["triangle_range_pct"] = range_pct * 100
            momentum = close.iloc[-1] - close.iloc[-10] if len(close) > 10 else 0
            features["triangle_momentum"] = "BULLISH" if momentum > 0 else "BEARISH"
        return features

    def _find_swing_highs(self, series):
        highs = []
        for i in range(2, len(series)-2):
            if series.iloc[i] > series.iloc[i-1] and series.iloc[i] > series.iloc[i-2] and series.iloc[i] > series.iloc[i+1] and series.iloc[i] > series.iloc[i+2]:
                highs.append(series.iloc[i])
        return highs

    def _find_swing_lows(self, series):
        lows = []
        for i in range(2, len(series)-2):
            if series.iloc[i] < series.iloc[i-1] and series.iloc[i] < series.iloc[i-2] and series.iloc[i] < series.iloc[i+1] and series.iloc[i] < series.iloc[i+2]:
                lows.append(series.iloc[i])
        return lows
