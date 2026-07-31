# leviathan/core/events.py
import asyncio
from typing import Dict, List, Callable, Any, Awaitable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import inspect

class EventPriority(Enum):
    HIGH = 0
    NORMAL = 1
    LOW = 2

@dataclass
class Event:
    type: str
    data: Any
    timestamp: datetime = field(default_factory=datetime.utcnow)
    priority: EventPriority = EventPriority.NORMAL

class EventBus:
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}
        self._async_subscribers: Dict[str, List[Callable]] = {}
        self._lock = asyncio.Lock()

    def subscribe(self, event_type: str, callback: Callable, async_: bool = False):
        """Register a callback for an event type."""
        if async_:
            if event_type not in self._async_subscribers:
                self._async_subscribers[event_type] = []
            self._async_subscribers[event_type].append(callback)
        else:
            if event_type not in self._subscribers:
                self._subscribers[event_type] = []
            self._subscribers[event_type].append(callback)

    def unsubscribe(self, event_type: str, callback: Callable):
        """Remove a callback."""
        if event_type in self._subscribers:
            self._subscribers[event_type] = [c for c in self._subscribers[event_type] if c != callback]
        if event_type in self._async_subscribers:
            self._async_subscribers[event_type] = [c for c in self._async_subscribers[event_type] if c != callback]

    async def publish(self, event: Event):
        """Publish an event to all subscribers."""
        # Sync subscribers (run in thread pool if blocking)
        for callback in self._subscribers.get(event.type, []):
            if inspect.iscoroutinefunction(callback):
                # if a sync subscriber is async, await it
                await callback(event)
            else:
                # run sync callbacks in a thread to avoid blocking
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, callback, event)

        # Async subscribers
        for callback in self._async_subscribers.get(event.type, []):
            await callback(event)
