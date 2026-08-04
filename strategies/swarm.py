# leviathan/strategies/swarm.py
from typing import List, Dict, Any
from .trend import TrendStrategy
from .mean_reversion import MeanReversionStrategy
from .breakout import BreakoutStrategy
from .momentum import MomentumStrategy
from .scalp import ScalpStrategy
from .swing import SwingStrategy
from .position import PositionStrategy

class StrategySwarm:
    def __init__(self):
        self.strategies = [
            TrendStrategy('trend', {'fast_ema': 20, 'mid_ema': 50, 'slow_ema': 200, 'adx_threshold': 25}),
            TrendStrategy('trend_fast', {'fast_ema': 10, 'mid_ema': 30, 'slow_ema': 100, 'adx_threshold': 20}),
            MeanReversionStrategy('mean_reversion', {'bb_period': 20, 'bb_std': 2, 'rsi_oversold': 30, 'rsi_overbought': 70}),
            BreakoutStrategy('breakout', {'lookback': 20, 'volume_threshold': 1.5}),
            MomentumStrategy('momentum', {'roc_period': 14, 'momentum_threshold': 3}),
            ScalpStrategy('scalp', {'atr_mult': 1.5}),
            SwingStrategy('swing', {'lookback': 50, 'rsi_oversold': 30, 'rsi_overbought': 70}),
            PositionStrategy('position', {'macro_weight': 0.3, 'trend_weight': 0.7}),
        ]

    def get_votes(self, features: Dict[str, Any]) -> List[Dict[str, Any]]:
        votes = []
        for s in self.strategies:
            try:
                sig = s.get_signal(features)
                if sig['direction'] != 'WAIT':
                    votes.append({'source': s.name, 'direction': sig['direction'], 'confidence': sig['confidence'], 'reason': sig['reason']})
            except: pass
        return votes

    def update_performance(self, strategy_name: str, pnl: float):
        for s in self.strategies:
            if s.name == strategy_name: s.update_performance(pnl); break
