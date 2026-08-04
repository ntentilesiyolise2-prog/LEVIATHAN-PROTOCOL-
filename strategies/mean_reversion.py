# leviathan/strategies/mean_reversion.py
from .base import Strategy

class MeanReversionStrategy(Strategy):
    def get_signal(self, features: Dict[str, Any]) -> Dict[str, Any]:
        price = features.get('last_price', 0); bb_high = features.get('bb_high', price); bb_low = features.get('bb_low', price); rsi = features.get('rsi_14', 50)
        rsi_os = self.params.get('rsi_oversold', 30); rsi_ob = self.params.get('rsi_overbought', 70)
        if price <= bb_low and rsi < rsi_os:
            conf = min(80, 50 + (rsi_os - rsi))
            return {'direction': 'BUY', 'confidence': conf, 'reason': 'Overextended lower band, RSI oversold'}
        elif price >= bb_high and rsi > rsi_ob:
            conf = min(80, 50 + (rsi - rsi_ob))
            return {'direction': 'SELL', 'confidence': conf, 'reason': 'Overextended upper band, RSI overbought'}
        else:
            return {'direction': 'WAIT', 'confidence': 50, 'reason': 'Neutral'}
