# leviathan/core/engine.py
import asyncio
import signal
from pathlib import Path
from typing import Optional
from loguru import logger

from ..config import get_settings
from .events import EventBus, Event
from .notification_center import NotificationCenter
from ..data import MarketDataService
from ..features import FeatureStore
from ..strategies import StrategySwarm
from ..nexus import MetaNexus
from ..signals import ContinuousSignalEngine
from ..execution import SimulatorBroker, ExecutionCore
from ..risk import RiskEngine, PropFirm
from ..learning import DQNAgent, GeneticOptimizer
from ..portfolio import PortfolioManager
from ..predictive import LSTMPredictor, OptionsAnalyzer, OnChainData, PredictiveSentiment
from ..plugin_manager import PluginManager
from ..feature_requests import FeatureRequestManager
from ..auto_updater import AutoUpdater

class Engine:
    def __init__(self):
        self.settings = get_settings()
        self.event_bus = EventBus()
        self.notification_center = NotificationCenter(max_stored=self.settings.config.notification.max_stored)
        self.data_service: Optional[MarketDataService] = None
        self.feature_store: Optional[FeatureStore] = None
        self.signal_engine: Optional[ContinuousSignalEngine] = None
        self.broker: Optional[SimulatorBroker] = None
        self.execution_core: Optional[ExecutionCore] = None
        self.nexus: Optional[MetaNexus] = None
        self.swarm: Optional[StrategySwarm] = None
        self.risk_engine: Optional[RiskEngine] = None
        self.prop_firm: Optional[PropFirm] = None
        self.dqn: Optional[DQNAgent] = None
        self.genetic: Optional[GeneticOptimizer] = None
        self.portfolio: Optional[PortfolioManager] = None
        self.predictor: Optional[LSTMPredictor] = None
        self.options: Optional[OptionsAnalyzer] = None
        self.onchain: Optional[OnChainData] = None
        self.sentiment: Optional[PredictiveSentiment] = None
        self.plugin_manager: Optional[PluginManager] = None
        self.feature_request_manager: Optional[FeatureRequestManager] = None
        self.auto_updater: Optional[AutoUpdater] = None
        self._initialized = False
        self._running = False
        self._tasks = []
        self._signal_handlers_set = False
        self._signal_cache = {}
        self._journal = []

    def setup_logging(self):
        log_path = Path("logs")
        log_path.mkdir(exist_ok=True)
        level = self.settings.config.logging.level if not self.settings.DEBUG else "DEBUG"
        if self.settings.config.logging.file_enabled:
            logger.add(log_path / "leviathan_{time}.log", rotation=self.settings.config.logging.rotation,
                       retention=self.settings.config.logging.retention, level=level,
                       format=self.settings.config.logging.format)
        logger.add(lambda msg: print(msg, end=""), level=level)
        logger.info("Logging initialised")

    async def start(self):
        if self._initialized:
            return
        self.setup_logging()
        logger.info("LEVIATHAN 21.0 Engine starting...")

        if not self._signal_handlers_set:
            loop = asyncio.get_event_loop()
            for sig in (signal.SIGINT, signal.SIGTERM):
                loop.add_signal_handler(sig, lambda: asyncio.create_task(self.shutdown()))
            self._signal_handlers_set = True

        # Plugin Manager
        self.plugin_manager = PluginManager()
        self.plugin_manager.discover_plugins()
        logger.info("PluginManager initialised")

        # Feature Request Manager
        self.feature_request_manager = FeatureRequestManager()
        logger.info("FeatureRequestManager initialised")

        # Auto-Updater
        self.auto_updater = AutoUpdater()
        logger.info("AutoUpdater initialised")

        # Data Service
        self.data_service = MarketDataService(self.settings, self.event_bus, self.notification_center)
        await self.data_service.start()
        logger.info("MarketDataService started")

        # Feature Store
        self.feature_store = FeatureStore(self.data_service, self.event_bus)
        logger.info("FeatureStore initialised")

        # Strategy Swarm
        self.swarm = StrategySwarm()
        logger.info("StrategySwarm initialised")

        # Meta-Nexus
        self.nexus = MetaNexus()
        logger.info("MetaNexus initialised")

        # Broker & Execution Core
        initial_balance = self.settings.config.initial_balance
        self.broker = SimulatorBroker(initial_balance=initial_balance)
        self.execution_core = ExecutionCore(self.broker, self.notification_center, self.event_bus)
        logger.info("Broker and ExecutionCore initialised")

        # Risk & Prop Firm
        self.risk_engine = RiskEngine(initial_balance=initial_balance)
        self.prop_firm = PropFirm()
        logger.info("RiskEngine and PropFirm initialised")

        # DQN & Genetic
        self.dqn = DQNAgent()
        self.genetic = GeneticOptimizer({}, lambda x: 0.5, generations=5)
        logger.info("DQN and GeneticOptimizer initialised")

        # Portfolio
        self.portfolio = PortfolioManager()
        logger.info("PortfolioManager initialised")

        # Predictive modules
        self.predictor = LSTMPredictor()
        self.options = OptionsAnalyzer()
        self.onchain = OnChainData()
        self.sentiment = PredictiveSentiment()
        logger.info("Predictive modules initialised")

        # Continuous Signal Engine
        self.signal_engine = ContinuousSignalEngine(
            feature_store=self.feature_store,
            data_service=self.data_service,
            notif_center=self.notification_center,
            event_bus=self.event_bus,
            broker=self.broker,
            nexus=self.nexus,
            swarm=self.swarm,
            symbols=self.settings.config.symbols,
            interval=5.0,
            target_profit=self.settings.config.target_profit_per_trade
        )
        await self.signal_engine.start()
        logger.info("ContinuousSignalEngine started")

        self._initialized = True
        self._running = True
        self._tasks.append(asyncio.create_task(self._health_task()))
        logger.info("Engine started successfully")

    async def shutdown(self):
        if not self._running:
            return
        logger.info("Engine shutting down...")
        self._running = False
        if self.signal_engine:
            await self.signal_engine.stop()
        if self.data_service:
            await self.data_service.stop()
        for task in self._tasks:
            task.cancel()
        await asyncio.gather(*self._tasks, return_exceptions=True)
        self._tasks.clear()
        logger.info("Engine stopped")

    async def _health_task(self):
        while self._running:
            await asyncio.sleep(30)
            logger.debug("Health check passed")

    def get_notification_center(self): return self.notification_center
    def get_event_bus(self): return self.event_bus
    def get_settings(self): return self.settings
    def get_data_service(self): return self.data_service
    def get_feature_store(self): return self.feature_store
    def get_signal_engine(self): return self.signal_engine
    def get_broker(self): return self.broker
    def get_execution_core(self): return self.execution_core
    def get_nexus(self): return self.nexus
    def get_swarm(self): return self.swarm
    def get_risk_engine(self): return self.risk_engine
    def get_prop_firm(self): return self.prop_firm
    def get_dqn(self): return self.dqn
    def get_genetic(self): return self.genetic
    def get_portfolio(self): return self.portfolio
    def get_predictor(self): return self.predictor
    def get_options(self): return self.options
    def get_onchain(self): return self.onchain
    def get_sentiment(self): return self.sentiment
    def get_plugin_manager(self): return self.plugin_manager
    def get_feature_request_manager(self): return self.feature_request_manager
    def get_auto_updater(self): return self.auto_updater
    def get_signal_cache(self): return self._signal_cache
    def get_journal(self): return self._journal

    async def reload_plugins(self):
        if self.plugin_manager:
            self.plugin_manager.discover_plugins()
            logger.info("Plugins reloaded")
            await self.event_bus.publish(Event(type="plugins_reloaded", data={}))

    def reload_config(self):
        self.settings.reload()
        logger.info("Configuration reloaded")
        asyncio.create_task(self.event_bus.publish(Event(type="config_reload", data={"settings": self.settings.config.model_dump()})))
