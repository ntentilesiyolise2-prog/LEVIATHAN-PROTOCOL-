# leviathan/strategies/trend.py
from .base import Strategy

class TrendStrategy(Strategy):
    def get_signal(self, features: Dict[str, Any]) -> Dict[str, Any]:
        fast = self.params.get('fast_ema', 20); mid = self.params.get('mid_ema', 50); slow = self.params.get('slow_ema', 200); adx_threshold = self.params.get('adx_threshold', 25)
        price = features.get('last_price', 0); ema_fast = features.get(f'ema_{fast}', price); ema_mid = features.get(f'ema_{mid}', price); ema_slow = features.get(f'ema_{slow}', price); adx = features.get('adx', 0)
        if adx < adx_threshold:
            return {'direction': 'WAIT', 'confidence': 0, 'reason': f'ADX {adx:.1f} < {adx_threshold}'}
        if price > ema_fast > ema_mid > ema_slow:
            conf = min(90, 60 + (adx - 25) * 0.5)
            return {'direction': 'BUY', 'confidence': conf, 'reason': f'Strong uptrend (ADX {adx:.1f})'}
        elif price < ema_fast < ema_mid < ema_slow:
            conf = min(90, 60 + (adx - 25) * 0.5)
            return {'direction': 'SELL', 'confidence': conf, 'reason': f'Strong downtrend (ADX {adx:.1f})'}
        else:
            return {'direction': 'WAIT', 'confidence': 50, 'reason': 'No clear trend'}
