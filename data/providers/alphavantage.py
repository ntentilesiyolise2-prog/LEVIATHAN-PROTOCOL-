# leviathan/data/providers/alphavantage.py
import aiohttp
import pandas as pd
from typing import Optional, Dict, Any
from loguru import logger

from .base import DataProvider

class AlphaVantageProvider(DataProvider):
    """Additional fallback provider. No AI dependency."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://www.alphavantage.co/query"

    @property
    def provider_name(self) -> str:
        return "alphavantage"

    async def get_ohlcv(self, symbol: str, timeframe: str, limit: int = 100) -> Optional[pd.DataFrame]:
        if not self.api_key:
            return None
        func_map = {
            "1m": "TIME_SERIES_INTRADAY",
            "5m": "TIME_SERIES_INTRADAY",
            "15m": "TIME_SERIES_INTRADAY",
            "30m": "TIME_SERIES_INTRADAY",
            "1h": "TIME_SERIES_INTRADAY",
            "1d": "TIME_SERIES_DAILY",
            "1wk": "TIME_SERIES_WEEKLY",
            "1mo": "TIME_SERIES_MONTHLY"
        }
        func = func_map.get(timeframe, "TIME_SERIES_DAILY")
        params = {
            "function": func,
            "symbol": symbol,
            "apikey": self.api_key,
            "outputsize": "compact"
        }
        if "INTRADAY" in func:
            interval_map = {"1m": "1min", "5m": "5min", "15m": "15min", "30m": "30min", "1h": "60min"}
            params["interval"] = interval_map.get(timeframe, "1min")

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(self.base_url, params=params, timeout=10) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        for key in data:
                            if "Time Series" in key:
                                series = data[key]
                                rows = []
                                for ts, values in series.items():
                                    rows.append({
                                        "timestamp": pd.to_datetime(ts),
                                        "Open": float(values["1. open"]),
                                        "High": float(values["2. high"]),
                                        "Low": float(values["3. low"]),
                                        "Close": float(values["4. close"]),
                                        "Volume": float(values["5. volume"])
                                    })
                                df = pd.DataFrame(rows)
                                df.set_index("timestamp", inplace=True)
                                return df
            except Exception as e:
                logger.warning(f"Alpha Vantage OHLCV error: {e}")
        return None

    async def get_price(self, symbol: str) -> Optional[float]:
        df = await self.get_ohlcv(symbol, "1d", 1)
        if df is not None and not df.empty:
            return df['Close'].iloc[-1]
        return None

    async def get_ticker_info(self, symbol: str) -> Optional[Dict[str, Any]]:
        # Not implemented
        return None
