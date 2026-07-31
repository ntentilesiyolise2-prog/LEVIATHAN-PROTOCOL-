# leviathan/api/routes.py
from fastapi import APIRouter, Request, HTTPException, Query
from fastapi.responses import JSONResponse
from loguru import logger
import asyncio

from ..core import Engine, NotificationCenter
from ..config import get_settings

router = APIRouter()

_engine: Engine = None

def set_engine(engine: Engine):
    global _engine
    _engine = engine

# ----- Helper -----
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
    # Update config model
    for key, value in data.items():
        if hasattr(engine.settings.config, key):
            setattr(engine.settings.config, key, value)
    engine.settings.save_config()
    logger.info(f"Config updated: {data}")
    # Publish event
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
    # Placeholder; we'll implement full balance later
    return {"balance": 10000.0, "equity": 10000.0, "margin": 0.0, "free_margin": 10000.0, "margin_level": 100.0}

# ----- Signal (placeholder) -----
@router.get("/signal")
async def get_signal(symbol: str = Query("EURUSD=X")):
    # Placeholder signal; real one will come from the signal engine
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
    # Placeholder; will return a list of signals from the engine
    return []

# ----- Market Pulse (placeholder) -----
@router.get("/market_pulse")
async def market_pulse():
    # Placeholder; will fetch real data later
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
    # Placeholder; will fetch from trade journal
    return {"trades": []}

# ----- Assistant Chat -----
@router.post("/assistant/chat")
async def assistant_chat(request: Request):
    data = await request.json()
    message = data.get("message", "")
    if not message:
        return {"response": "Please ask a question."}
    # Placeholder; later we'll call the assistant
    return {"response": f"I received your question: '{message}'. I'm still under development, but I'll soon give you real answers."}
