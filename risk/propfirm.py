# leviathan/risk/propfirm.py
from typing import Dict, Any

class PropFirm:
    def __init__(self, max_daily_loss: float = 5.0, max_total_loss: float = 10.0, target_profit: float = 10.0):
        self.max_daily_loss = max_daily_loss; self.max_total_loss = max_total_loss; self.target_profit = target_profit
        self.daily_loss = 0.0; self.total_loss = 0.0; self.profit = 0.0; self.initial_balance = 10000.0; self.current_balance = 10000.0
    def reset_daily(self): self.daily_loss = 0.0
    def update(self, pnl: float):
        self.current_balance += pnl
        if pnl < 0:
            self.daily_loss += abs(pnl); self.total_loss += abs(pnl)
        else: self.profit += pnl
    def get_status(self) -> Dict[str, Any]:
        daily_loss_pct = (self.daily_loss / self.initial_balance) * 100
        total_loss_pct = (self.total_loss / self.initial_balance) * 100
        profit_pct = (self.profit / self.initial_balance) * 100
        status = "PASSING" if profit_pct >= self.target_profit and daily_loss_pct < self.max_daily_loss and total_loss_pct < self.max_total_loss else "WORKING"
        return {"daily_loss_pct": round(daily_loss_pct,2), "total_loss_pct": round(total_loss_pct,2), "profit_pct": round(profit_pct,2), "status": status, "passed": status == "PASSING"}
