# leviathan/strategies/scalp.py
from .base import Strategy

class ScalpStrategy(Strategy):
    def get_signal(self, features: Dict[str, Any]) -> Dict[str, Any]:
        price = features.get('last_price', 0); vwap = features.get('vwap', price); delta = features.get('delta_trend', 'NEUTRAL')
        if price < vwap and delta == 'BUY':
            return {'direction': 'BUY', 'confidence': 60, 'reason': 'Price below VWAP, buying delta'}
        elif price > vwap and delta == 'SELL':
            return {'direction': 'SELL', 'confidence': 60, 'reason': 'Price above VWAP, selling delta'}
        else:
            return {'direction': 'WAIT', 'confidence': 50, 'reason': 'No scalp setup'}
