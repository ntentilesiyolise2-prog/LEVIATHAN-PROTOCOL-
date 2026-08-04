# leviathan/risk/engine.py
import numpy as np
from typing import Dict, Any, List, Optional

class RiskEngine:
    def __init__(self, initial_balance: float = 10000, max_drawdown: float = 5.0):
        self.initial_balance = initial_balance; self.balance = initial_balance; self.peak = initial_balance; self.drawdown = 0.0; self.trades = []
    def update_balance(self, pnl: float):
        self.balance += pnl
        if self.balance > self.peak: self.peak = self.balance
        self.drawdown = (self.peak - self.balance) / self.peak * 100 if self.peak > 0 else 0
    def calculate_var(self, confidence: float = 0.95) -> float:
        if len(self.trades) < 10: return 0.0
        returns = [t['pnl'] for t in self.trades[-100:]]; returns.sort()
        idx = int((1 - confidence) * len(returns))
        return abs(returns[idx])
    def calculate_cvar(self, confidence: float = 0.95) -> float:
        if len(self.trades) < 10: return 0.0
        returns = [t['pnl'] for t in self.trades[-100:]]; returns.sort()
        idx = int((1 - confidence) * len(returns))
        tail = returns[:idx]
        return abs(np.mean(tail)) if tail else 0.0
    def position_size(self, risk_percent: float, stop_loss_pips: float, pip_value: float = 0.0001, account_balance: float = None) -> float:
        balance = account_balance or self.balance
        risk_amount = balance * risk_percent / 100
        lot_size = risk_amount / (stop_loss_pips * pip_value * 100000)
        return round(max(0.01, min(10.0, lot_size)), 2)
