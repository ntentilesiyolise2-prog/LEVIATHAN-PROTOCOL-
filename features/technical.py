# leviathan/features/technical.py
import pandas as pd
import numpy as np
import ta

class TechnicalFeatures:
    def compute_all(self, df: pd.DataFrame) -> dict:
        if df is None or df.empty or len(df) < 20:
            return {}
        close = df['Close']; high = df['High']; low = df['Low']; volume = df['Volume']; price = close.iloc[-1]
        features = {}
        for period in [20,50,100,200]:
            ema = ta.ema(close, length=period)
            if len(ema) > 0:
                features[f"ema_{period}"] = float(ema.iloc[-1])
                features[f"price_vs_ema_{period}"] = float(price - ema.iloc[-1])
        for period in [20,50,100]:
            sma = ta.sma(close, length=period)
            if len(sma) > 0: features[f"sma_{period}"] = float(sma.iloc[-1])
        macd = ta.macd(close)
        features["macd"] = float(macd.iloc[-1])
        features["macd_signal"] = float(ta.macd_signal(close).iloc[-1])
        features["macd_diff"] = features["macd"] - features["macd_signal"]
        adx = ta.adx(high, low, close, length=14)
        if len(adx) > 0:
            features["adx"] = float(adx.iloc[-1])
            features["adx_trend"] = "STRONG" if adx.iloc[-1] > 25 else "WEAK"
        rsi = ta.rsi(close, length=14)
        if len(rsi) > 0:
            features["rsi_14"] = float(rsi.iloc[-1])
            features["rsi_7"] = float(ta.rsi(close, length=7).iloc[-1])
            features["rsi_21"] = float(ta.rsi(close, length=21).iloc[-1])
        stoch = ta.stoch(high, low, close)
        if len(stoch) > 0:
            features["stoch_k"] = float(stoch.iloc[-1])
            features["stoch_d"] = float(ta.stoch_signal(high, low, close).iloc[-1])
        cci = ta.cci(high, low, close, length=20)
        if len(cci) > 0: features["cci"] = float(cci.iloc[-1])
        williams = ta.williams_r(high, low, close, length=14)
        if len(williams) > 0: features["williams_r"] = float(williams.iloc[-1])
        atr = ta.atr(high, low, close, length=14)
        if len(atr) > 0:
            features["atr_14"] = float(atr.iloc[-1])
            features["atr_7"] = float(ta.atr(high, low, close, length=7).iloc[-1])
            features["atr_pct"] = features["atr_14"] / price if price > 0 else 0
        bb_high = ta.bollinger_hband(close); bb_low = ta.bollinger_lband(close)
        if len(bb_high) > 0 and len(bb_low) > 0:
            features["bb_high"] = float(bb_high.iloc[-1])
            features["bb_low"] = float(bb_low.iloc[-1])
            features["bb_mid"] = float(ta.bollinger_mavg(close).iloc[-1])
            features["bb_position"] = (price - features["bb_low"]) / (features["bb_high"] - features["bb_low"])
        features["volatility"] = features.get("atr_pct", 0.01)
        features["volume"] = float(volume.iloc[-1])
        features["volume_sma_20"] = float(volume.rolling(20).mean().iloc[-1])
        features["volume_ratio"] = features["volume"] / features["volume_sma_20"] if features["volume_sma_20"] > 0 else 1.0
        obv = ta.on_balance_volume(close, volume)
        if len(obv) > 0: features["obv"] = float(obv.iloc[-1])
        typical = (high + low + close) / 3
        vwap = (typical * volume).cumsum() / volume.cumsum()
        if len(vwap) > 0:
            features["vwap"] = float(vwap.iloc[-1])
            features["price_vs_vwap"] = price - features["vwap"]
        features["pivot_high"] = float(high.rolling(20).max().iloc[-1])
        features["pivot_low"] = float(low.rolling(20).min().iloc[-1])
        features["pivot_mid"] = (features["pivot_high"] + features["pivot_low"]) / 2
        high_50 = high.iloc[-50:].max(); low_50 = low.iloc[-50:].min(); diff = high_50 - low_50
        features["fib_0"] = low_50
        features["fib_0.236"] = low_50 + diff * 0.236
        features["fib_0.382"] = low_50 + diff * 0.382
        features["fib_0.5"] = low_50 + diff * 0.5
        features["fib_0.618"] = low_50 + diff * 0.618
        features["fib_0.786"] = low_50 + diff * 0.786
        features["fib_1"] = high_50
        return features
