# leviathan/core/engine.py
import asyncio
import signal
from pathlib import Path
from typing import Optional, Dict, Any
from loguru import logger

from ..config import get_settings
from .events import EventBus, Event
from .notification_center import NotificationCenter

class Engine:
    def __init__(self):
        self.settings = get_settings()
        self.event_bus = EventBus()
        self.notification_center = NotificationCenter(
            max_stored=self.settings.config.notification.max_stored
        )
        self._initialized = False
        self._running = False
        self._tasks = []
        self._signal_handlers_set = False

    def setup_logging(self):
        log_path = Path("logs")
        log_path.mkdir(exist_ok=True)
        level = self.settings.config.logging.level if not self.settings.DEBUG else "DEBUG"
        if self.settings.config.logging.file_enabled:
            logger.add(
                log_path / "leviathan_{time}.log",
                rotation=self.settings.config.logging.rotation,
                retention=self.settings.config.logging.retention,
                level=level,
                format=self.settings.config.logging.format,
            )
        logger.add(
            lambda msg: print(msg, end=""),
            level=level,
            format=self.settings.config.logging.format,
        )
        logger.info("Logging initialised")

    async def start(self):
        if self._initialized:
            return
        self.setup_logging()
        logger.info("LEVIATHAN 8.0 Engine starting...")
        
        # Register signal handlers
        if not self._signal_handlers_set:
            loop = asyncio.get_event_loop()
            for sig in (signal.SIGINT, signal.SIGTERM):
                loop.add_signal_handler(sig, lambda: asyncio.create_task(self.shutdown()))
            self._signal_handlers_set = True

        # Start background tasks (placeholder for data service, signal engine, etc.)
        # We'll add them later; for now, just a health task
        self._tasks.append(asyncio.create_task(self._health_task()))
        
        self._initialized = True
        self._running = True
        logger.info("Engine started successfully")

    async def shutdown(self):
        if not self._running:
            return
        logger.info("Engine shutting down...")
        self._running = False
        for task in self._tasks:
            task.cancel()
        await asyncio.gather(*self._tasks, return_exceptions=True)
        self._tasks.clear()
        logger.info("Engine stopped")

    async def _health_task(self):
        """Periodic health check task."""
        while self._running:
            await asyncio.sleep(30)
            # In future, we can check data providers, etc.
            logger.debug("Health check passed")

    def get_notification_center(self):
        return self.notification_center

    def get_event_bus(self):
        return self.event_bus

    def get_settings(self):
        return self.settings

    def reload_config(self):
        """Reload configuration without restarting."""
        self.settings.reload()
        logger.info("Configuration reloaded")
        # Optionally, publish a config reload event
        asyncio.create_task(self.event_bus.publish(
            Event(type="config_reload", data={"settings": self.settings.config.model_dump()})
        ))
