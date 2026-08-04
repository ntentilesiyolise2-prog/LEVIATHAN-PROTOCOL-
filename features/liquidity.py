# leviathan/features/liquidity.py
import pandas as pd
import numpy as np
from typing import Dict, Any

class LiquidityAnalyzer:
    async def compute(self, symbol: str, df: pd.DataFrame) -> Dict[str, Any]:
        if df is None or df.empty or len(df) < 20: return {}
        high = df['High']; low = df['Low']; close = df['Close']; volume = df['Volume']; price = close.iloc[-1]
        features = {}
        price_range = np.linspace(low.min(), high.max(), 20)
        volume_profile = {}
        for p in price_range:
            mask = (close > p - (p * 0.001)) & (close < p + (p * 0.001))
            volume_profile[p] = volume[mask].sum()
        if volume_profile:
            poc = max(volume_profile, key=volume_profile.get)
            features["poc"] = float(poc)
            features["poc_distance"] = (price - poc) / price * 100
            sorted_nodes = sorted(volume_profile.items(), key=lambda x: x[1], reverse=True)
            features["hv_node1"] = float(sorted_nodes[0][0]) if len(sorted_nodes) > 0 else 0
            features["hv_node2"] = float(sorted_nodes[1][0]) if len(sorted_nodes) > 1 else 0
            features["hv_node3"] = float(sorted_nodes[2][0]) if len(sorted_nodes) > 2 else 0
        delta = volume * (close - (high + low) / 2) / price
        features["cumulative_delta"] = float(delta.sum())
        features["delta_trend"] = "BUY" if delta.sum() > 0 else "SELL"
        up_volume = volume[close > close.shift(1)].sum()
        down_volume = volume[close < close.shift(1)].sum()
        if up_volume + down_volume > 0:
            features["buy_volume_ratio"] = up_volume / (up_volume + down_volume)
            features["sell_volume_ratio"] = down_volume / (up_volume + down_volume)
        features["volume_imbalance"] = (up_volume - down_volume) / (up_volume + down_volume + 1)
        typical = (high + low + close) / 3
        vwap = (typical * volume).cumsum() / volume.cumsum()
        if len(vwap) > 0:
            features["vwap"] = float(vwap.iloc[-1])
            features["vwap_side"] = "ABOVE" if price > vwap.iloc[-1] else "BELOW"
        if "poc" in features:
            std = price * 0.01
            features["liquidity_zone_high"] = features["poc"] + std
            features["liquidity_zone_low"] = features["poc"] - std
            features["in_liquidity_zone"] = features["liquidity_zone_low"] <= price <= features["liquidity_zone_high"]
        return features
