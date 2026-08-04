# leviathan/strategies/base.py
from abc import ABC, abstractmethod
from typing import Dict, Any

class Strategy(ABC):
    def __init__(self, name: str, params: Dict[str, Any]):
        self.name = name; self.params = params; self.wins = 0; self.losses = 0; self.total_pnl = 0.0
    @abstractmethod
    def get_signal(self, features: Dict[str, Any]) -> Dict[str, Any]:
        pass
    def update_performance(self, pnl: float):
        if pnl > 0: self.wins += 1
        else: self.losses += 1
        self.total_pnl += pnl
    @property
    def win_rate(self) -> float:
        total = self.wins + self.losses
        return (self.wins / total * 100) if total > 0 else 50.0
