# leviathan/signals/continuous_engine.py
import asyncio
import time
from typing import List, Dict, Any
from loguru import logger
from ..features import FeatureStore
from ..data import MarketDataService
from ..core.notification_center import NotificationCenter
from ..core.events import EventBus, Event
from ..execution import BrokerInterface
from ..nexus import MetaNexus
from ..strategies import StrategySwarm
from .pipeline import SignalPipeline
from .timing import TimingEstimator

class ContinuousSignalEngine:
    def __init__(self, feature_store: FeatureStore, data_service: MarketDataService, notif_center: NotificationCenter, event_bus: EventBus, broker: BrokerInterface, nexus: MetaNexus, swarm: StrategySwarm, symbols: List[str], interval: float = 5.0, target_profit: float = 150.0):
        self.feature_store = feature_store; self.data_service = data_service; self.notif_center = notif_center; self.event_bus = event_bus; self.broker = broker; self.nexus = nexus; self.swarm = swarm; self.symbols = symbols; self.interval = interval; self.target_profit = target_profit
        self.pipeline = SignalPipeline(feature_store, data_service, nexus, swarm)
        self.running = False; self._task = None; self._signal_cache = {}

    async def start(self):
        self.running = True; self._task = asyncio.create_task(self._run()); logger.info("ContinuousSignalEngine started")

    async def stop(self):
        self.running = False
        if self._task: self._task.cancel()
        logger.info("ContinuousSignalEngine stopped")

    async def _run(self):
        while self.running:
            start_time = time.time()
            try:
                tasks = [self._process_symbol(sym) for sym in self.symbols]
                await asyncio.gather(*tasks)
            except Exception as e:
                logger.error(f"Signal engine error: {e}")
            elapsed = time.time() - start_time
            if elapsed < self.interval: await asyncio.sleep(self.interval - elapsed)

    async def _process_symbol(self, symbol: str):
        try:
            signal = await self.pipeline.generate_signal(symbol, "1h")
            if signal["direction"] == "WAIT": return
            price = signal.get("price", 0)
            atr = await self.feature_store.get_feature(symbol, "atr_14", "1h") or price * 0.01
            signal["atr"] = atr
            if signal["direction"] == "BUY":
                entry = price; sl = entry - atr * 2.0; tp = entry + atr * 3.0
            else:
                entry = price; sl = entry + atr * 2.0; tp = entry - atr * 3.0
            signal["entry"] = round(entry, 5); signal["sl"] = round(sl, 5); signal["tp"] = round(tp, 5)
            pip_value = 0.0001 if 'USD' in symbol else 0.01
            tp_distance = abs(tp - entry)
            lot = self.target_profit / (tp_distance / pip_value * 100000) if tp_distance > 0 else 0.01
            signal["recommended_lot"] = round(max(0.01, min(1.0, lot)), 2)
            velocity = atr / 60
            timing = TimingEstimator.estimate_tp_time(signal, velocity)
            signal["estimated_tp_time"] = timing.get("tp_formatted"); signal["estimated_sl_time"] = timing.get("sl_formatted")
            expiry = time.time() + 900
            signal["expiry"] = expiry; signal["expiry_formatted"] = time.strftime("%H:%M:%S", time.localtime(expiry))
            self._signal_cache[symbol] = signal
            self.notif_center.add({"type": "signal", "symbol": symbol, "direction": signal["direction"], "confidence": signal["confidence"], "entry": signal["entry"], "sl": signal["sl"], "tp": signal["tp"], "lot": signal["recommended_lot"], "rationale": signal["rationale"], "estimated_tp": signal["estimated_tp_time"], "expiry": signal["expiry_formatted"]})
            await self.event_bus.publish(Event(type="signal_new", data=signal))
            from ..config import get_settings
            settings = get_settings()
            if signal["confidence"] > 75 and settings.config.auto_trade.get("enabled", False):
                await self._auto_execute(signal)
        except Exception as e:
            logger.error(f"Error processing {symbol}: {e}")

    async def _auto_execute(self, signal: Dict[str, Any]):
        try:
            result = await self.broker.execute_order(symbol=signal["symbol"], direction=signal["direction"], entry=signal["entry"], sl=signal["sl"], tp=signal["tp"], volume=signal["recommended_lot"])
            if result.get("status") == "filled":
                logger.info(f"Auto‑executed {signal['symbol']} {signal['direction']} lot {signal['recommended_lot']}")
                self.notif_center.add({"type": "execution", "symbol": signal["symbol"], "direction": signal["direction"], "order_id": result.get("order_id"), "lot": signal["recommended_lot"], "status": "filled"})
        except Exception as e:
            logger.error(f"Auto‑execution error: {e}")
