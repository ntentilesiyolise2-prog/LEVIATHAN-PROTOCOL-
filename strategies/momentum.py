# leviathan/strategies/momentum.py
from .base import Strategy

class MomentumStrategy(Strategy):
    def get_signal(self, features: Dict[str, Any]) -> Dict[str, Any]:
        rsi = features.get('rsi_14', 50); macd = features.get('macd', 0); macd_signal = features.get('macd_signal', 0)
        if rsi > 60 and macd > macd_signal:
            return {'direction': 'BUY', 'confidence': 65, 'reason': 'Strong momentum (RSI > 60, MACD bullish)'}
        elif rsi < 40 and macd < macd_signal:
            return {'direction': 'SELL', 'confidence': 65, 'reason': 'Weak momentum (RSI < 40, MACD bearish)'}
        else:
            return {'direction': 'WAIT', 'confidence': 50, 'reason': 'Neutral momentum'}
