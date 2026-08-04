# leviathan/api/routes.py
from fastapi import APIRouter, Request, HTTPException, Query, UploadFile, File
from fastapi.responses import JSONResponse
from loguru import logger
import os, json, time, asyncio, random, re
from datetime import datetime
from typing import Optional, List, Dict, Any
import numpy as np
import pandas as pd
import yfinance as yf
import ta
import requests
from pathlib import Path

from ..core import Engine
from ..config import get_settings

router = APIRouter()
_engine: Engine = None
BASE_URL = ""

def set_engine(engine: Engine):
    global _engine
    _engine = engine

def get_engine():
    if _engine is None:
        raise HTTPException(status_code=503, detail="Engine not initialized")
    return _engine

# ---------- Helper: Data ----------
def get_data(symbol, period="5d", interval="5m"):
    try:
        df = yf.download(symbol, period=period, interval=interval, progress=False)
        return df if not df.empty else None
    except:
        return None

def compute_features(df):
    if df is None or df.empty:
        return {}
    close = df['Close']; high = df['High']; low = df['Low']; volume = df['Volume']
    features = {}
    features['rsi_14'] = ta.rsi(close, 14).iloc[-1] if len(close)>14 else 50
    features['atr_14'] = ta.atr(high, low, close, 14).iloc[-1] if len(close)>14 else 0.01
    features['ema_50'] = ta.ema(close, 50).iloc[-1] if len(close)>50 else close.iloc[-1]
    features['ema_200'] = ta.ema(close, 200).iloc[-1] if len(close)>200 else close.iloc[-1]
    features['last_price'] = close.iloc[-1]
    return features

# ---------- Root & Health ----------
@router.get("/")
async def root():
    return {"message": "LEVIATHAN 21.0", "version": "21.0.0", "status": "online"}

@router.get("/health")
async def health():
    engine = get_engine()
    data_source = "Mock"
    if engine.data_service:
        data_source = engine.data_service.provider_name if hasattr(engine.data_service, 'provider_name') else "Yahoo"
    return {
        "status": "ok", "version": "21.0.0", "running": engine._running,
        "initialized": engine._initialized,
        "notifications": engine.notification_center.count_unread(),
        "data_service": engine.data_service is not None,
        "data_source": data_source,
        "feature_store": engine.feature_store is not None,
        "signal_engine": engine.signal_engine is not None,
        "broker": engine.broker is not None,
        "plugin_manager": engine.plugin_manager is not None,
    }

# ---------- Account / Balance ----------
@router.get("/account")
async def get_account():
    engine = get_engine()
    broker = engine.get_broker()
    if broker is None:
        return {"balance": 0, "equity": 0, "margin": 0, "free_margin": 0, "margin_level": 0,
                "win_rate": 0, "profit_factor": 0, "drawdown": 0, "today_pnl": 0, "initial_balance": 10000}
    info = await broker.get_account_info()
    journal = engine.get_journal()
    trades = journal
    wins = sum(1 for t in trades if t.get('win', False))
    total = len(trades)
    win_rate = (wins / total * 100) if total > 0 else 0
    gross_profit = sum(t.get('pnl', 0) for t in trades if t.get('pnl', 0) > 0)
    gross_loss = abs(sum(t.get('pnl', 0) for t in trades if t.get('pnl', 0) < 0))
    pf = gross_profit / gross_loss if gross_loss > 0 else 0
    today = datetime.utcnow().date()
    today_pnl = sum(t.get('pnl', 0) for t in trades if datetime.fromisoformat(t.get('closed_at', '')).date() == today)
    return {
        "balance": info.get("balance", 0),
        "equity": info.get("equity", 0),
        "margin": info.get("margin", 0),
        "free_margin": info.get("free_margin", 0),
        "margin_level": info.get("margin_level", 0),
        "win_rate": round(win_rate, 2),
        "profit_factor": round(pf, 2),
        "drawdown": engine.risk_engine.drawdown if engine.risk_engine else 0,
        "today_pnl": round(today_pnl, 2),
        "initial_balance": engine.settings.config.initial_balance,
    }

@router.post("/balance")
async def set_balance(request: Request):
    engine = get_engine()
    data = await request.json()
    new_balance = data.get("balance")
    if new_balance is None or new_balance < 0:
        raise HTTPException(status_code=400, detail="Invalid balance")
    broker = engine.get_broker()
    if broker is None:
        raise HTTPException(status_code=503, detail="Broker not ready")
    if hasattr(broker, 'set_balance'):
        await broker.set_balance(new_balance)
    engine.settings.config.initial_balance = new_balance
    engine.settings.save_config()
    return {"status": "updated", "balance": new_balance}

# ---------- Signals ----------
@router.get("/signals")
async def get_signals():
    engine = get_engine()
    cache = engine.get_signal_cache()
    return {"signals": list(cache.values())}

@router.get("/signal/{symbol}")
async def get_signal(symbol: str):
    engine = get_engine()
    se = engine.get_signal_engine()
    if se is None:
        raise HTTPException(status_code=503, detail="Signal engine not ready")
    from ..signals import SignalPipeline
    pipeline = SignalPipeline(engine.feature_store, engine.data_service, engine.nexus, engine.swarm)
    signal = await pipeline.generate_signal(symbol, "1h")
    if not signal or signal.get("direction") == "WAIT":
        return {"symbol": symbol, "direction": "WAIT", "confidence": 0, "rationale": "No signal"}
    price = signal.get("price", 0)
    atr = await engine.feature_store.get_feature(symbol, "atr_14", "1h") or price * 0.01
    if signal["direction"] == "BUY":
        entry = price; sl = entry - atr * 2.0; tp = entry + atr * 3.0
    else:
        entry = price; sl = entry + atr * 2.0; tp = entry - atr * 3.0
    signal["entry"] = round(entry, 5); signal["sl"] = round(sl, 5); signal["tp"] = round(tp, 5)
    signal["atr"] = atr
    signal["data_source"] = engine.data_service.provider_name if engine.data_service else "unknown"
    return signal

# ---------- Execute Trade ----------
@router.post("/execute")
async def execute(request: Request):
    engine = get_engine()
    data = await request.json()
    symbol = data.get("symbol")
    direction = data.get("direction")
    entry = data.get("entry")
    sl = data.get("sl")
    tp = data.get("tp")
    volume = data.get("volume", 0.01)
    if not all([symbol, direction, entry, sl, tp]):
        raise HTTPException(status_code=400, detail="Missing fields")
    exec_core = engine.get_execution_core()
    if exec_core is None:
        raise HTTPException(status_code=503, detail="Execution core not ready")
    signal = {'symbol': symbol, 'direction': direction, 'entry': entry, 'sl': sl, 'tp': tp, 'recommended_lot': volume}
    result = await exec_core.execute_with_management(signal)
    result["data_source"] = engine.data_service.provider_name if engine.data_service else "unknown"
    return result

# ---------- Positions ----------
@router.get("/positions")
async def get_positions():
    engine = get_engine()
    broker = engine.get_broker()
    if broker is None:
        return {"positions": []}
    pos = await broker.get_positions()
    return {"positions": pos}

@router.post("/close_position")
async def close_position(request: Request):
    engine = get_engine()
    data = await request.json()
    position_id = data.get("id")
    if not position_id:
        raise HTTPException(status_code=400, detail="Missing position id")
    broker = engine.get_broker()
    if broker is None:
        raise HTTPException(status_code=503, detail="Broker not ready")
    result = await broker.close_position(position_id)
    return result

# ---------- Risk ----------
@router.get("/risk")
async def get_risk():
    engine = get_engine()
    risk = engine.get_risk_engine()
    if risk is None:
        return {"var": 0, "cvar": 0, "drawdown": 0, "sharpe": 0}
    var = risk.calculate_var(); cvar = risk.calculate_cvar(); dd = risk.drawdown
    trades = engine.get_journal()
    returns = [t.get('pnl', 0) for t in trades if 'pnl' in t]
    sharpe = 0
    if len(returns) > 1:
        mean = np.mean(returns); std = np.std(returns)
        sharpe = (mean / std) * np.sqrt(252) if std > 0 else 0
    return {"var": var, "cvar": cvar, "drawdown": dd, "sharpe": round(sharpe, 2)}

@router.get("/propfirm")
async def get_propfirm():
    engine = get_engine()
    prop = engine.get_prop_firm()
    if prop is None:
        return {"status": "NOT_CONFIGURED"}
    return prop.get_status()

# ---------- Journal ----------
@router.get("/journal")
async def get_journal():
    engine = get_engine()
    journal = engine.get_journal()
    return {"trades": journal}

# ---------- News ----------
@router.get("/news")
async def get_news(limit: int = Query(10), symbol: Optional[str] = None):
    engine = get_engine()
    sentiment = engine.get_sentiment()
    if sentiment is None:
        return {"news": []}
    if symbol:
        result = sentiment.analyze(symbol)
        return {"news": [{"title": f"Sentiment for {symbol}: {result['label']} ({result['score']})", "source": "RSS", "published": "now"}]}
    return {"news": [{"title": "LEVIATHAN active", "source": "System", "published": "now"}]}

# ---------- AI Chat ----------
try:
    import google.generativeai as genai
except:
    genai = None

GEMINI_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_KEY and genai:
    genai.configure(api_key=GEMINI_KEY)
    gemini_model = genai.GenerativeModel('gemini-1.5-flash')
else:
    gemini_model = None

MEMORY_FILE = "ai_memory.json"
def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    return {"history": [], "knowledge": []}
def save_memory(memory):
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=2)

def fallback_response(message):
    if "price" in message.lower():
        return "Get live prices via the Dashboard or /price endpoint."
    elif "signal" in message.lower():
        return "Check the Signals tab for live BUY/SELL signals."
    elif "risk" in message.lower():
        return "Your current risk is 1% per trade. Max daily loss is 2%."
    else:
        return f"I'm LEVIATHAN AI. You asked: '{message}'"

@router.post("/ai/chat")
async def ai_chat(request: Request):
    data = await request.json()
    message = data.get("message", "")
    # Check for feature request
    if "add" in message.lower() and ("feature" in message.lower() or "function" in message.lower()):
        # Create a feature request
        engine = get_engine()
        fm = engine.get_feature_request_manager()
        req = fm.add_request(message, requester="ai_assistant")
        return {"response": f"✅ Feature request created: '{message}'. I've logged it for development."}
    memory = load_memory()
    memory["history"].append({"role": "user", "content": message})
    context = "\n".join([f"{h['role']}: {h['content']}" for h in memory["history"][-10:]])
    if gemini_model:
        try:
            prompt = f"You are LEVIATHAN AI. Context:\n{context}\nUser: {message}\nProvide a clear, helpful response."
            response = gemini_model.generate_content(prompt)
            reply = response.text
        except:
            reply = fallback_response(message)
    else:
        reply = fallback_response(message)
    memory["history"].append({"role": "assistant", "content": reply})
    save_memory(memory)
    return {"response": reply}

# ---------- AI Feature Request Tool ----------
@router.post("/ai/request_feature")
async def ai_request_feature(request: Request):
    data = await request.json()
    description = data.get("description")
    if not description:
        raise HTTPException(status_code=400, detail="Missing description")
    engine = get_engine()
    fm = engine.get_feature_request_manager()
    req = fm.add_request(description, requester="ai_assistant")
    return {"status": "created", "request": req}

# ---------- Chart Scanner (AI) ----------
@router.post("/analyze_chart")
async def analyze_chart(request: Request):
    data = await request.json()
    symbol = data.get("symbol", "EURUSD=X")
    # We'll simulate a pattern detection using rule‑based logic
    engine = get_engine()
    fs = engine.get_feature_store()
    if fs is None:
        return {"pattern": "Unknown", "confidence": 0, "direction": "WAIT"}
    features = await fs.get_features(symbol, "1h")
    price = features.get("last_price", 0)
    ema200 = features.get("ema_200", price)
    rsi = features.get("rsi_14", 50)
    if price > ema200 and rsi > 60:
        return {"pattern": "Bullish Trend", "confidence": 75, "direction": "BUY", "analysis": "Price above 200 EMA, RSI strong."}
    elif price < ema200 and rsi < 40:
        return {"pattern": "Bearish Trend", "confidence": 75, "direction": "SELL", "analysis": "Price below 200 EMA, RSI weak."}
    else:
        return {"pattern": "Consolidation", "confidence": 50, "direction": "WAIT", "analysis": "No clear trend."}

# ---------- Backtesting ----------
@router.post("/backtest")
async def run_backtest(request: Request):
    data = await request.json()
    symbol = data.get("symbol", "EURUSD=X")
    start = data.get("start", "2024-01-01")
    end = data.get("end", "2024-12-31")
    try:
        df = get_data(symbol, period="1y", interval="1d")
        if df is None:
            return {"error": "No data available"}
        df['EMA50'] = df['Close'].rolling(50).mean()
        df['Signal'] = 0
        df.loc[df['Close'] > df['EMA50'], 'Signal'] = 1
        df.loc[df['Close'] < df['EMA50'], 'Signal'] = -1
        df['Return'] = df['Close'].pct_change() * df['Signal'].shift(1)
        total_return = (df['Return'] + 1).prod() - 1
        win_rate = (df['Return'] > 0).sum() / df['Return'].count() * 100
        trades = int(df['Signal'].diff().abs().sum())
        return {"symbol": symbol, "start": start, "end": end, "total_return": round(total_return*100,2),
                "win_rate": round(win_rate,2), "trades": trades}
    except Exception as e:
        return {"error": str(e)}

# ---------- EA Converter ----------
def generate_ea_code(symbol, direction, entry, sl, tp, volume):
    code = f"""
//+------------------------------------------------------------------+
//| LEVIATHAN EA – Generated by LEVIATHAN 21.0                       |
//+------------------------------------------------------------------+
input double LotSize = {volume};
input int MagicNumber = 123456;
input int Slippage = 20;
input double StopLoss = {sl};
input double TakeProfit = {tp};

int OnInit() {{
   return(INIT_SUCCEEDED);
}}

void OnTick() {{
   if (CheckSignal()) {{
      ExecuteOrder("{direction}");
   }}
}}

bool CheckSignal() {{
   // Your custom signal logic
   return true;
}}

void ExecuteOrder(string direction) {{
   MqlTradeRequest request = {{0}};
   MqlTradeResult result = {{0}};
   request.action = TRADE_ACTION_DEAL;
   request.symbol = "{symbol}";
   request.volume = LotSize;
   request.type = (direction == "BUY") ? ORDER_TYPE_BUY : ORDER_TYPE_SELL;
   request.price = (direction == "BUY") ? SymbolInfoDouble(_Symbol, SYMBOL_ASK) : SymbolInfoDouble(_Symbol, SYMBOL_BID);
   request.sl = (direction == "BUY") ? request.price - StopLoss : request.price + StopLoss;
   request.tp = (direction == "BUY") ? request.price + TakeProfit : request.price - TakeProfit;
   request.deviation = Slippage;
   request.magic = MagicNumber;
   OrderSend(request, result);
}}
"""
    return code

@router.post("/ea/convert")
async def convert_to_ea(request: Request):
    data = await request.json()
    symbol = data.get("symbol", "EURUSD=X")
    direction = data.get("direction", "BUY")
    entry = data.get("entry", 0)
    sl = data.get("sl", 0)
    tp = data.get("tp", 0)
    volume = data.get("volume", 0.01)
    ea_code = generate_ea_code(symbol, direction, entry, sl, tp, volume)
    return {"ea_code": ea_code}

# ---------- Plugin Generator ----------
@router.post("/plugin/generate")
async def generate_plugin(request: Request):
    data = await request.json()
    description = data.get("description", "")
    if not description:
        raise HTTPException(status_code=400, detail="Description required")
    if gemini_model:
        try:
            prompt = f"""
You are LEVIATHAN's plugin generator. Write a Python plugin that implements:
{description}

The plugin must have function register_plugin() returning dict with:
- name, version, description, author, type ("strategy"|"indicator"|"execution"|"risk"|"utility")
- init: callable receiving engine, event_bus
- get_signal: optional callable receiving features returning vote (if strategy/indicator)
- on_tick: optional
- on_trade: optional

Provide ONLY the Python code, no explanations.
"""
            response = gemini_model.generate_content(prompt)
            code = response.text
        except:
            code = generate_plugin_template(description)
    else:
        code = generate_plugin_template(description)
    # Save to plugins/
    plugin_dir = Path("plugins")
    plugin_dir.mkdir(exist_ok=True)
    safe_name = re.sub(r'[^a-zA-Z0-9_]', '_', description[:30])
    filename = plugin_dir / f"{safe_name}.py"
    with open(filename, "w") as f:
        f.write(code)
    # Reload plugins
    engine = get_engine()
    pm = engine.get_plugin_manager()
    pm.discover_plugins()
    return {"status": "generated", "file": str(filename), "code": code}

def generate_plugin_template(description: str) -> str:
    safe_name = description[:30].replace(" ", "_")
    return f'''
# leviathan/plugins/{safe_name}.py
def register_plugin():
    return {{
        "name": "{safe_name}",
        "version": "1.0",
        "description": "{description}",
        "author": "LEVIATHAN Auto-Generator",
        "type": "utility",
        "init": init_plugin,
    }}

def init_plugin(engine, event_bus):
    print(f"Plugin {safe_name} loaded.")
    return True
'''

# ---------- Plugin Management ----------
@router.get("/plugins")
async def list_plugins():
    engine = get_engine()
    pm = engine.get_plugin_manager()
    return {"plugins": pm.list_plugins()}

@router.post("/plugins/enable")
async def enable_plugin(request: Request):
    engine = get_engine()
    data = await request.json()
    name = data.get("name")
    if not name:
        raise HTTPException(status_code=400, detail="Missing plugin name")
    pm = engine.get_plugin_manager()
    pm.enable_plugin(name)
    return {"status": "enabled", "plugin": name}

@router.post("/plugins/disable")
async def disable_plugin(request: Request):
    engine = get_engine()
    data = await request.json()
    name = data.get("name")
    if not name:
        raise HTTPException(status_code=400, detail="Missing plugin name")
    pm = engine.get_plugin_manager()
    pm.disable_plugin(name)
    return {"status": "disabled", "plugin": name}

# ---------- Feature Requests ----------
@router.get("/feature_requests")
async def get_feature_requests(status: Optional[str] = None):
    engine = get_engine()
    fm = engine.get_feature_request_manager()
    return {"requests": fm.list_requests(status)}

@router.post("/feature_requests")
async def add_feature_request(request: Request):
    engine = get_engine()
    data = await request.json()
    description = data.get("description")
    if not description:
        raise HTTPException(status_code=400, detail="Missing description")
    fm = engine.get_feature_request_manager()
    req = fm.add_request(description)
    return req

@router.patch("/feature_requests/{request_id}")
async def update_feature_request(request_id: str, request: Request):
    engine = get_engine()
    data = await request.json()
    status = data.get("status")
    if not status:
        raise HTTPException(status_code=400, detail="Missing status")
    fm = engine.get_feature_request_manager()
    success = fm.update_status(request_id, status)
    if not success:
        raise HTTPException(status_code=404, detail="Request not found")
    return {"status": "updated"}

# ---------- UI Configuration ----------
UI_CONFIG_FILE = "ui_config.json"

@router.get("/ui/config")
async def get_ui_config():
    if os.path.exists(UI_CONFIG_FILE):
        with open(UI_CONFIG_FILE, "r") as f:
            return json.load(f)
    return {"theme": "dark", "accent": "blue",
            "tab_order": ["dashboard","signals","scanner","trading","journal","backtest","settings","ai"],
            "hidden_tabs": []}

@router.post("/ui/config")
async def set_ui_config(request: Request):
    data = await request.json()
    with open(UI_CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=2)
    engine = get_engine()
    await engine.event_bus.publish(Event(type="ui_update", data=data))
    return {"status": "updated"}

# ---------- Auto-Updater ----------
@router.get("/update/check")
async def check_for_updates():
    engine = get_engine()
    updater = engine.get_auto_updater()
    has_update = updater.check_for_updates()
    return {"has_update": has_update}

@router.post("/update/pull")
async def pull_update():
    engine = get_engine()
    updater = engine.get_auto_updater()
    success = updater.pull_updates()
    if success:
        return {"status": "pulled", "message": "Update pulled. Restarting..."}
    else:
        return {"status": "failed", "message": "Pull failed"}

@router.post("/update/restart")
async def restart_server():
    engine = get_engine()
    engine.get_auto_updater().restart_server()
    return {"status": "restarting"}
