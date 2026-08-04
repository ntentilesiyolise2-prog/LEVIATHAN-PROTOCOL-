# leviathan/execution/simulator.py
import json, random, time
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
from loguru import logger
from .broker import BrokerInterface

class SimulatorBroker(BrokerInterface):
    def __init__(self, initial_balance: float = 10000, journal_path: str = "sim_journal.json"):
        self.balance = initial_balance; self.equity = initial_balance; self.margin = 0.0; self.positions = []; self.closed_positions = []; self.journal_path = Path(journal_path); self._load_journal()
    def _load_journal(self):
        if self.journal_path.exists():
            try:
                with open(self.journal_path, "r") as f:
                    data = json.load(f)
                    self.balance = data.get("balance", 10000)
                    self.positions = data.get("open_positions", [])
                    self.closed_positions = data.get("closed_positions", [])
            except: pass
        else:
            self.positions = []; self.closed_positions = []; self.balance = 10000
    def _save_journal(self):
        with open(self.journal_path, "w") as f:
            json.dump({"balance": self.balance, "open_positions": self.positions, "closed_positions": self.closed_positions}, f, indent=2)
    async def set_balance(self, new_balance: float):
        self.balance = new_balance; self.equity = new_balance; self._save_journal()
    async def execute_order(self, symbol: str, direction: str, entry: float, sl: float, tp: float, volume: float = 0.01) -> Dict[str, Any]:
        win = random.random() < 0.60
        if direction == "BUY":
            exit_price = tp if win else sl
            pnl = (exit_price - entry) * volume * 100000
        else:
            exit_price = tp if win else sl
            pnl = (entry - exit_price) * volume * 100000
        self.balance += pnl; self.equity = self.balance
        position = {"id": str(len(self.closed_positions)+1), "symbol": symbol, "direction": direction, "entry": entry, "exit": exit_price, "volume": volume, "pnl": pnl, "win": win, "closed_at": datetime.utcnow().isoformat()}
        self.closed_positions.append(position); self._save_journal()
        logger.info(f"Simulated {direction} {symbol} at {entry}, PnL: {pnl:.2f}")
        return {"status": "filled", "order_id": position["id"], "volume": volume, "price": entry, "message": f"Trade closed with {'WIN' if win else 'LOSS'}", "pnl": pnl, "win": win}
    async def close_position(self, position_id: str) -> Dict[str, Any]:
        for pos in self.positions:
            if pos.get("id") == position_id:
                self.positions.remove(pos); self._save_journal(); return {"status": "closed", "position": pos}
        return {"status": "not_found"}
    async def close_position_partial(self, position_id: str, volume: float) -> Dict[str, Any]:
        return await self.close_position(position_id)
    async def modify_position(self, position_id: str, sl: float, tp: float) -> Dict[str, Any]:
        for pos in self.positions:
            if pos.get("id") == position_id:
                pos["sl"] = sl; pos["tp"] = tp; self._save_journal(); return {"status": "modified", "position": pos}
        return {"status": "not_found"}
    async def get_positions(self) -> List[Dict[str, Any]]:
        return self.positions
    async def get_account_info(self) -> Dict[str, Any]:
        return {"balance": self.balance, "equity": self.equity, "margin": self.margin, "free_margin": self.balance - self.margin, "margin_level": 100.0 if self.margin == 0 else (self.balance / self.margin) * 100}
    async def get_price(self, symbol: str) -> Optional[float]:
        return None
