# leviathan/data/providers/mock.py
import pandas as pd
import numpy as np
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from loguru import logger

from .base import DataProvider

class MockProvider(DataProvider):
    """Fallback provider that generates realistic mock data. No AI dependency."""

    @property
    def provider_name(self) -> str:
        return "mock"

    async def get_ohlcv(self, symbol: str, timeframe: str, limit: int = 100) -> Optional[pd.DataFrame]:
        base_price = 1.0
        if "BTC" in symbol:
            base_price = 67000
        elif "ETH" in symbol:
            base_price = 3400
        elif "USD" in symbol and "JPY" not in symbol:
            base_price = 1.08
        elif "JPY" in symbol:
            base_price = 150
        elif "^GSPC" in symbol:
            base_price = 5200
        elif "GC" in symbol:
            base_price = 2340
        elif "CL" in symbol:
            base_price = 78
        periods = limit
        returns = np.random.normal(0.0002, 0.01, periods)
        prices = base_price * np.exp(np.cumsum(returns))
        df = pd.DataFrame({
            "Open": prices * (1 + np.random.uniform(-0.001, 0.001, periods)),
            "High": prices * (1 + np.random.uniform(0.001, 0.005, periods)),
            "Low": prices * (1 - np.random.uniform(0.001, 0.005, periods)),
            "Close": prices,
            "Volume": np.random.randint(1000, 10000, periods)
        })
        start_time = datetime.utcnow() - timedelta(minutes=periods * 5)
        df.index = pd.date_range(start=start_time, periods=periods, freq="5min")
        return df

    async def get_price(self, symbol: str) -> Optional[float]:
        base = 1.0
        if "BTC" in symbol: base = 67000
        elif "ETH" in symbol: base = 3400
        elif "USD" in symbol and "JPY" not in symbol: base = 1.08
        elif "JPY" in symbol: base = 150
        elif "^GSPC" in symbol: base = 5200
        elif "GC" in symbol: base = 2340
        elif "CL" in symbol: base = 78
        return base * (1 + np.random.uniform(-0.002, 0.002))

    async def get_ticker_info(self, symbol: str) -> Optional[Dict[str, Any]]:
        return {"name": f"{symbol} Mock", "exchange": "MOCK"}
