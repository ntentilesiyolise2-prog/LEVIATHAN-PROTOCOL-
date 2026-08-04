# leviathan/strategies/breakout.py
from .base import Strategy

class BreakoutStrategy(Strategy):
    def get_signal(self, features: Dict[str, Any]) -> Dict[str, Any]:
        price = features.get('last_price', 0); high = features.get('pivot_high', price); low = features.get('pivot_low', price); volume_ratio = features.get('volume_ratio', 1.0)
        volume_threshold = self.params.get('volume_threshold', 1.5)
        if price > high and volume_ratio > volume_threshold:
            return {'direction': 'BUY', 'confidence': 70, 'reason': 'Breakout above resistance with high volume'}
        elif price < low and volume_ratio > volume_threshold:
            return {'direction': 'SELL', 'confidence': 70, 'reason': 'Breakout below support with high volume'}
        else:
            return {'direction': 'WAIT', 'confidence': 50, 'reason': 'No breakout'}
