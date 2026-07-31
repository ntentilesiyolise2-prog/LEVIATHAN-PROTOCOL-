# leviathan/data/providers/polygon.py
import asyncio
import json
import pandas as pd
import aiohttp
import websockets
from typing import Optional, Dict, Any
from datetime import datetime
from loguru import logger

from .base import DataProvider

class PolygonProvider(DataProvider):
    """Real-time provider using Polygon.io WebSocket and REST API.
    This is the primary provider for real-time data. It does NOT require AI APIs.
    """

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.polygon.io"
        self.ws_url = "wss://delayed.polygon.io/ws"
        self._ws = None
        self._latest_prices = {}  # symbol -> price
        self._running = False
        self._subscribed_symbols = set()

    @property
    def provider_name(self) -> str:
        return "polygon"

    async def start_websocket(self, symbols: list = None):
        """Start WebSocket connection for real-time price updates."""
        if not self.api_key:
            logger.warning("Polygon API key missing; WebSocket disabled.")
            return
        self._running = True
        while self._running:
            try:
                async with websockets.connect(self.ws_url) as ws:
                    self._ws = ws
                    # Authenticate
                    await ws.send(json.dumps({"action": "auth", "params": self.api_key}))
                    auth_resp = await ws.recv()
                    logger.debug(f"Polygon WS auth: {auth_resp}")

                    # Subscribe to symbols if provided
                    if symbols:
                        sub_msg = json.dumps({"action": "subscribe", "params": f"T.{','.join(symbols)}"})
                        await ws.send(sub_msg)
                        self._subscribed_symbols = set(symbols)

                    async for message in ws:
                        if not self._running:
                            break
                        try:
                            data = json.loads(message)
                            if "ev" in data and data["ev"] == "T":  # Trade
                                sym = data["sym"]
                                price = data["p"]
                                self._latest_prices[sym] = price
                                # Emit event via callback if needed
                        except Exception as e:
                            logger.error(f"Polygon WS message error: {e}")
            except Exception as e:
                logger.error(f"Polygon WebSocket error: {e}")
                await asyncio.sleep(5)

    async def subscribe_symbols(self, symbols: list):
        """Subscribe to real-time price updates for symbols."""
        if not self._ws:
            return
        # Only subscribe to new symbols not already subscribed
        new_symbols = [s for s in symbols if s not in self._subscribed_symbols]
        if new_symbols:
            msg = json.dumps({"action": "subscribe", "params": f"T.{','.join(new_symbols)}"})
            await self._ws.send(msg)
            self._subscribed_symbols.update(new_symbols)

    async def get_ohlcv(self, symbol: str, timeframe: str, limit: int = 100) -> Optional[pd.DataFrame]:
        """Fetch OHLCV from Polygon REST API."""
        if not self.api_key:
            return None
        url = f"{self.base_url}/v2/aggs/ticker/{symbol}/range/1/{timeframe}/{limit}"
        params = {"adjusted": "true", "apiKey": self.api_key}
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, params=params, timeout=10) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if data.get("status") == "OK":
                            results = data.get("results", [])
                            if results:
                                df = pd.DataFrame(results)
                                df["timestamp"] = pd.to_datetime(df["t"], unit="ms")
                                df.set_index("timestamp", inplace=True)
                                df.rename(columns={"o": "Open", "h": "High", "l": "Low", "c": "Close", "v": "Volume"}, inplace=True)
                                return df
            except Exception as e:
                logger.warning(f"Polygon OHLCV error: {e}")
        return None

    async def get_price(self, symbol: str) -> Optional[float]:
        """Return latest price from WebSocket feed, or fallback to REST."""
        if symbol in self._latest_prices:
            return self._latest_prices[symbol]
        # Fallback: get last trade
        if not self.api_key:
            return None
        url = f"{self.base_url}/v2/last/trade/{symbol}"
        params = {"apiKey": self.api_key}
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, params=params, timeout=10) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if data.get("status") == "OK":
                            return data["results"]["p"]
            except:
                pass
        return None

    async def get_ticker_info(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get ticker details."""
        if not self.api_key:
            return None
        url = f"{self.base_url}/v3/reference/tickers/{symbol}"
        params = {"apiKey": self.api_key}
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, params=params, timeout=10) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data.get("results")
            except:
                pass
        return None
