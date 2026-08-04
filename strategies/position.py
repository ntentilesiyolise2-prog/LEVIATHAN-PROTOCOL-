# leviathan/strategies/position.py
from .base import Strategy

class PositionStrategy(Strategy):
    def get_signal(self, features: Dict[str, Any]) -> Dict[str, Any]:
        macro_weight = self.params.get('macro_weight', 0.3); trend_weight = self.params.get('trend_weight', 0.7)
        price = features.get('last_price', 0); ema200 = features.get('ema_200', price); risk_on = features.get('risk_on', False); vix = features.get('vix', 20)
        trend_score = 1 if price > ema200 else -1
        macro_score = 1 if risk_on and vix < 18 else -1 if vix > 25 else 0
        composite = trend_score * trend_weight + macro_score * macro_weight
        if composite > 0.5:
            return {'direction': 'BUY', 'confidence': 70, 'reason': 'Trend up + risk on'}
        elif composite < -0.5:
            return {'direction': 'SELL', 'confidence': 70, 'reason': 'Trend down + risk off'}
        else:
            return {'direction': 'WAIT', 'confidence': 50, 'reason': 'Position mode neutral'}
