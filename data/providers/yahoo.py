# leviathan/data/providers/yahoo.py
import yfinance as yf
import pandas as pd
from typing import Optional, Dict, Any
from loguru import logger

from .base import DataProvider

class YahooProvider(DataProvider):
    """Fallback provider using Yahoo Finance. No AI dependency."""

    @property
    def provider_name(self) -> str:
        return "yahoo"

    async def get_ohlcv(self, symbol: str, timeframe: str, limit: int = 100) -> Optional[pd.DataFrame]:
        try:
            ticker = yf.Ticker(symbol)
            interval_map = {
                "1m": "1m", "5m": "5m", "15m": "15m", "30m": "30m",
                "1h": "1h", "4h": "1h", "1d": "1d", "1wk": "1wk", "1mo": "1mo"
            }
            interval = interval_map.get(timeframe, "1d")
            if timeframe in ["1m", "5m"]:
                period = "1d"
            elif timeframe in ["15m", "30m"]:
                period = "5d"
            elif timeframe in ["1h", "4h"]:
                period = "1mo"
            else:
                period = "1y"
            df = ticker.history(period=period, interval=interval)
            if df.empty:
                return None
            df.rename(columns={"Open": "Open", "High": "High", "Low": "Low", "Close": "Close", "Volume": "Volume"}, inplace=True)
            return df
        except Exception as e:
            logger.warning(f"Yahoo OHLCV error for {symbol}: {e}")
            return None

    async def get_price(self, symbol: str) -> Optional[float]:
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="1d", interval="1m")
            if not data.empty:
                return data['Close'].iloc[-1]
            return None
        except Exception as e:
            logger.warning(f"Yahoo price error for {symbol}: {e}")
            return None

    async def get_ticker_info(self, symbol: str) -> Optional[Dict[str, Any]]:
        try:
            ticker = yf.Ticker(symbol)
            return ticker.info
        except:
            return None
