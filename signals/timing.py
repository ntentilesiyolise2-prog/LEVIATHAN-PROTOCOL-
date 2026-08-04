# leviathan/signals/timing.py
from typing import Dict, Any

class TimingEstimator:
    @staticmethod
    def estimate_tp_time(signal: Dict[str, Any], velocity: float = None) -> Dict[str, Any]:
        if not signal or signal.get("direction") == "WAIT":
            return {"tp_seconds": None, "sl_seconds": None, "tp_formatted": "N/A", "sl_formatted": "N/A"}
        entry = signal.get("entry", 0); tp = signal.get("tp", entry + 0.01); sl = signal.get("sl", entry - 0.01); atr = signal.get("atr", 0.001)
        if velocity is None: velocity = atr / 60
        if velocity == 0:
            return {"tp_seconds": None, "sl_seconds": None, "tp_formatted": "N/A", "sl_formatted": "N/A"}
        if signal["direction"] == "BUY":
            tp_distance = tp - entry; sl_distance = entry - sl
        else:
            tp_distance = entry - tp; sl_distance = sl - entry
        tp_seconds = tp_distance / abs(velocity) * 60
        sl_seconds = sl_distance / abs(velocity) * 60
        tp_seconds = min(tp_seconds, 86400) if tp_seconds > 0 else None
        sl_seconds = min(sl_seconds, 86400) if sl_seconds > 0 else None
        return {"tp_seconds": tp_seconds, "sl_seconds": sl_seconds, "tp_formatted": TimingEstimator._format_time(tp_seconds), "sl_formatted": TimingEstimator._format_time(sl_seconds)}

    @staticmethod
    def _format_time(seconds):
        if seconds is None: return "N/A"
        if seconds < 60: return f"{int(seconds)}s"
        elif seconds < 3600: return f"{int(seconds // 60)}m {int(seconds % 60)}s"
        else: return f"{int(seconds // 3600)}h {int((seconds % 3600) // 60)}m"
