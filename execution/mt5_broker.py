# leviathan/execution/mt5_broker.py
from .broker import BrokerInterface
from typing import Dict, Any, List, Optional
from loguru import logger
try:
    import MetaTrader5 as mt5
except:
    mt5 = None; logger.warning("MT5 package not installed")

class MT5Broker(BrokerInterface):
    def __init__(self, login: int = 0, password: str = "", server: str = ""):
        self.login = login; self.password = password; self.server = server; self.connected = False
    async def connect(self):
        if mt5 is None: return False
        if self.connected: return True
        if not mt5.initialize(): return False
        if self.login and self.password and self.server:
            if not mt5.login(self.login, self.password, self.server): return False
        self.connected = True; return True
    async def execute_order(self, symbol, direction, entry, sl, tp, volume=0.01):
        if not await self.connect(): return {"status":"error","message":"MT5 not connected"}
        order_type = mt5.ORDER_TYPE_BUY if direction=="BUY" else mt5.ORDER_TYPE_SELL
        request = {"action": mt5.TRADE_ACTION_DEAL, "symbol": symbol, "volume": volume, "type": order_type, "price": entry, "sl": sl, "tp": tp, "deviation": 20, "magic": 123456, "comment": "LEVIATHAN", "type_time": mt5.ORDER_TIME_GTC, "type_filling": mt5.ORDER_FILLING_IOC}
        result = mt5.order_send(request)
        if result.retcode != mt5.TRADE_RETCODE_DONE: return {"status":"error","message":result.comment}
        return {"status":"filled","order_id":result.order,"volume":result.volume,"price":result.price}
    async def close_position(self, position_id): return {"status":"not_implemented"}
    async def close_position_partial(self, position_id, volume): return {"status":"not_implemented"}
    async def modify_position(self, position_id, sl, tp): return {"status":"not_implemented"}
    async def get_positions(self): return []
    async def get_account_info(self): return {}
    async def get_price(self, symbol): return None
