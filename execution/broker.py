# leviathan/execution/broker.py
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional

class BrokerInterface(ABC):
    @abstractmethod
    async def execute_order(self, symbol: str, direction: str, entry: float, sl: float, tp: float, volume: float = 0.01) -> Dict[str, Any]:
        pass
    @abstractmethod
    async def close_position(self, position_id: str) -> Dict[str, Any]:
        pass
    @abstractmethod
    async def close_position_partial(self, position_id: str, volume: float) -> Dict[str, Any]:
        pass
    @abstractmethod
    async def modify_position(self, position_id: str, sl: float, tp: float) -> Dict[str, Any]:
        pass
    @abstractmethod
    async def get_positions(self) -> List[Dict[str, Any]]:
        pass
    @abstractmethod
    async def get_account_info(self) -> Dict[str, Any]:
        pass
    @abstractmethod
    async def get_price(self, symbol: str) -> Optional[float]:
        pass
