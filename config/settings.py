# leviathan/config/settings.py
import os
import json
from pathlib import Path
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator, ValidationInfo
from pydantic_settings import BaseSettings

class RiskConfig(BaseModel):
    risk_percent: float = 1.0
    max_daily_loss: float = 2.0
    max_weekly_loss: float = 5.0
    max_drawdown: float = 5.0
    rr: float = 2.5
    dynamic_scaling: bool = True
    black_swan_protection: bool = True
    volatility_scaling: bool = True

class NotificationConfig(BaseModel):
    enabled: bool = True
    max_stored: int = 1000
    push_enabled: bool = False
    sound_enabled: bool = True

class LoggingConfig(BaseModel):
    level: str = "INFO"
    file_enabled: bool = True
    rotation: str = "1 day"
    retention: str = "7 days"
    format: str = "{time} | {level} | {name}:{function}:{line} | {message}"

class ConfigModel(BaseModel):
    symbols: List[str] = [
        "EURUSD=X", "GBPUSD=X", "AUDUSD=X", "USDJPY=X", "NZDUSD=X",
        "BTC-USD", "ETH-USD", "SOL-USD", "XRP-USD", "ADA-USD",
        "GC=F", "SI=F", "CL=F", "NG=F", "HG=F",
        "^GSPC", "^DJI", "^IXIC", "^RUT"
    ]
    risk: RiskConfig = RiskConfig()
    notification: NotificationConfig = NotificationConfig()
    logging: LoggingConfig = LoggingConfig()
    lock_in: Dict[str, Any] = {"daily_goal_pnl": 100, "daily_goal_trades": 3}
    school_mode: Dict[str, Any] = {"enabled": False, "start_hour": 7, "end_hour": 15}
    auto_trade: Dict[str, Any] = {"enabled": False, "mt5_webhook_url": ""}
    prop_firm: Dict[str, Any] = {"enabled": True, "max_daily_loss": 5.0, "max_total_loss": 10.0, "target_profit": 10.0}
    leviathan: Dict[str, Any] = {"enabled": True, "bayesian_scoring": True, "monte_carlo_simulations": True}
    rl: Dict[str, Any] = {"enabled": True, "learning_rate": 0.1, "discount_factor": 0.95, "exploration_rate": 0.2}
    nexus: Dict[str, Any] = {"unified_decision": True, "black_swan_protection": True}
    ultimate: Dict[str, Any] = {
        "dynamic_strategy_adaptation": True,
        "adaptive_take_profit": True,
        "vader_sentiment": True,
        "gradient_parameter_optimization": True,
        "risk_of_ruin_calculator": True,
        "multi_distribution_monte_carlo": True
    }
    education: Dict[str, Any] = {"enabled": True, "daily_lesson": True}
    eternal: Dict[str, Any] = {"dqn_enabled": True, "multi_strategy": True, "global_state": True, "genesis_report": True}

    @field_validator("symbols", mode="before")
    def validate_symbols(cls, v: List[str]) -> List[str]:
        if not v:
            raise ValueError("At least one symbol required")
        return v

class Settings(BaseSettings):
    ENV: str = "development"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # API Keys
    YAHOO_API_KEY: Optional[str] = None
    ALPHA_VANTAGE_API_KEY: Optional[str] = None
    POLYGON_API_KEY: Optional[str] = None
    GROQ_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    DEEPSEEK_API_KEY: Optional[str] = None
    TELEGRAM_TOKEN: Optional[str] = None
    TELEGRAM_CHAT_ID: Optional[str] = None
    MT5_WEBHOOK_URL: Optional[str] = None
    
    config: ConfigModel = Field(default_factory=ConfigModel)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @field_validator("config", mode="before")
    def load_config_json(cls, v, info: ValidationInfo):
        config_path = Path("config.json")
        if config_path.exists():
            with open(config_path, "r") as f:
                data = json.load(f)
                return ConfigModel(**data)
        return v

    def save_config(self):
        config_path = Path("config.json")
        with open(config_path, "w") as f:
            json.dump(self.config.model_dump(), f, indent=2)

    def reload(self):
        """Reload config from file without restarting."""
        config_path = Path("config.json")
        if config_path.exists():
            with open(config_path, "r") as f:
                data = json.load(f)
                self.config = ConfigModel(**data)

def get_settings() -> Settings:
    return Settings()
