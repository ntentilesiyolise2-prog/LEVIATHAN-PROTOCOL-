# leviathan/signals/pipeline.py
from typing import Dict, Any
from ..nexus import MetaNexus
from ..strategies import StrategySwarm
from ..features import FeatureStore
from ..data import MarketDataService

class SignalPipeline:
    def __init__(self, feature_store: FeatureStore, data_service: MarketDataService, nexus: MetaNexus, swarm: StrategySwarm):
        self.feature_store = feature_store; self.data_service = data_service; self.nexus = nexus; self.swarm = swarm

    async def generate_signal(self, symbol: str, timeframe: str = "1h") -> Dict[str, Any]:
        features = await self.feature_store.get_features(symbol, timeframe)
        if not features:
            return {"direction": "WAIT", "confidence": 0, "rationale": "No features", "symbol": symbol}
        votes = self.swarm.get_votes(features)
        decision = self.nexus.combine(votes)
        decision["symbol"] = symbol
        decision["timeframe"] = timeframe
        decision["price"] = features.get("last_price", 0)
        decision["timestamp"] = features.get("timestamp")
        return decision
