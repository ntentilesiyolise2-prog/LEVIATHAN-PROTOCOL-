# leviathan/data/market_hours.py
from datetime import datetime, time
import pytz
from typing import Dict, Tuple

class MarketHours:
    """Determine if a market is open for a given symbol. No AI dependency."""

    FOREX_CLOSE_WEEKEND = True  # closed Sat/Sun UTC
    CRYPTO_ALWAYS_OPEN = True

    STOCK_SESSIONS = {
        "NYSE": (time(9, 30), time(16, 0)),
        "NASDAQ": (time(9, 30), time(16, 0)),
        "LSE": (time(8, 0), time(16, 30)),
    }
    EXCHANGE_MAP = {
        "^GSPC": "NYSE",
        "^DJI": "NYSE",
        "^IXIC": "NASDAQ",
        "^FTSE": "LSE",
        "^N225": None,
    }

    @classmethod
    def is_open(cls, symbol: str, dt: datetime = None) -> bool:
        if dt is None:
            dt = datetime.utcnow()
        # Check symbol type
        if "=" in symbol or any(c in symbol for c in ["USD", "EUR", "GBP", "JPY", "AUD", "NZD", "CAD", "CHF"]):
            if cls.FOREX_CLOSE_WEEKEND:
                if dt.weekday() >= 5:  # 5=Sat, 6=Sun
                    return False
                return True
            return True
        elif any(c in symbol for c in ["BTC", "ETH", "SOL", "XRP", "ADA", "DOGE", "DOT"]):
            return True  # Crypto always open
        else:
            exchange = cls.EXCHANGE_MAP.get(symbol, "NYSE")
            if exchange in cls.STOCK_SESSIONS:
                open_time, close_time = cls.STOCK_SESSIONS[exchange]
                # Simplified: for US exchanges, convert to Eastern time
                if exchange in ["NYSE", "NASDAQ"]:
                    eastern = pytz.timezone("America/New_York")
                    dt_local = dt.astimezone(eastern)
                    if dt_local.weekday() >= 5:
                        return False
                    if open_time <= dt_local.time() <= close_time:
                        return True
                elif exchange == "LSE":
                    london = pytz.timezone("Europe/London")
                    dt_local = dt.astimezone(london)
                    if dt_local.weekday() >= 5:
                        return False
                    if open_time <= dt_local.time() <= close_time:
                        return True
                return False
            return True
