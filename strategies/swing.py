# leviathan/strategies/swing.py
from .base import Strategy

class SwingStrategy(Strategy):
    def get_signal(self, features: Dict[str, Any]) -> Dict[str, Any]:
        rsi = features.get('rsi_14', 50); bull_div = features.get('divergence_bullish_rsi', False); bear_div = features.get('divergence_bearish_rsi', False)
        if rsi < 30 and bull_div:
            return {'direction': 'BUY', 'confidence': 75, 'reason': 'Oversold + bullish divergence'}
        elif rsi > 70 and bear_div:
            return {'direction': 'SELL', 'confidence': 75, 'reason': 'Overbought + bearish divergence'}
        else:
            return {'direction': 'WAIT', 'confidence': 50, 'reason': 'No swing setup'}
