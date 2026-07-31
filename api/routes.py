# leviathan/api/routes.py
from fastapi import APIRouter, Request, HTTPException, Query
from fastapi.responses import JSONResponse
from loguru import logger
import asyncio
from datetime import datetime  # added for timestamp

from ..core import Engine, NotificationCenter
from ..config import get_settings

router = APIRouter()

_engine: Engine = None

def set_engine(engine: Engine):
    global _engine
    _engine = engine

def get_engine():
    if _engine is None:
        raise HTTPException(status_code=503, detail="Engine not initialized")
    return _engine

# ----- Root -----
@router.get("/")
async def root():
    return {"message": "🦈 LEVIATHAN 8.0 – LIVE TERMINAL", "status": "online"}

# ----- Health -----
@router.get("/health")
async def health():
    engine = get_engine()
    return {
        "status": "ok",
        "version": "8.0.0",
        "running": engine._running,
        "initialized": engine._initialized,
        "notifications": engine.notification_center.count_unread(),
        "data_service": engine.data_service is not None,  # new
    }

# ----- Config -----
@router.get("/config")
async def get_config():
    engine = get_engine()
    return engine.settings.config.model_dump()

@router.post("/config")
async def update_config(request: Request):
    engine = get_engine()
    data = await request.json()
    for key, value in data.items():
        if hasattr(engine.settings.config, key):
            setattr(engine.settings.config, key, value)
    engine.settings.save_config()
    logger.info(f"Config updated: {data}")
    await engine.event_bus.publish(
        Event(type="config_updated", data={"config": data})
    )
    return {"status": "updated", "config": engine.settings.config.model_dump()}

@router.post("/config/reload")
async def reload_config():
    engine = get_engine()
    engine.reload_config()
    return {"status": "reloaded"}

# ----- Notifications -----
@router.get("/notifications")
async def get_notifications(limit: int = Query(50, ge=1, le=200)):
    engine = get_engine()
    return {"notifications": engine.notification_center.get_all(limit)}

@router.get("/notifications/unread")
async def get_unread():
    engine = get_engine()
    return {"unread": engine.notification_center.get_unread()}

@router.post("/notifications/mark_read")
async def mark_read(request: Request):
    engine = get_engine()
    data = await request.json()
    notification_id = data.get("id")
    if not notification_id:
        raise HTTPException(status_code=400, detail="Missing id")
    engine.notification_center.mark_read(notification_id)
    return {"status": "marked_read"}

@router.post("/notifications/mark_all_read")
async def mark_all_read():
    engine = get_engine()
    engine.notification_center.mark_all_read()
    return {"status": "all_marked_read"}

# ----- Balance (placeholder) -----
@router.get("/balance")
async def get_balance():
    return {"balance": 10000.0, "equity": 10000.0, "margin": 0.0, "free_margin": 10000.0, "margin_level": 100.0}

# ----- NEW: Price endpoint (real-time) -----
@router.get("/price/{symbol}")
async def get_price(symbol: str):
    engine = get_engine()
    data_service = engine.get_data_service()
    if data_service is None:
        raise HTTPException(status_code=503, detail="Data service not ready")
    price = await data_service.get_price(symbol)
    if price is None:
        raise HTTPException(status_code=404, detail="Price not available")
    return {
        "symbol": symbol,
        "price": price,
        "timestamp": datetime.utcnow().isoformat(),
        "market_open": data_service.is_market_open(symbol)
    }

# ----- Signal (placeholder) -----
@router.get("/signal")
async def get_signal(symbol: str = Query("EURUSD=X")):
    return {
        "symbol": symbol,
        "direction": "WAIT",
        "confidence": 0,
        "entry": 0,
        "sl": 0,
        "tp": 0,
        "rationale": "Signal engine not started",
        "expiry": None
    }

# ----- Scan (placeholder) -----
@router.get("/scan")
async def scan_all(symbols: Optional[str] = Query(None)):
    return []

# ----- Market Pulse (placeholder) -----
@router.get("/market_pulse")
async def market_pulse():
    return {
        "dxy": 104.20, "dxy_change": 0.12,
        "vix": 15.30, "vix_change": -0.8,
        "gold": 2340.00, "gold_change": 0.45,
        "btc": 67200.00, "btc_change": 1.5,
        "eth": 3450.00, "eth_change": 0.8,
        "spx": 5200.00, "spx_change": 0.32,
        "oil": 78.50, "oil_change": 0.21,
        "us10y": 4.12, "us10y_change": -0.03,
    }

# ----- Journal (placeholder) -----
@router.get("/journal")
async def get_journal():
    return {"trades": []}

# ----- Assistant Chat (placeholder, no AI dependency) -----
@router.post("/assistant/chat")
async def assistant_chat(request: Request):
    data = await request.json()
    message = data.get("message", "")
    if not message:
        return {"response": "Please ask a question."}
    # Simple rule-based response (no AI API)
    if "price" in message.lower():
        return {"response": "I can fetch live prices for you. Use the /price endpoint."}
    elif "signal" in message.lower():
        return {"response": "Signals are being generated. Check the Signals tab."}
    else:
        return {"response": f"Command received: '{message}'. I'm a self-contained assistant that doesn't rely on external AI."}
