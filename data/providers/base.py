# leviathan/data/providers/base.py
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
import pandas as pd

class DataProvider(ABC):
    """Abstract base class for all data providers."""

    @abstractmethod
    async def get_ohlcv(self, symbol: str, timeframe: str, limit: int = 100) -> Optional[pd.DataFrame]:
        """Get OHLCV data for a symbol and timeframe."""
        pass

    @abstractmethod
    async def get_price(self, symbol: str) -> Optional[float]:
        """Get the latest price for a symbol."""
        pass

    @abstractmethod
    async def get_ticker_info(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get additional ticker info (optional)."""
        pass

    @property
    @abstractmethod
    def provider_name(self) -> str:
        pass

    @property
    def is_healthy(self) -> bool:
        """Override to check provider health."""
        return True
