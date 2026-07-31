# leviathan/data/service.py
import asyncio
import pandas as pd
from typing import List, Optional, Dict, Any
from loguru import logger

from ..config import get_settings
from ..core.events import EventBus, Event
from ..core.notification_center import NotificationCenter
from .cache import Cache
from .market_hours import MarketHours
from .providers import (
    PolygonProvider, YahooProvider, AlphaVantageProvider, MockProvider, DataProvider
)

class MarketDataService:
    """Unified market data service with provider fallback and caching.
    This service is self-sufficient and does not rely on any AI APIs.
    """

    def __init__(self, settings, event_bus: EventBus, notif_center: NotificationCenter):
        self.settings = settings
        self.event_bus = event_bus
        self.notif_center = notif_center
        self.cache = Cache(default_ttl=5)

        # Initialize providers
        self.providers: List[DataProvider] = []
        if settings.POLYGON_API_KEY:
            self.providers.append(PolygonProvider(settings.POLYGON_API_KEY))
        else:
            logger.info("Polygon API key missing; skipping Polygon provider.")
        # Always include Yahoo and Mock
        self.providers.append(YahooProvider())
        if settings.ALPHA_VANTAGE_API_KEY:
            self.providers.append(AlphaVantageProvider(settings.ALPHA_VANTAGE_API_KEY))
        self.providers.append(MockProvider())  # last resort

        # WebSocket task
        self._ws_task = None
        self._polygon_provider = None
        for p in self.providers:
            if isinstance(p, PolygonProvider):
                self._polygon_provider = p
                break

    async def start(self):
        """Start background WebSocket for real-time updates."""
        if self._polygon_provider:
            symbols = self.settings.config.symbols
            self._ws_task = asyncio.create_task(self._polygon_provider.start_websocket(symbols))
            logger.info("Polygon WebSocket started.")
            # Subscribe to symbols after connection
            await asyncio.sleep(2)  # allow time to connect
            await self._polygon_provider.subscribe_symbols(symbols)

    async def stop(self):
        if self._ws_task:
            self._ws_task.cancel()

    async def get_ohlcv(self, symbol: str, timeframe: str = "1d", limit: int = 100) -> Optional[pd.DataFrame]:
        """Get OHLCV data with caching and provider fallback."""
        cache_key = f"ohlcv_{symbol}_{timeframe}_{limit}"
        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached

        for provider in self.providers:
            try:
                df = await provider.get_ohlcv(symbol, timeframe, limit)
                if df is not None and not df.empty:
                    # Cache with appropriate TTL
                    ttl = 60
                    if timeframe in ["1m", "5m"]:
                        ttl = 10
                    elif timeframe in ["15m", "30m"]:
                        ttl = 30
                    elif timeframe == "1h":
                        ttl = 300
                    else:
                        ttl = 3600
                    self.cache.set(cache_key, df, ttl=ttl)
                    # Publish event
                    await self.event_bus.publish(
                        Event(type="data_updated", data={"symbol": symbol, "timeframe": timeframe, "provider": provider.provider_name})
                    )
                    return df
            except Exception as e:
                logger.warning(f"Provider {provider.provider_name} failed for OHLCV {symbol}: {e}")
                await self._notify_error(f"{provider.provider_name} failed for OHLCV {symbol}", e)
                continue
        # Fallback: Mock data if all providers fail
        mock = MockProvider()
        df = await mock.get_ohlcv(symbol, timeframe, limit)
        return df

    async def get_price(self, symbol: str) -> Optional[float]:
        """Get latest price, prioritized from WebSocket feed."""
        # Check if we have a cached price from WebSocket
        if self._polygon_provider and symbol in self._polygon_provider._latest_prices:
            return self._polygon_provider._latest_prices[symbol]
        # Else try providers
        cache_key = f"price_{symbol}"
        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached

        for provider in self.providers:
            try:
                price = await provider.get_price(symbol)
                if price is not None:
                    self.cache.set(cache_key, price, ttl=5)
                    return price
            except Exception as e:
                logger.warning(f"Provider {provider.provider_name} failed for price {symbol}: {e}")
                continue
        # Fallback to mock
        mock = MockProvider()
        return await mock.get_price(symbol)

    async def get_ticker_info(self, symbol: str) -> Optional[Dict[str, Any]]:
        cache_key = f"info_{symbol}"
        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached
        for provider in self.providers:
            try:
                info = await provider.get_ticker_info(symbol)
                if info:
                    self.cache.set(cache_key, info, ttl=3600)
                    return info
            except:
                continue
        return None

    async def subscribe_symbols(self, symbols: List[str]):
        """Subscribe to real-time updates for symbols (Polygon WebSocket)."""
        if self._polygon_provider:
            await self._polygon_provider.subscribe_symbols(symbols)

    def is_market_open(self, symbol: str) -> bool:
        return MarketHours.is_open(symbol)

    async def _notify_error(self, message: str, error: Exception):
        """Send a notification about an error."""
        if self.notif_center:
            self.notif_center.add({
                "type": "error",
                "title": "Data Provider Error",
                "message": f"{message}: {str(error)}",
                "severity": "warning"
            })
