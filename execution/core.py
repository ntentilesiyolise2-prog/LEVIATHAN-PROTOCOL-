# leviathan/execution/core.py
import asyncio
from typing import Dict, Any
from loguru import logger
from .broker import BrokerInterface
from ..core.notification_center import NotificationCenter
from ..core.events import EventBus, Event

class ExecutionCore:
    def __init__(self, broker: BrokerInterface, notif_center: NotificationCenter, event_bus: EventBus):
        self.broker = broker; self.notif_center = notif_center; self.event_bus = event_bus; self.active_trades = {}
    async def execute_with_management(self, signal: Dict[str, Any]) -> Dict[str, Any]:
        if signal['direction'] == 'WAIT': return {'status':'skipped','reason':'No signal'}
        volume = signal.get('recommended_lot', 0.01)
        order = await self.broker.execute_order(symbol=signal['symbol'], direction=signal['direction'], entry=signal['entry'], sl=signal['sl'], tp=signal['tp'], volume=volume)
        if order.get('status') == 'filled':
            trade_id = order['order_id']
            self.active_trades[trade_id] = {'signal': signal, 'entry': signal['entry'], 'sl': signal['sl'], 'tp': signal['tp'], 'volume': volume, 'partials_taken': 0, 'trailing_activated': False}
            asyncio.create_task(self._monitor_trade(trade_id))
            self.notif_center.add({'type': 'execution', 'symbol': signal['symbol'], 'direction': signal['direction'], 'entry': signal['entry'], 'sl': signal['sl'], 'tp': signal['tp'], 'lot': volume, 'order_id': trade_id, 'status': 'filled'})
            await self.event_bus.publish(Event(type='trade_opened', data=order))
        return order

    async def _monitor_trade(self, trade_id: str):
        while trade_id in self.active_trades:
            await asyncio.sleep(1)
            trade = self.active_trades.get(trade_id)
            if not trade: break
            price = await self.broker.get_price(trade['signal']['symbol'])
            if price is None: continue
            if trade['partials_taken'] == 0:
                tp1 = trade['entry'] + (trade['tp'] - trade['entry']) * 0.25 if trade['signal']['direction'] == 'BUY' else trade['entry'] - (trade['entry'] - trade['tp']) * 0.25
                if (trade['signal']['direction'] == 'BUY' and price >= tp1) or (trade['signal']['direction'] == 'SELL' and price <= tp1):
                    close_vol = trade['volume'] * 0.25
                    await self.broker.close_position_partial(trade_id, close_vol)
                    trade['volume'] -= close_vol; trade['partials_taken'] = 1
                    self.notif_center.add({'type':'partial_tp','trade_id':trade_id,'message':'25% TP hit'})
            elif trade['partials_taken'] == 1:
                tp2 = trade['entry'] + (trade['tp'] - trade['entry']) * 0.50 if trade['signal']['direction'] == 'BUY' else trade['entry'] - (trade['entry'] - trade['tp']) * 0.50
                if (trade['signal']['direction'] == 'BUY' and price >= tp2) or (trade['signal']['direction'] == 'SELL' and price <= tp2):
                    close_vol = trade['volume'] * 0.5
                    await self.broker.close_position_partial(trade_id, close_vol)
                    trade['volume'] -= close_vol; trade['partials_taken'] = 2; trade['trailing_activated'] = True
                    self.notif_center.add({'type':'partial_tp','trade_id':trade_id,'message':'50% TP hit, trailing activated'})
            if trade['trailing_activated']:
                atr = trade['signal'].get('atr', 0.01)
                if trade['signal']['direction'] == 'BUY':
                    new_sl = price - atr * 1.5
                    if new_sl > trade['sl']:
                        await self.broker.modify_position(trade_id, new_sl, trade['tp'])
                        trade['sl'] = new_sl
                else:
                    new_sl = price + atr * 1.5
                    if new_sl < trade['sl']:
                        await self.broker.modify_position(trade_id, new_sl, trade['tp'])
                        trade['sl'] = new_sl
        if trade_id in self.active_trades: del self.active_trades[trade_id]
