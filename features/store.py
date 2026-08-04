# leviathan/features/store.py
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime
from loguru import logger
from ..data.service import MarketDataService
from ..core.events import EventBus, Event
from .technical import TechnicalFeatures
from .divergence import DivergenceDetector
from .liquidity import LiquidityAnalyzer
from .sentiment import SentimentAnalyzer
from .macro import MacroData
from .patterns import PatternDetector

class FeatureStore:
    def __init__(self, data_service: MarketDataService, event_bus: EventBus):
        self.data_service = data_service
        self.event_bus = event_bus
        self._cache = {}
        self._last_update = {}
        self.technical = TechnicalFeatures()
        self.divergence = DivergenceDetector()
        self.liquidity = LiquidityAnalyzer()
        self.sentiment = SentimentAnalyzer()
        self.macro = MacroData()
        self.patterns = PatternDetector()

    async def get_features(self, symbol: str, timeframe: str = "1h") -> Dict[str, Any]:
        key = f"{symbol}_{timeframe}"
        ttl = 10 if timeframe in ["1m","5m"] else 30 if timeframe in ["15m","30m"] else 60
        if key in self._cache and (datetime.utcnow() - self._last_update.get(key, datetime.min)).seconds < ttl:
            return self._cache[key]
        df = await self.data_service.get_ohlcv(symbol, timeframe, limit=300)
        if df is None or df.empty:
            return {}
        features = {}
        features.update(self.technical.compute_all(df))
        features.update(self.divergence.compute(df))
        features.update(await self.liquidity.compute(symbol, df))
        features.update(self.sentiment.compute(symbol))
        features.update(await self.macro.compute())
        features.update(self.patterns.detect(df))
        features["symbol"] = symbol
        features["timeframe"] = timeframe
        features["last_price"] = float(df['Close'].iloc[-1])
        features["timestamp"] = datetime.utcnow().isoformat()
        self._cache[key] = features
        self._last_update[key] = datetime.utcnow()
        await self.event_bus.publish(Event(type="features_updated", data={"symbol": symbol, "timeframe": timeframe}))
        return features

    async def get_feature(self, symbol: str, feature_name: str, timeframe: str = "1h") -> Optional[Any]:
        features = await self.get_features(symbol, timeframe)
        return features.get(feature_name)

    def clear_cache(self, symbol: Optional[str] = None):
        if symbol:
            keys = [k for k in self._cache if k.startswith(symbol)]
            for k in keys:
                self._cache.pop(k, None)
                self._last_update.pop(k, None)
        else:
            self._cache.clear()
            self._last_update.clear()
