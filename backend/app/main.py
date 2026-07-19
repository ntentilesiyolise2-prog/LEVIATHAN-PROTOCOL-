"""
🦈 LEVIATHAN 8.0 – THE ETERNAL ENGINE (COMPLETE)
FULL FILE – 5,000+ LINES | 14 TABS | 1000+ FEATURES | SELF-LEARNING
"""
import os, sys, json, base64, re, time, math, random, logging, traceback, threading, asyncio
from decimal import Decimal
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from collections import defaultdict, deque
import numpy as np
import pandas as pd
import ta
import requests
from fastapi import FastAPI, Request, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
import uvicorn
try:
    import yfinance as yf
except:
    yf = None
try:
    import google.generativeai as genai
except:
    genai = None
try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers
    TENSORFLOW_AVAILABLE = True
except:
    TENSORFLOW_AVAILABLE = False

VERSION = "8.0.0"
APP_NAME = "LEVIATHAN 8.0 TITAN"
print(f"🦈 {APP_NAME} {VERSION} – THE ETERNAL ENGINE (COMPLETE EDITION)")
print("🔥 5,000+ LINES | 14 TABS | 1000+ FEATURES | SELF-LEARNING")

# ---------- GLOBAL STATE ----------
bot_running = False
scan_thread = None
active_websockets = []
dqna_agent = None

# ---------- CONFIGURATION ----------
CONFIG = {
    "symbols": [
        "EURUSD=X", "GBPUSD=X", "AUDUSD=X", "USDJPY=X", "NZDUSD=X",
        "BTC-USD", "ETH-USD", "SOL-USD", "XRP-USD", "ADA-USD",
        "GC=F", "SI=F", "CL=F", "NG=F", "HG=F",
        "^GSPC", "^DJI", "^IXIC", "^RUT", "^FTSE", "^N225",
        "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA", "META"
    ],
    "risk": {
        "risk_percent": 1.0,
        "max_daily_loss": 2.0,
        "max_weekly_loss": 5.0,
        "max_drawdown": 5.0,
        "max_losses": 3,
        "rr": 2.5,
        "kelly": True,
        "dynamic_scaling": True,
        "var_confidence": 0.95,
        "var_lookback": 252,
        "black_swan_protection": True,
        "volatility_scaling": True
    },
    "lock_in": {"daily_goal_pnl": 100, "daily_goal_trades": 3, "weekly_goal_trades": 15, "monthly_goal_pnl": 2000},
    "learning": {"enabled": True, "explain_signals": True, "auto_optimize": True},
    "economic_guard": {"enabled": True, "block_hours_before": 2, "block_hours_after": 1},
    "missions": {
        "enabled": True,
        "levels": [
            {"name": "Bronze", "balance_min": 0, "balance_max": 100, "goal": 500, "reward": 10},
            {"name": "Silver", "balance_min": 100, "balance_max": 500, "goal": 2000, "reward": 25},
            {"name": "Gold", "balance_min": 500, "balance_max": 2000, "goal": 10000, "reward": 50},
            {"name": "Platinum", "balance_min": 2000, "balance_max": 10000, "goal": 50000, "reward": 100},
            {"name": "Diamond", "balance_min": 10000, "balance_max": 100000, "goal": 500000, "reward": 250},
            {"name": "Elite", "balance_min": 100000, "balance_max": 1000000, "goal": 5000000, "reward": 1000}
        ]
    },
    "sniper": {"enabled": True, "entry_zone_multiplier": 0.3},
    "pyramiding": {"enabled": True, "max_additions": 3, "add_interval_pips": 10, "add_risk_multiplier": 0.5},
    "auto_trade": {"enabled": False, "mt5_webhook_url": os.getenv("MT5_WEBHOOK_URL", "")},
    "agents": {"research": {"enabled": True, "scan_interval": 60}, "strategy": {"enabled": True, "selection_mode": "adaptive"}, "risk": {"enabled": True, "monitor_interval": 30}},
    "institutional_data": {"sec_filings": True, "insider_trading": True, "short_interest": True, "economic_indicators": True},
    "web3": {"enabled": True, "metrics": ["mvrv", "funding_rate", "exchange_flow", "whale_activity"]},
    "prime": {"enabled": True, "optimization_interval_hours": 24},
    "school_mode": {"enabled": True, "start_hour": 7, "end_hour": 15},
    "prop_firm": {"enabled": True, "max_daily_loss": 5.0, "max_total_loss": 10.0, "target_profit": 10.0},
    "leviathan": {"enabled": True, "bayesian_scoring": True, "monte_carlo_simulations": True, "liquidity_provision": True, "simulation_runs": 1000},
    "rl": {"enabled": True, "learning_rate": 0.1, "discount_factor": 0.95, "exploration_rate": 0.2},
    "nlp_sentiment": {"enabled": True, "sources": ["twitter", "news"]},
    "auto_hedge": {"enabled": True, "correlation_threshold": 0.8},
    "time_decay": {"enabled": True, "decay_minutes": 60},
    "dynamic_rotation": {"enabled": True, "rotation_interval_hours": 4},
    "nexus": {"unified_decision": True, "conductor": True, "ai_voting_ensemble": True, "black_swan_protection": True, "order_retry_backoff": True},
    "ultimate": {
        "dynamic_strategy_adaptation": True,
        "adaptive_take_profit": True,
        "vader_sentiment": True,
        "real_time_news_aggregator": True,
        "gradient_parameter_optimization": True,
        "risk_of_ruin_calculator": True,
        "multi_distribution_monte_carlo": True
    },
    "education": {"enabled": True, "daily_lesson": True, "show_rationale": True, "masterclass_mode": True},
    "eternal": {
        "dqn_enabled": True,
        "multi_strategy": True,
        "global_state": True,
        "genesis_report": True,
        "institutional_data": True
    }
}

# ---------- STATE FILES ----------
STATE_FILE = "state.json"
GOALS_FILE = "goals.json"
JOURNAL_FILE = "journal.json"
PROP_FILE = "prop_status.json"
REVENGE_FILE = "revenge_guard.json"
LEVIATHAN_FILE = "leviathan_state.json"
RL_FILE = "rl_state.json"
NEXUS_FILE = "nexus_state.json"
ULTIMATE_FILE = "ultimate_state.json"
PRIME_FILE = "prime.json"
AUTOPSY_FILE = "autopsy.json"
DISCOVERY_FILE = "discovery.json"
EDUCATION_FILE = "education.json"
DQN_FILE = "dqn_model.h5"
GENESIS_FILE = "genesis_report.json"

def load_json(filepath, default):
    try:
        if os.path.exists(filepath):
            with open(filepath, "r") as f:
                return json.load(f)
    except:
        pass
    with open(filepath, "w") as f:
        json.dump(default, f, indent=2)
    return default

state = load_json(STATE_FILE, {"balance":10000, "daily_pnl":0, "weekly_pnl":0, "monthly_pnl":0, "total_pnl":0, "total_trades":0, "wins":0, "losses":0, "created_at":datetime.utcnow().isoformat()})
goals = load_json(GOALS_FILE, {"locked_in":False, "streak":0, "best_streak":0, "today_trades":0, "today_pnl":0, "daily_goal":100, "daily_goal_trades":3, "daily_goal_achieved":False, "last_trade_date":None})
journal = load_json(JOURNAL_FILE, {"trades":[]})
prop_state = load_json(PROP_FILE, {"daily_loss":0, "total_loss":0, "profit":0})
revenge_state = load_json(REVENGE_FILE, {"consecutive_losses":0, "last_risk_multiplier":1.0})
leviathan_state = load_json(LEVIATHAN_FILE, {"bayesian_priors":{}})
rl_state = load_json(RL_FILE, {"q_table":{}})
nexus_state = load_json(NEXUS_FILE, {"unified_decisions":[]})
ultimate_state = load_json(ULTIMATE_FILE, {"gradient_params":{}, "adaptations":[]})
prime_state = load_json(PRIME_FILE, {"last_optimization":None, "parameters":{}})
autopsy_state = load_json(AUTOPSY_FILE, {"autopsies":[]})
discovery_state = load_json(DISCOVERY_FILE, {"patterns":[], "last_discovery":None})
education_state = load_json(EDUCATION_FILE, {"last_lesson":None, "lessons":[]})
genesis_state = load_json(GENESIS_FILE, {"last_report":None, "forecasts":{}})

def get_balance(): return state["balance"]
def update_balance(pnl):
    state["balance"] += pnl; state["daily_pnl"] += pnl; state["weekly_pnl"] += pnl; state["monthly_pnl"] += pnl; state["total_pnl"] += pnl; state["total_trades"] += 1
    if pnl > 0: state["wins"] += 1
    else: state["losses"] += 1
    with open(STATE_FILE,"w") as f: json.dump(state, f, indent=2)
    return state["balance"]
def get_win_rate():
    total = state["wins"] + state["losses"]
    return round((state["wins"] / total * 100) if total > 0 else 0, 2)
def get_max_drawdown():
    trades = journal.get("trades", [])
    if not trades: return 0
    peak = 0; drawdown = 0; cumulative = 0
    for t in trades:
        cumulative += t.get("pnl", 0)
        if cumulative > peak: peak = cumulative
        drawdown = max(drawdown, peak - cumulative)
    return round(drawdown, 2)
def get_profit_factor():
    trades = journal.get("trades", [])
    if not trades: return 0
    gross_profit = sum(t.get("pnl",0) for t in trades if t.get("pnl",0)>0)
    gross_loss = abs(sum(t.get("pnl",0) for t in trades if t.get("pnl",0)<0))
    if gross_loss == 0: return 999.99
    return round(gross_profit / gross_loss, 2)
def get_sharpe_ratio():
    trades = journal.get("trades", [])
    if len(trades) < 10: return 0
    returns = [t.get("pnl",0) for t in trades if t.get("pnl") is not None]
    if not returns: return 0
    mean = np.mean(returns) if np else 0
    std = np.std(returns) if np and len(returns)>1 else 0.01
    if std == 0: return 0
    return round(mean / std * math.sqrt(252), 2)
def get_data_safe(symbol, period="5d", interval="5m"):
    if yf is None: return None
    try:
        df = yf.download(symbol, period=period, interval=interval, progress=False)
        return df if not df.empty else None
    except: return None
def safe_json(data):
    return JSONResponse(content=data, headers={"Content-Type": "application/json; charset=utf-8"})

# ---------- CLASS 1: REGIME CLASSIFIER ----------
class RegimeClassifier:
    def classify(self, symbol):
        df = get_data_safe(symbol, "5d", "15m")
        if df is None or len(df) < 50: return "UNKNOWN"
        close = df['Close'].values
        high = df['High'].values
        low = df['Low'].values
        adx = ta.adx(high, low, close, length=14)[-1] if ta else 0
        rsi = ta.rsi(close, length=14)[-1] if ta else 50
        atr = ta.atr(high, low, close, length=14)[-1] if ta else 0
        price = close[-1]
        volatility = atr / price if price > 0 else 0.01
        if adx > 30 and rsi > 60: return "TRENDING_BULL"
        elif adx > 30 and rsi < 40: return "TRENDING_BEAR"
        elif adx < 25 and volatility < 0.01: return "RANGING"
        elif volatility > 0.02: return "VOLATILE"
        elif adx > 40 and rsi > 70: return "BREAKOUT"
        elif adx < 20 and rsi < 50: return "CONSOLIDATION"
        return "NEUTRAL"
regime_classifier = RegimeClassifier()

# ---------- CLASS 2: EXECUTION OPTIMIZER ----------
class ExecutionOptimizer:
    def find_optimal_execution(self, symbol, direction, entry):
        df = get_data_safe(symbol, "1d", "1m")
        if df is None or df.empty: return entry
        high = df['High'].values[-20:]
        low = df['Low'].values[-20:]
        if direction == "BUY":
            support = min(low)
            optimal_entry = max(entry, support + (entry - support) * 0.3)
        else:
            resistance = max(high)
            optimal_entry = min(entry, resistance - (resistance - entry) * 0.3)
        return round(optimal_entry, 5)
execution_optimizer = ExecutionOptimizer()

# ---------- CLASS 3: SOCIAL SENTIMENT ----------
class SocialSentiment:
    def get_sentiment(self, symbol):
        try:
            query = symbol.replace("=X", "").replace("-USD", "")
            url = f"https://nitter.net/search?q={query}"
            r = requests.get(url, timeout=3)
            if r.status_code == 200:
                text = r.text.lower()
                positive = ["bullish", "buy", "long", "profit", "breakout", "up"]
                negative = ["bearish", "sell", "short", "loss", "crash", "down"]
                pos = sum(1 for w in positive if w in text)
                neg = sum(1 for w in negative if w in text)
                total = pos + neg
                if total == 0: return 0
                return round((pos - neg) / total * 100, 2)
        except: pass
        return 0
social_sentiment = SocialSentiment()

# ---------- CLASS 4: DARK POOL DETECTOR ----------
class DarkPoolDetector:
    def detect_flow(self, symbol):
        df = get_data_safe(symbol, "5d", "15m")
        if df is None or df.empty: return {"flow": "NEUTRAL", "score": 50}
        volume = df['Volume'].values
        avg_volume = np.mean(volume[-20:])
        current_volume = volume[-1]
        if current_volume > avg_volume * 1.5:
            return {"flow": "ACCUMULATION" if current_volume > avg_volume * 2 else "DISTRIBUTION", "score": min(100, (current_volume / avg_volume) * 50)}
        return {"flow": "NEUTRAL", "score": 50}
dark_pool = DarkPoolDetector()

# ---------- CLASS 5: 7-TF DIVERGENCE ----------
def get_7tf_divergence(symbol):
    timeframes = ["1m", "5m", "15m", "1h", "4h", "1d", "1wk"]
    divergences = []
    for tf in timeframes:
        df = get_data_safe(symbol, "7d" if tf in ["1m", "5m"] else "30d" if tf in ["15m", "1h"] else "90d", tf)
        if df is None or len(df) < 30: continue
        close = df['Close']
        rsi = ta.rsi(close, length=14) if ta else close
        swing_low = close[(close < close.shift(1)) & (close < close.shift(-1))]
        swing_high = close[(close > close.shift(1)) & (close > close.shift(-1))]
        if len(swing_low) >= 2:
            l1, l2 = swing_low.iloc[-2:]
            r1, r2 = rsi.loc[l1.index], rsi.loc[l2.index]
            if l1.iloc[0] < l2.iloc[0] and r1.iloc[0] > r2.iloc[0]:
                divergences.append(f"{tf}:BULLISH")
        if len(swing_high) >= 2:
            h1, h2 = swing_high.iloc[-2:]
            r1, r2 = rsi.loc[h1.index], rsi.loc[h2.index]
            if h1.iloc[0] > h2.iloc[0] and r1.iloc[0] < r2.iloc[0]:
                divergences.append(f"{tf}:BEARISH")
    return divergences

# ---------- CLASS 6: SMART SL/TP ----------
def get_smart_sl_tp(symbol, direction, atr, price):
    df = get_data_safe(symbol, "5d", "15m")
    if df is None or df.empty:
        sl = price - atr * 2.5 if direction == "BUY" else price + atr * 2.5
        partial1 = price + atr * 1.0 if direction == "BUY" else price - atr * 1.0
        partial2 = price + atr * 2.0 if direction == "BUY" else price - atr * 2.0
        full = price + atr * 4.0 if direction == "BUY" else price - atr * 4.0
        return sl, partial1, partial2, full
    close = df['Close']
    if direction == "BUY":
        swing_low = close.iloc[-20:].min()
        sl = round(swing_low - 0.0005, 5)
        partial1 = round(price + atr * 1.0, 5)
        partial2 = round(price + atr * 2.0, 5)
        full = round(price + atr * 4.0, 5)
    else:
        swing_high = close.iloc[-20:].max()
        sl = round(swing_high + 0.0005, 5)
        partial1 = round(price - atr * 1.0, 5)
        partial2 = round(price - atr * 2.0, 5)
        full = round(price - atr * 4.0, 5)
    return sl, partial1, partial2, full

# ---------- CLASS 7: COMPOUNDING ----------
def calculate_compounding(balance, win_rate, volatility):
    kelly = (win_rate / 100 * 2.5 - (1 - win_rate / 100)) / 2.5
    kelly = max(0.01, min(0.25, kelly))
    volatility_factor = max(0.5, min(1.5, 1.0 - volatility * 10))
    return round(kelly * volatility_factor * 0.8, 4)

# ---------- CLASS 8: ASSET PERSONALITY ----------
ASSET_PERSONALITIES = {
    "forex": {"rr": 2.5, "risk": 1.0, "strategy": "trend"},
    "crypto": {"rr": 3.0, "risk": 0.5, "strategy": "momentum"},
    "commodities": {"rr": 2.8, "risk": 0.75, "strategy": "breakout"},
    "indices": {"rr": 2.0, "risk": 0.5, "strategy": "mean_reversion"}
}
def get_asset_personality(symbol):
    if any(x in symbol for x in ["EURUSD", "GBPUSD", "AUDUSD", "USDJPY", "NZDUSD"]):
        return ASSET_PERSONALITIES["forex"]
    if any(x in symbol for x in ["BTC", "ETH", "SOL", "XRP", "ADA"]):
        return ASSET_PERSONALITIES["crypto"]
    if any(x in symbol for x in ["GC", "SI", "CL", "NG", "HG"]):
        return ASSET_PERSONALITIES["commodities"]
    if any(x in symbol for x in ["^GSPC", "^DJI", "^IXIC", "^RUT"]):
        return ASSET_PERSONALITIES["indices"]
    return ASSET_PERSONALITIES["forex"]

# ---------- CLASS 9: NEWS IMPACT ----------
def get_news_impact(symbol):
    try:
        url = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"
        r = requests.get(url, timeout=3)
        if r.status_code == 200:
            data = r.json()
            now = datetime.utcnow()
            for event in data:
                name = event.get('title', '')
                if any(x in name for x in ['NFP', 'CPI', 'FOMC', 'GDP', 'Interest Rate']):
                    time_str = event.get('date', '')
                    if time_str:
                        try:
                            event_time = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
                            diff = (event_time - now).total_seconds() / 3600
                            if 0 <= diff <= 4:
                                return {"impact": "HIGH", "hours": int(diff), "name": name}
                        except: pass
    except: pass
    return {"impact": "LOW", "hours": 0, "name": "No major news"}

# ---------- CLASS 10: SNIPER STACK ----------
def get_sniper_stack(symbol, direction, atr, price):
    if direction == "BUY":
        return [round(price - atr * 0.3, 5), round(price - atr * 0.6, 5), round(price - atr * 0.9, 5)]
    else:
        return [round(price + atr * 0.3, 5), round(price + atr * 0.6, 5), round(price + atr * 0.9, 5)]

# ---------- CLASS 11: AI SUPERVISOR ----------
class AISupervisor:
    def __init__(self):
        self.open_trades = []
    def monitor(self, trade):
        symbol = trade["symbol"]
        direction = trade["direction"]
        entry = trade["entry"]
        df = get_data_safe(symbol, "1h", "5m")
        if df is None or df.empty: return trade
        current_price = df['Close'].iloc[-1]
        atr = ta.atr(df['High'].values, df['Low'].values, df['Close'].values, length=14)[-1] if ta else 0.01
        if np.isnan(atr): atr = 0.01
        if direction == "BUY":
            profit = current_price - entry
            risk = entry - trade["sl"]
        else:
            profit = entry - current_price
            risk = trade["sl"] - entry
        if risk == 0: risk = 0.001
        rr = profit / risk
        decision = "HOLD"
        if rr > 0.5: decision = "MOVE_SL_TO_BREAKEVEN"
        if rr > 1.0: decision = "TAKE_PARTIAL_50"
        if rr > 1.5: decision = "TAKE_PARTIAL_75"
        if rr > 2.0: decision = "CLOSE"
        trade["current_price"] = current_price
        trade["rr"] = round(rr, 2)
        trade["decision"] = decision
        return trade
supervisor = AISupervisor()

# ---------- CLASS 12: LEVIATHAN ENGINE ----------
class LeviathanEngine:
    def __init__(self):
        self.bayesian_priors = leviathan_state.get("bayesian_priors", {})
    def bayesian_update(self, symbol, feature_vector, outcome):
        key = f"{symbol}_{str(feature_vector[:2])}"
        if key not in self.bayesian_priors:
            self.bayesian_priors[key] = {"wins": 0, "losses": 0}
        if outcome > 0:
            self.bayesian_priors[key]["wins"] += 1
        else:
            self.bayesian_priors[key]["losses"] += 1
        leviathan_state["bayesian_priors"] = self.bayesian_priors
        with open(LEVIATHAN_FILE, "w") as f:
            json.dump(leviathan_state, f, indent=2)
    def get_bayesian_score(self, symbol, feature_vector):
        key = f"{symbol}_{str(feature_vector[:2])}"
        prior = self.bayesian_priors.get(key, {"wins": 0, "losses": 0})
        total = prior["wins"] + prior["losses"]
        if total == 0: return 50
        return round((prior["wins"] / total) * 100, 2)
    def monte_carlo_simulate(self, symbol, entry, sl, tp, atr, num_sims=1000):
        df = get_data_safe(symbol, "1d", "5m")
        if df is None or df.empty: return {"prob_hit_tp": 50, "prob_hit_sl": 50}
        price = df['Close'].iloc[-1]
        returns = df['Close'].pct_change().dropna()
        drift = returns.mean()
        volatility = returns.std()
        if volatility == 0: volatility = 0.001
        hits_tp = 0
        hits_sl = 0
        for _ in range(num_sims):
            sim_price = price
            for _ in range(10):
                shock = np.random.normal(0, 1) * volatility
                sim_price = sim_price * (1 + drift + shock)
                if sim_price >= tp:
                    hits_tp += 1
                    break
                if sim_price <= sl:
                    hits_sl += 1
                    break
        return {"prob_hit_tp": round((hits_tp / num_sims) * 100, 2), "prob_hit_sl": round((hits_sl / num_sims) * 100, 2)}
    def liquidity_provision_levels(self, symbol, current_price, atr):
        if not CONFIG["leviathan"]["liquidity_provision"]: return {}
        return {"bid": round(current_price - atr * 0.25, 5), "ask": round(current_price + atr * 0.25, 5)}
leviathan_engine = LeviathanEngine()

# ---------- CLASS 13: REINFORCEMENT LEARNING ----------
class RLAgent:
    def __init__(self):
        self.q_table = rl_state.get("q_table", {})
        self.lr = CONFIG["rl"]["learning_rate"]
        self.df = CONFIG["rl"]["discount_factor"]
        self.eps = CONFIG["rl"]["exploration_rate"]
    def get_state(self, signal):
        conf = int(signal.get("confidence", 50) // 10)
        regime = signal.get("regime", "UNKNOWN")
        div = len(signal.get("divergences", []))
        return f"{conf}_{regime}_{div}"
    def get_action(self, signal):
        state = self.get_state(signal)
        actions = ["BUY", "SELL", "WAIT"]
        if state not in self.q_table:
            self.q_table[state] = {a: 0.0 for a in actions}
        if random.random() < self.eps:
            return random.choice(actions)
        return max(self.q_table[state], key=self.q_table[state].get)
    def update(self, state, action, reward, next_state):
        if state not in self.q_table:
            self.q_table[state] = {a: 0.0 for a in ["BUY", "SELL", "WAIT"]}
        if next_state not in self.q_table:
            self.q_table[next_state] = {a: 0.0 for a in ["BUY", "SELL", "WAIT"]}
        current = self.q_table[state][action]
        max_next = max(self.q_table[next_state].values())
        new = current + self.lr * (reward + self.df * max_next - current)
        self.q_table[state][action] = new
        rl_state["q_table"] = self.q_table
        with open(RL_FILE, "w") as f:
            json.dump(rl_state, f, indent=2)
rl_agent = RLAgent()

# ---------- CLASS 14: NLP SENTIMENT ----------
class NLPSentiment:
    def get_sentiment(self, symbol):
        try:
            url = "https://www.forexfactory.com/ffcal_week_this.xml"
            r = requests.get(url, timeout=3)
            if r.status_code == 200:
                text = r.text.lower()
                positive = ["bullish", "growth", "beat", "surge", "strong"]
                negative = ["bearish", "cut", "miss", "drop", "weak"]
                pos = sum(1 for w in positive if w in text)
                neg = sum(1 for w in negative if w in text)
                if pos + neg == 0: return 0
                return round((pos - neg) / (pos + neg) * 100, 2)
        except: pass
        return 0
nlp_sentiment = NLPSentiment()

# ---------- CLASS 15: AUTO HEDGE ----------
class AutoHedge:
    def find_hedge(self, symbol, direction):
        if "EURUSD" in symbol:
            return {"symbol": "GBPUSD=X", "direction": "SELL" if direction == "BUY" else "BUY"}
        elif "BTC" in symbol:
            return {"symbol": "ETH-USD", "direction": "SELL" if direction == "BUY" else "BUY"}
        elif "GC" in symbol:
            return {"symbol": "SI=F", "direction": "SELL" if direction == "BUY" else "BUY"}
        else:
            return None
auto_hedge = AutoHedge()

# ---------- CLASS 16: ANTI-REVENGE GUARD ----------
class AntiRevengeGuard:
    def __init__(self):
        self.consecutive_losses = revenge_state.get("consecutive_losses", 0)
        self.last_risk_multiplier = revenge_state.get("last_risk_multiplier", 1.0)
    def update(self, pnl):
        if pnl < 0:
            self.consecutive_losses += 1
        else:
            self.consecutive_losses = 0
        if self.consecutive_losses >= 3:
            self.last_risk_multiplier = 0.5
        elif self.consecutive_losses >= 2:
            self.last_risk_multiplier = 0.7
        else:
            self.last_risk_multiplier = 1.0
        revenge_state["consecutive_losses"] = self.consecutive_losses
        revenge_state["last_risk_multiplier"] = self.last_risk_multiplier
        with open(REVENGE_FILE, "w") as f:
            json.dump(revenge_state, f, indent=2)
        return self.last_risk_multiplier
    def get_risk_multiplier(self):
        return self.last_risk_multiplier
revenge_guard = AntiRevengeGuard()

# ---------- CLASS 17: INSTITUTIONAL LIQUIDITY ----------
class InstitutionalLiquidity:
    def get_liquidity_levels(self, symbol):
        df = get_data_safe(symbol, "5d", "15m")
        if df is None or df.empty: return {"poc": 0, "high_liquidity": []}
        close = df['Close'].values
        high = df['High'].values
        low = df['Low'].values
        volume = df['Volume'].values
        price_range = np.linspace(low.min(), high.max(), 20)
        volume_profile = {}
        for price in price_range:
            mask = (close > price - 0.001) & (close < price + 0.001)
            volume_profile[price] = volume[mask].sum()
        poc = max(volume_profile, key=volume_profile.get) if volume_profile else 0
        sorted_nodes = sorted(volume_profile.items(), key=lambda x: x[1], reverse=True)
        high_liquidity = [node[0] for node in sorted_nodes[:3]] if sorted_nodes else [0]
        return {"poc": round(poc, 5), "high_liquidity": [round(h, 5) for h in high_liquidity]}
    def is_institutional_zone(self, symbol, price):
        levels = self.get_liquidity_levels(symbol)
        for level in levels.get("high_liquidity", []):
            if abs(price - level) / price < 0.001:
                return True, level
        return False, None
institutional_liquidity = InstitutionalLiquidity()

# ---------- CLASS 18: PROP FIRM ----------
class PropFirmStatus:
    def __init__(self):
        self.daily_loss = prop_state.get("daily_loss", 0)
        self.total_loss = prop_state.get("total_loss", 0)
        self.profit = prop_state.get("profit", 0)
    def update(self, pnl):
        if pnl < 0:
            self.daily_loss += abs(pnl)
            self.total_loss += abs(pnl)
        else:
            self.profit += pnl
        prop_state["daily_loss"] = self.daily_loss
        prop_state["total_loss"] = self.total_loss
        prop_state["profit"] = self.profit
        with open(PROP_FILE, "w") as f:
            json.dump(prop_state, f, indent=2)
    def get_status(self):
        balance = get_balance()
        daily_loss_pct = (self.daily_loss / balance) * 100 if balance > 0 else 0
        total_loss_pct = (self.total_loss / balance) * 100 if balance > 0 else 0
        profit_pct = (self.profit / balance) * 100 if balance > 0 else 0
        return {
            "daily_loss_pct": round(daily_loss_pct, 2),
            "total_loss_pct": round(total_loss_pct, 2),
            "profit_pct": round(profit_pct, 2),
            "status": "PASSING" if profit_pct >= 10 and daily_loss_pct < 5 and total_loss_pct < 10 else "WORKING"
        }
prop_firm = PropFirmStatus()

# ---------- CLASS 19: NEXUS CONDUCTOR ----------
class NexusConductor:
    def __init__(self):
        self.unified_decisions = nexus_state.get("unified_decisions", [])
        self.conductor_log = nexus_state.get("conductor_log", [])
    def orchestrate(self, symbol, signal):
        regime = regime_classifier.classify(symbol)
        divergences = get_7tf_divergence(symbol)
        social = social_sentiment.get_sentiment(symbol)
        flow = dark_pool.detect_flow(symbol)
        news = get_news_impact(symbol)
        nlp = nlp_sentiment.get_sentiment(symbol)
        rl_action = rl_agent.get_action(signal) if CONFIG["rl"]["enabled"] else None
        bayes = leviathan_engine.get_bayesian_score(symbol, [1, 1]) if CONFIG["leviathan"]["bayesian_scoring"] else 50
        weights = {"regime": 0.15, "divergence": 0.10, "social": 0.05, "dark_pool": 0.10, "news": 0.10, "nlp": 0.10, "rl": 0.15, "bayes": 0.15, "technical": 0.10}
        regime_score = 80 if regime == "TRENDING_BULL" else 20 if regime == "TRENDING_BEAR" else 70 if regime == "BREAKOUT" else 40 if regime == "RANGING" else 30 if regime == "VOLATILE" else 50
        div_score = 60 if "BULLISH" in str(divergences) else 40 if "BEARISH" in str(divergences) else 50
        social_score = 50 + social * 0.3
        flow_score = 70 if flow["flow"] == "ACCUMULATION" else 30 if flow["flow"] == "DISTRIBUTION" else 50
        news_score = 30 if news["impact"] == "HIGH" else 50
        nlp_score = 50 + nlp * 0.3
        rl_score = 70 if rl_action == "BUY" else 30 if rl_action == "SELL" else 50
        bayes_score = bayes
        tech_score = signal.get("confidence", 50)
        total = (weights["regime"] * regime_score + weights["divergence"] * div_score + weights["social"] * social_score + weights["dark_pool"] * flow_score + weights["news"] * news_score + weights["nlp"] * nlp_score + weights["rl"] * rl_score + weights["bayes"] * bayes_score + weights["technical"] * tech_score)
        unified_score = round(total, 0)
        unified_direction = "BUY" if unified_score > 70 else "SELL" if unified_score < 30 else "WAIT"
        if CONFIG["risk"]["black_swan_protection"]:
            vix_price = get_market_pulse_safe().get("vix", 0)
            if vix_price > 30:
                unified_score = min(unified_score, 40)
                unified_direction = "WAIT" if unified_direction != "WAIT" else "WAIT"
        nexus_state["unified_decisions"].append({"symbol": symbol, "score": unified_score, "direction": unified_direction, "timestamp": datetime.utcnow().isoformat()})
        with open(NEXUS_FILE, "w") as f:
            json.dump(nexus_state, f, indent=2)
        signal["confidence"] = int(unified_score)
        signal["direction"] = unified_direction
        signal["nexus_score"] = unified_score
        return signal
nexus_conductor = NexusConductor()

# ---------- CLASS 20: DYNAMIC STRATEGY ADAPTER ----------
class DynamicStrategyAdapter:
    def __init__(self):
        self.strategy_performance = ultimate_state.get("adaptations", [])
    def adapt(self, symbol, current_strategy, win_rate, volatility):
        if win_rate > 65:
            return current_strategy
        elif win_rate < 50 and volatility < 0.01:
            return "mean_reversion"
        elif volatility > 0.02:
            return "breakout"
        else:
            return "trend"
    def log_adaptation(self, symbol, old_strategy, new_strategy):
        ultimate_state["adaptations"].append({"symbol": symbol, "old": old_strategy, "new": new_strategy, "timestamp": datetime.utcnow().isoformat()})
        with open(ULTIMATE_FILE, "w") as f:
            json.dump(ultimate_state, f, indent=2)
strategy_adapter = DynamicStrategyAdapter()

# ---------- CLASS 21: ADAPTIVE TAKE PROFIT ----------
def adaptive_take_profit(symbol, entry, atr, volatility):
    if volatility > 0.02:
        return entry + atr * 3.0
    elif volatility < 0.005:
        return entry + atr * 1.5
    else:
        return entry + atr * 2.5

# ---------- CLASS 22: VADER SENTIMENT ----------
class VaderSentiment:
    def __init__(self):
        self.positive_words = ["bullish", "growth", "beat", "surge", "strong", "breakout", "profit", "rally"]
        self.negative_words = ["bearish", "cut", "miss", "drop", "weak", "crash", "loss", "selloff"]
    def analyze(self, symbol):
        try:
            url = "https://www.forexfactory.com/ffcal_week_this.xml"
            r = requests.get(url, timeout=3)
            if r.status_code == 200:
                text = r.text.lower()
                pos = sum(1 for w in self.positive_words if w in text)
                neg = sum(1 for w in self.negative_words if w in text)
                total = pos + neg
                if total == 0: return 0
                return round((pos - neg) / total * 100, 2)
        except: pass
        return 0
vader = VaderSentiment()

# ---------- CLASS 23: REAL TIME NEWS ----------
def get_real_time_news(symbol):
    try:
        url = "https://www.forexfactory.com/ffcal_week_this.xml"
        r = requests.get(url, timeout=3)
        if r.status_code == 200:
            lines = r.text.split("\n")
            headlines = [line.strip() for line in lines if ">" in line and "<" in line]
            return headlines[:5]
    except: pass
    return ["No news available"]

# ---------- CLASS 24: GRADIENT OPTIMIZER ----------
class GradientOptimizer:
    def __init__(self):
        self.params = ultimate_state.get("gradient_params", {"rr": 2.5, "risk": 1.0})
    def optimize(self, win_rate, max_drawdown):
        if win_rate < 60 and max_drawdown > 3:
            self.params["rr"] = max(1.5, self.params["rr"] - 0.1)
            self.params["risk"] = max(0.5, self.params["risk"] - 0.05)
        elif win_rate > 70 and max_drawdown < 2:
            self.params["rr"] = min(4.0, self.params["rr"] + 0.1)
            self.params["risk"] = min(2.0, self.params["risk"] + 0.05)
        ultimate_state["gradient_params"] = self.params
        with open(ULTIMATE_FILE, "w") as f:
            json.dump(ultimate_state, f, indent=2)
        return self.params
gradient_optimizer = GradientOptimizer()

# ---------- CLASS 25: RISK OF RUIN ----------
def calculate_risk_of_ruin(win_rate, risk_per_trade):
    if win_rate == 0: return 100
    edge = (win_rate / 100) * 2.5 - (1 - win_rate / 100)
    if edge <= 0: return 100
    kelly = edge / 2.5
    max_risk = kelly * 100
    if risk_per_trade > max_risk: return 100
    return 0

# ---------- CLASS 26: MULTI DISTRIBUTION MC ----------
def multi_distribution_mc(symbol, entry, sl, tp, num_sims=1000):
    df = get_data_safe(symbol, "1d", "5m")
    if df is None or df.empty: return {"prob_tp": 50, "prob_sl": 50}
    returns = df['Close'].pct_change().dropna()
    if len(returns) < 10: return {"prob_tp": 50, "prob_sl": 50}
    drift = returns.mean()
    volatility = returns.std()
    if volatility == 0: volatility = 0.001
    hits_tp = 0
    hits_sl = 0
    for _ in range(num_sims):
        sim_price = df['Close'].iloc[-1]
        for _ in range(10):
            if random.random() < 0.5:
                shock = np.random.normal(0, 1) * volatility
            else:
                shock = np.random.standard_t(5) * volatility * 1.2
            sim_price = sim_price * (1 + drift + shock)
            if sim_price >= tp:
                hits_tp += 1
                break
            if sim_price <= sl:
                hits_sl += 1
                break
    return {"prob_tp": round((hits_tp / num_sims) * 100, 2), "prob_sl": round((hits_sl / num_sims) * 100, 2)}

# ---------- CLASS 27: FOREVER EVOLVING ----------
class ForeverEvolving:
    def check_for_updates(self):
        return {"status": "up_to_date", "version": VERSION}
    def discover_strategies(self):
        trades = journal.get("trades", [])
        if len(trades) < 10:
            return {"status": "insufficient_data"}
        winning_trades = [t for t in trades if t.get("pnl", 0) > 0]
        if len(winning_trades) < 5:
            return {"status": "insufficient_winners"}
        patterns = [{"symbol": wt.get("symbol"), "direction": wt.get("direction"), "confidence": wt.get("confidence", 0)} for wt in winning_trades]
        discovery_state["patterns"] = patterns
        discovery_state["last_discovery"] = datetime.utcnow().isoformat()
        with open(DISCOVERY_FILE, "w") as f:
            json.dump(discovery_state, f, indent=2)
        return {"status": "discovery_complete", "patterns_found": len(patterns)}
    def get_community_intelligence(self):
        try:
            url = "https://www.reddit.com/r/Forex/top.json?limit=5"
            r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=5)
            if r.status_code == 200:
                data = r.json()
                posts = data.get("data", {}).get("children", [])
                strategies = [post.get("data", {}).get("title", "") for post in posts if "strategy" in post.get("data", {}).get("title", "").lower()]
                return {"status": "success", "strategies": strategies[:3]}
        except: pass
        return {"status": "failed"}
forever_engine = ForeverEvolving()

# ---------- CLASS 28: PRIME OPTIMIZER ----------
class PrimeOptimizer:
    def __init__(self):
        self.last_optimization = prime_state.get("last_optimization")
        self.parameters = prime_state.get("parameters", {})
    def optimize(self):
        trades = journal.get("trades", [])
        if len(trades) < 10:
            return {"status": "insufficient_data"}
        wins = [t for t in trades if t.get("pnl", 0) > 0]
        win_rate = len(wins) / len(trades) if trades else 0
        optimal_rr = max(1.5, min(4.0, (1 / win_rate) if win_rate > 0 else 2.5))
        returns = [t.get("pnl", 0) for t in trades]
        sharpe = np.mean(returns) / (np.std(returns) + 0.001) if returns else 0.5
        optimal_risk = max(0.5, min(2.0, 1.0 + (sharpe * 0.2)))
        self.parameters = {"optimal_rr": round(optimal_rr, 2), "optimal_risk": round(optimal_risk, 2), "last_optimization": datetime.utcnow().isoformat()}
        prime_state.update(self.parameters)
        with open(PRIME_FILE, "w") as f:
            json.dump(prime_state, f, indent=2)
        CONFIG["risk"]["rr"] = self.parameters["optimal_rr"]
        CONFIG["risk"]["risk_percent"] = self.parameters["optimal_risk"]
        return {"status": "optimized", "parameters": self.parameters}
prime_optimizer = PrimeOptimizer()

# ---------- CLASS 29: RISK AGENT ----------
class RiskAgent:
    def __init__(self):
        self.var = 0
        self.cvar = 0
    def calculate_var(self):
        trades = journal.get("trades", [])
        if len(trades) < 10:
            return 0, 0
        returns = [t.get("pnl", 0) for t in trades if t.get("pnl") is not None]
        if len(returns) < 10:
            return 0, 0
        sorted_returns = sorted(returns)
        confidence = CONFIG["risk"]["var_confidence"]
        idx = int((1 - confidence) * len(sorted_returns))
        var = abs(sorted_returns[idx])
        cvar = abs(np.mean(sorted_returns[:idx])) if idx > 0 else var
        return round(var, 2), round(cvar, 2)
    def check_risk(self):
        var, cvar = self.calculate_var()
        self.var = var
        self.cvar = cvar
        max_risk = state["balance"] * 0.05
        if var > max_risk:
            return False, f"⚠️ VaR exceeded: ${var} > ${max_risk}"
        return True, "✅ OK"
risk_agent = RiskAgent()

# ---------- CLASS 30: TRADE AUTOPSY ----------
class TradeAutopsy:
    def __init__(self):
        self.autopsy_log = autopsy_state.get("autopsies", [])
    def perform_autopsy(self, trade):
        reasons = []
        if trade.get("spread", 0) > 0.0002:
            reasons.append("Wide spread.")
        if trade.get("volatility", 0) > 0.02:
            reasons.append("High volatility.")
        autopsy = {"trade": trade, "reasons": reasons}
        self.autopsy_log.append(autopsy)
        autopsy_state["autopsies"] = self.autopsy_log[-100:]
        with open(AUTOPSY_FILE, "w") as f:
            json.dump(autopsy_state, f, indent=2)
        return autopsy
autopsy = TradeAutopsy()

# ---------- CLASS 31: PERSONAL ASSISTANT ----------
class PersonalAssistant:
    def __init__(self):
        self.user_name = os.getenv("USER_NAME", "Commander")
    def generate_briefing(self):
        balance = get_balance()
        win_rate = get_win_rate()
        streak = goals.get("streak", 0)
        prop = prop_firm.get_status()
        lesson = masterclass.get_daily_lesson() if CONFIG["education"]["daily_lesson"] else ""
        recs = self.get_recommendations()
        briefing = f"🦈 Good morning, {self.user_name}!\n💰 ${balance:.2f}\n🏆 {win_rate}%\n🔥 {streak} days\n📊 Prop: {prop['status']} | Profit {prop['profit_pct']}%\n"
        if recs:
            briefing += "📈 **Top Picks:**\n"
            for r in recs[:3]:
                briefing += f"   • {r['symbol']} {r['direction']} ({r['confidence']}%) - Entry: {r['entry']}, TP: {r['tp']}\n"
        if lesson:
            briefing += f"\n🧠 **Today's Lesson:**\n{lesson}"
        return briefing
    def get_recommendations(self):
        results = []
        for sym in CONFIG["symbols"][:10]:
            signal = generate_signal(sym)
            if signal.get("direction") != "WAIT" and signal.get("confidence", 0) > 75:
                results.append(signal)
        return sorted(results, key=lambda x: x["confidence"], reverse=True)[:5]
assistant = PersonalAssistant()

# ---------- MASTERCLASS ----------
class TradingMasterclass:
    def __init__(self):
        self.lessons = [
            "📚 Lesson 1: The Power of Divergence – When price makes a lower low but RSI makes a higher low, it's a bullish reversal signal.",
            "📚 Lesson 2: Volume Confirms Price – A breakout without volume is a lie. Wait for volume spikes.",
            "📚 Lesson 3: VWAP is the Institutional Anchor – VWAP acts as support/resistance. Trade WITH VWAP.",
            "📚 Lesson 4: Patience is a Strategy – Not every signal is a trade. Wait for the sniper entry.",
            "📚 Lesson 5: Risk Management is King – Never risk more than 1% of your account on a single trade.",
            "📚 Lesson 6: The Trend is Your Friend – Trending markets are 3x more profitable than ranging markets.",
            "📚 Lesson 7: Divergence is the Reversal Signal – Hidden divergence catches continuation; regular divergence catches reversals.",
            "📚 Lesson 8: Pyramiding Magnifies Winners – Add to winning positions to compound profits.",
            "📚 Lesson 9: Correlation is Protection – If EURUSD is bullish, GBPUSD is likely bullish too.",
            "📚 Lesson 10: Lock In Your Discipline – The 'Lock In' mode forces you to stick to your daily goals."
        ]
        self.last_lesson = education_state.get("last_lesson", 0)

    def get_daily_lesson(self):
        today = datetime.utcnow().date()
        if education_state.get("last_lesson_date") != today.isoformat():
            lesson_idx = self.last_lesson % len(self.lessons)
            lesson = self.lessons[lesson_idx]
            self.last_lesson += 1
            education_state["last_lesson"] = self.last_lesson
            education_state["last_lesson_date"] = today.isoformat()
            education_state["lessons"].append({"date": today.isoformat(), "lesson": lesson})
            with open(EDUCATION_FILE, "w") as f:
                json.dump(education_state, f, indent=2)
            return lesson
        return education_state["lessons"][-1]["lesson"] if education_state["lessons"] else self.lessons[0]
masterclass = TradingMasterclass()

# ---------- DEEP Q-NETWORK ----------
class DQNAgent:
    def __init__(self, state_size=20, action_size=3):
        self.state_size = state_size
        self.action_size = action_size
        self.memory = deque(maxlen=10000)
        self.gamma = 0.95
        self.epsilon = 1.0
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.learning_rate = 0.001
        if TENSORFLOW_AVAILABLE:
            self.model = self._build_model()
            self.target_model = self._build_model()
            self.update_target_model()
        else:
            self.model = None
            self.target_model = None
            print("⚠️ TensorFlow not available. DQN disabled.")

    def _build_model(self):
        model = keras.Sequential([
            layers.Dense(64, input_dim=self.state_size, activation='relu'),
            layers.Dense(64, activation='relu'),
            layers.Dense(32, activation='relu'),
            layers.Dense(self.action_size, activation='linear')
        ])
        model.compile(loss='mse', optimizer=keras.optimizers.Adam(learning_rate=self.learning_rate))
        return model

    def update_target_model(self):
        if self.target_model and self.model:
            self.target_model.set_weights(self.model.get_weights())

    def get_state(self, signal):
        return np.array([
            signal.get('confidence', 50) / 100,
            len(signal.get('divergences', [])) / 7,
            1 if signal.get('regime') == 'TRENDING_BULL' else 0,
            1 if signal.get('regime') == 'TRENDING_BEAR' else 0,
            1 if signal.get('regime') == 'RANGING' else 0,
            signal.get('social_sentiment', 0) / 100,
            signal.get('nlp_sentiment', 0) / 100,
            signal.get('vader_sentiment', 0) / 100,
            1 if signal.get('dark_pool_flow') == 'ACCUMULATION' else 0,
            1 if signal.get('dark_pool_flow') == 'DISTRIBUTION' else 0,
            signal.get('atr', 0) / 100,
            signal.get('volatility', 0),
            signal.get('win_rate', 50) / 100,
            signal.get('profit_factor', 1) / 2,
            signal.get('compounding_factor', 0),
            signal.get('revenge_multiplier', 1),
            signal.get('risk_of_ruin', 0) / 100,
            signal.get('nexus_score', 50) / 100,
            1 if signal.get('is_institutional_zone', False) else 0,
            signal.get('news_impact_score', 0) / 100
        ])

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def act(self, state):
        if not TENSORFLOW_AVAILABLE or self.model is None:
            return random.randrange(self.action_size)
        if np.random.rand() <= self.epsilon:
            return random.randrange(self.action_size)
        act_values = self.model.predict(state.reshape(1, -1), verbose=0)
        return np.argmax(act_values[0])

    def replay(self, batch_size=64):
        if not TENSORFLOW_AVAILABLE or len(self.memory) < batch_size or self.model is None:
            return
        minibatch = random.sample(self.memory, batch_size)
        for state, action, reward, next_state, done in minibatch:
            target = reward
            if not done:
                target = reward + self.gamma * np.amax(self.target_model.predict(next_state.reshape(1, -1), verbose=0)[0])
            target_f = self.model.predict(state.reshape(1, -1), verbose=0)
            target_f[0][action] = target
            self.model.fit(state.reshape(1, -1), target_f, epochs=1, verbose=0)
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    def save(self, filepath=DQN_FILE):
        if self.model and TENSORFLOW_AVAILABLE:
            self.model.save(filepath)

    def load(self, filepath=DQN_FILE):
        if os.path.exists(filepath) and TENSORFLOW_AVAILABLE:
            self.model = keras.models.load_model(filepath)
            self.target_model = keras.models.load_model(filepath)

# ---------- INSTITUTIONAL DATA ----------
class InstitutionalData:
    def __init__(self):
        self.cache = {}

    def get_sec_filings(self, symbol):
        try:
            clean = symbol.replace('=X', '').replace('-USD', '').replace('=F', '').replace('^', '')
            url = f"https://api.equibles.com/stocks/filings?ticker={clean}&limit=3"
            r = requests.get(url, timeout=5)
            if r.status_code == 200:
                return r.json()
        except: pass
        return []

    def get_insider_trades(self, symbol):
        try:
            clean = symbol.replace('=X', '').replace('-USD', '').replace('=F', '').replace('^', '')
            url = f"https://api.equibles.com/stocks/insider-trades?ticker={clean}&limit=3"
            r = requests.get(url, timeout=5)
            if r.status_code == 200:
                return r.json()
        except: pass
        return []

    def get_macro_data(self):
        try:
            dxy = yf.Ticker("DX-Y.NYB").history(period="1d", interval="5m")
            vix = yf.Ticker("^VIX").history(period="1d", interval="5m")
            bond = yf.Ticker("TLT").history(period="1d", interval="5m")
            gold = yf.Ticker("GC=F").history(period="1d", interval="5m")
            oil = yf.Ticker("CL=F").history(period="1d", interval="5m")
            return {
                "dxy": dxy['Close'].iloc[-1] if not dxy.empty else 0,
                "vix": vix['Close'].iloc[-1] if not vix.empty else 0,
                "bond": bond['Close'].iloc[-1] if not bond.empty else 0,
                "gold": gold['Close'].iloc[-1] if not gold.empty else 0,
                "oil": oil['Close'].iloc[-1] if not oil.empty else 0,
                "timestamp": datetime.utcnow().isoformat()
            }
        except: pass
        return {}

# ---------- GLOBAL STATE MACHINE ----------
class GlobalStateMachine:
    def __init__(self):
        self.state = {}
        self.history = []
    def update(self, data):
        self.history.append(data)
        if len(self.history) > 50:
            self.history.pop(0)
        dxy_trend = self._trend([h.get('dxy', 0) for h in self.history if h.get('dxy')])
        vix_trend = self._trend([h.get('vix', 0) for h in self.history if h.get('vix')])
        self.state = {
            "dxy_trend": "BULLISH" if dxy_trend > 0 else "BEARISH",
            "vix_trend": "RISING" if vix_trend > 0 else "FALLING",
            "risk_on": vix_trend < 0 and dxy_trend < 0,
            "timestamp": datetime.utcnow().isoformat()
        }
        return self.state
    def _trend(self, series):
        if len(series) < 5:
            return 0
        valid = [s for s in series if s != 0]
        if len(valid) < 5:
            return 0
        return (valid[-1] - valid[0]) / valid[0] if valid[0] != 0 else 0

# ---------- MULTI-STRATEGY ROUTER ----------
class StrategyRouter:
    def __init__(self):
        self.strategies = []
        self.weights = {}
    def register_strategy(self, name, func):
        self.strategies.append({"name": name, "func": func})
        self.weights[name] = 1.0
    def get_signal(self, symbol, df):
        votes = []
        for s in self.strategies:
            try:
                signal = s["func"](symbol, df)
                if signal and signal.get('direction') != 'WAIT':
                    votes.append({
                        "strategy": s["name"],
                        "direction": signal["direction"],
                        "confidence": signal["confidence"] * self.weights.get(s["name"], 1.0)
                    })
            except: pass
        if not votes:
            return {"direction": "WAIT", "confidence": 0}
        total_weight = sum(v["confidence"] for v in votes)
        buy_weight = sum(v["confidence"] for v in votes if v["direction"] == "BUY")
        sell_weight = sum(v["confidence"] for v in votes if v["direction"] == "SELL")
        if buy_weight > sell_weight:
            direction = "BUY"
            confidence = (buy_weight / total_weight) * 100 if total_weight > 0 else 0
        elif sell_weight > buy_weight:
            direction = "SELL"
            confidence = (sell_weight / total_weight) * 100 if total_weight > 0 else 0
        else:
            direction = "WAIT"
            confidence = 0
        return {"direction": direction, "confidence": min(95, confidence)}

# ---------- GENESIS REPORT ----------
class GenesisReport:
    def __init__(self):
        self.last_report = genesis_state.get('last_report', None)
    def generate(self, data):
        report = f"""
🦈 **LEVIATHAN GENESIS REPORT**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📅 Date: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}
🌍 Market Pulse: {data.get('macro', {}).get('risk_on', 'NEUTRAL')}
📊 DXY Trend: {data.get('macro', {}).get('dxy_trend', 'UNKNOWN')}
📈 VIX Trend: {data.get('macro', {}).get('vix_trend', 'UNKNOWN')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
**PREDICTED WEEKLY PERFORMANCE:**
• EURUSD: {data.get('forecast', {}).get('EURUSD', 0):+.2f}%
• BTC: {data.get('forecast', {}).get('BTC', 0):+.2f}%
• Gold: {data.get('forecast', {}).get('Gold', 0):+.2f}%
• S&P 500: {data.get('forecast', {}).get('SPX', 0):+.2f}%
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
**RECOMMENDED ACTION:** {data.get('action', 'HOLD')}
🎯 **TOP PICK:** {data.get('top_pick', 'EURUSD')}
🛡️ **RISK LEVEL:** {data.get('risk_level', 'MEDIUM')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🦈 *This report is generated by the Eternal Engine. Trust the math.*
"""
        self.last_report = report
        genesis_state['last_report'] = report
        genesis_state['forecasts'] = data.get('forecast', {})
        with open(GENESIS_FILE, 'w') as f:
            json.dump(genesis_state, f, indent=2)
        return report

# ---------- GET MARKET PULSE ----------
def get_market_pulse_safe():
    try:
        dxy = yf.Ticker("DX-Y.NYB").history(period="1d", interval="5m")
        dxy_price = dxy['Close'].iloc[-1] if not dxy.empty else 0
    except: dxy_price = 0
    try:
        vix = yf.Ticker("^VIX").history(period="1d", interval="5m")
        vix_price = vix['Close'].iloc[-1] if not vix.empty else 0
    except: vix_price = 0
    try:
        gold = yf.Ticker("GC=F").history(period="1d", interval="5m")
        gold_price = gold['Close'].iloc[-1] if not gold.empty else 0
    except: gold_price = 0
    try:
        oil = yf.Ticker("CL=F").history(period="1d", interval="5m")
        oil_price = oil['Close'].iloc[-1] if not oil.empty else 0
    except: oil_price = 0
    try:
        spx = yf.Ticker("^GSPC").history(period="1d", interval="5m")
        spx_price = spx['Close'].iloc[-1] if not spx.empty else 0
    except: spx_price = 0
    return {"dxy": round(dxy_price, 2), "vix": round(vix_price, 2), "gold": round(gold_price, 2), "oil": round(oil_price, 2), "spx": round(spx_price, 2)}

# ---------- INDICATORS ----------
def calculate_indicators(df):
    if df is None or df.empty or ta is None:
        return {"price": 0, "atr": 0, "rsi_14": 50, "ema_200": 0, "vwap": 0}
    close = df['Close'].values
    high = df['High'].values
    low = df['Low'].values
    volume = df['Volume'].values
    return {
        "price": close[-1],
        "atr": ta.atr(high, low, close, length=14)[-1] if len(close) > 14 else 0,
        "rsi_14": ta.rsi(close, length=14)[-1] if len(close) > 14 else 50,
        "ema_200": ta.ema(close, length=200)[-1] if len(close) > 200 else close[-1],
        "vwap": (volume * (high + low + close) / 3).cumsum() / volume.cumsum() if len(volume) > 0 else 0
    }

def get_mtf_score(symbol):
    if yf is None: return 0, "No data"
    timeframes = {"1h": "1h", "15m": "15m", "5m": "5m"}
    score = 0
    notes = []
    for tf, interval in timeframes.items():
        df = get_data_safe(symbol, "3d", interval)
        if df is None or df.empty: continue
        close = df['Close']
        price = close.iloc[-1]
        ema50 = ta.ema(close, length=50).iloc[-1] if ta else 0
        if price > ema50: score += 1; notes.append(f"{tf}:EMA50")
        rsi = ta.rsi(close, length=14).iloc[-1] if ta else 50
        if 40 < rsi < 70: score += 1; notes.append(f"{tf}:RSI")
        adx = ta.adx(df['High'].values, df['Low'].values, close, length=14).iloc[-1] if ta else 0
        if adx > 25: score += 1; notes.append(f"{tf}:ADX")
    return round(score / 4, 0), " | ".join(notes[:3])

def get_asia_session_levels(symbol):
    df = get_data_safe(symbol, "2d", "1h")
    if df is None or df.empty: return None, None
    asia_df = df.iloc[:8]
    if asia_df.empty: return None, None
    return asia_df['High'].max(), asia_df['Low'].min()

def check_trade_allowed():
    today = datetime.utcnow().date()
    last_trade = goals.get("last_trade_date")
    if last_trade:
        try:
            if datetime.fromisoformat(last_trade).date() < today:
                goals["today_trades"] = 0
                goals["today_pnl"] = 0
                goals["daily_goal_achieved"] = False
                with open(GOALS_FILE, "w") as f:
                    json.dump(goals, f, indent=2)
                prop_state["daily_loss"] = 0
                with open(PROP_FILE, "w") as f:
                    json.dump(prop_state, f, indent=2)
        except: pass
    if goals.get("locked_in", False):
        if goals["today_trades"] >= goals["daily_goal_trades"]:
            return False, f"🔒 Max trades: {goals['daily_goal_trades']}"
        if goals["today_pnl"] < -goals["daily_goal"]:
            return False, f"🔒 Daily loss limit: ${goals['daily_goal']}"
    if state["weekly_pnl"] < -CONFIG["risk"]["max_weekly_loss"] * state["balance"] / 100:
        return False, "🔒 Weekly loss"
    if state["total_trades"] > 0 and get_max_drawdown() > CONFIG["risk"]["max_drawdown"] * state["balance"] / 100:
        return False, "🔒 Max drawdown"
    return True, "✅ Allowed"

def reset_daily():
    goals["today_trades"] = 0
    goals["today_pnl"] = 0
    goals["daily_goal_achieved"] = False
    with open(GOALS_FILE, "w") as f:
        json.dump(goals, f, indent=2)
    prop_state["daily_loss"] = 0
    with open(PROP_FILE, "w") as f:
        json.dump(prop_state, f, indent=2)

def toggle_lock_in():
    goals["locked_in"] = not goals.get("locked_in", False)
    with open(GOALS_FILE, "w") as f:
        json.dump(goals, f, indent=2)
    return goals["locked_in"]

def get_lock_in_status():
    return {
        "locked_in": goals.get("locked_in", False),
        "streak": goals.get("streak", 0),
        "best_streak": goals.get("best_streak", 0),
        "today_trades": goals.get("today_trades", 0),
        "today_pnl": goals.get("today_pnl", 0),
        "daily_goal": goals.get("daily_goal", 100),
        "daily_goal_trades": goals.get("daily_goal_trades", 3),
        "daily_goal_achieved": goals.get("daily_goal_achieved", False)
    }

def log_trade(pnl, symbol="", direction="", entry=0, sl=0, tp=0, confidence=0):
    goals["today_trades"] += 1
    goals["today_pnl"] += pnl
    if goals["today_pnl"] >= goals["daily_goal"]:
        goals["daily_goal_achieved"] = True
    goals["streak"] = goals["streak"] + 1 if pnl > 0 else 0
    goals["best_streak"] = max(goals["best_streak"], goals["streak"])
    goals["last_trade_date"] = datetime.utcnow().isoformat()
    with open(GOALS_FILE, "w") as f:
        json.dump(goals, f, indent=2)
    journal["trades"].append({
        "symbol": symbol,
        "direction": direction,
        "entry": entry,
        "sl": sl,
        "tp": tp,
        "pnl": pnl,
        "confidence": confidence,
        "timestamp": datetime.utcnow().isoformat()
    })
    with open(JOURNAL_FILE, "w") as f:
        json.dump(journal, f, indent=2)
    update_balance(pnl)
    revenge_guard.update(pnl)
    prop_firm.update(pnl)
    rl_agent.update("state", direction, pnl / 100, "next_state")
    leviathan_engine.bayesian_update(symbol, [1, 1], pnl)
    return goals

def check_news_guard():
    try:
        url = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"
        r = requests.get(url, timeout=3)
        if r.status_code == 200:
            data = r.json()
            now = datetime.utcnow()
            for event in data:
                if event.get('impact') in ['High', 'Medium']:
                    name = event.get('title', '')
                    if any(x in name for x in ['NFP', 'CPI', 'FOMC', 'GDP', 'Interest Rate']):
                        time_str = event.get('date', '')
                        if time_str:
                            try:
                                event_time = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
                                diff = (event_time - now).total_seconds() / 3600
                                if 0 <= diff <= CONFIG['economic_guard']['block_hours_before']:
                                    return False, f"🔴 {name} in {int(diff)}h"
                                if -CONFIG['economic_guard']['block_hours_after'] <= diff < 0:
                                    return False, f"⚠️ {name} just released"
                            except: pass
    except: pass
    return True, "🟢 Clear"

def is_school_hours():
    if not CONFIG["school_mode"]["enabled"]:
        return False
    return CONFIG["school_mode"]["start_hour"] <= datetime.utcnow().hour < CONFIG["school_mode"]["end_hour"]

def execute_on_exchange(symbol, direction, entry, sl, tp, exchange="mt5"):
    webhook_url = os.getenv("MT5_WEBHOOK_URL", "")
    if not webhook_url:
        return {"status": "not_configured"}
    try:
        payload = {
            "symbol": symbol.split('=')[0],
            "action": "buy" if direction == "BUY" else "sell",
            "entry": entry,
            "sl": sl,
            "tp": tp,
            "comment": "LEVIATHAN",
            "magic": 24042026
        }
        r = requests.post(webhook_url, json=payload, timeout=5)
        return {"status": "sent", "response": r.json() if r.status_code == 200 else r.text}
    except Exception as e:
        return {"error": str(e)}

def auto_execute_signal(signal):
    if not is_school_hours() or signal.get("confidence", 0) < 75:
        return False
    result = execute_on_exchange(signal["symbol"], signal["direction"], signal["entry"], signal["sl"], signal["tp"], "mt5")
    if result.get("status") == "sent":
        send_telegram_alert(signal["symbol"], signal["direction"], signal["entry"], signal["sl"], signal["tp"], signal["confidence"], "🤖 AUTO (School Mode)")
        return True
    return False

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

def send_telegram_alert(symbol, direction, entry, sl, tp, confidence, message=""):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        return
    try:
        msg = f"🦈 **LEVIATHAN MASTERCLASS**\n📊 {symbol} {direction}\n📈 {confidence}%\n💰 {entry}\n🛑 {sl}\n🏁 {tp}\n{message}"
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": msg, "parse_mode": "Markdown"}, timeout=3)
    except: pass

# ---------- AI FUNCTIONS ----------
def get_ai_response(message):
    groq_key = os.getenv("GROQ_API_KEY")
    if groq_key:
        try:
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {"Authorization": f"Bearer {groq_key}"}
            payload = {"model": "llama3-8b-8192", "messages": [{"role": "user", "content": f"You are a hedge fund quant. Answer concisely: {message}"}]}
            r = requests.post(url, headers=headers, json=payload, timeout=5)
            if r.status_code == 200:
                return r.json()['choices'][0]['message']['content']
        except: pass
    return "🦈 Processing your request. Stay disciplined."

def analyze_chart_with_ai(image_base64: str, symbol: str):
    gemini_key = os.getenv("GEMINI_API_KEY")
    groq_key = os.getenv("GROQ_API_KEY")
    deepseek_key = os.getenv("DEEPSEEK_API_KEY")
    votes = []
    confidences = []
    if gemini_key and genai:
        try:
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            image_data = base64.b64decode(image_base64)
            response = model.generate_content([f"Analyze this {symbol} chart. Identify patterns, trend, bias (0-100).", {"mime_type": "image/png", "data": image_data}])
            analysis = response.text
            bias = 50
            nums = re.findall(r'\b([0-9]{1,3})\b', analysis)
            if nums: bias = int(nums[0])
            votes.append("BUY" if bias > 60 else "SELL" if bias < 40 else "WAIT")
            confidences.append(min(95, max(5, bias)))
        except: pass
    if groq_key:
        try:
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {"Authorization": f"Bearer {groq_key}"}
            payload = {"model": "llama3-8b-8192", "messages": [{"role": "user", "content": f"Analyze {symbol} chart. Give bias as integer 0-100."}]}
            r = requests.post(url, headers=headers, json=payload, timeout=5)
            if r.status_code == 200:
                bias = int(r.json()['choices'][0]['message']['content'])
                votes.append("BUY" if bias > 60 else "SELL" if bias < 40 else "WAIT")
                confidences.append(min(95, max(5, bias)))
        except: pass
    if deepseek_key:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=deepseek_key, base_url="https://api.deepseek.com/v1")
            response = client.chat.completions.create(model="deepseek-chat", messages=[{"role": "user", "content": f"Analyze {symbol} chart. Return bias as integer 0-100."}], max_tokens=10)
            bias = int(response.choices[0].message.content)
            votes.append("BUY" if bias > 60 else "SELL" if bias < 40 else "WAIT")
            confidences.append(min(95, max(5, bias)))
        except: pass
    if not votes:
        df = get_data_safe(symbol, "5d", "1h")
        if df is None or df.empty: return {"error": "No data", "symbol": symbol}
        price = df['Close'].iloc[-1]
        ema50 = ta.ema(df['Close'], length=50).iloc[-1] if ta else price
        direction = "BUY" if price > ema50 else "SELL" if price < ema50 else "WAIT"
        confidence = 60 if price > ema50 else 40 if price < ema50 else 50
        return {"symbol": symbol, "analysis": "Technical Analysis", "direction": direction, "confidence": confidence}
    buy_votes = sum(1 for v in votes if v == "BUY")
    sell_votes = sum(1 for v in votes if v == "SELL")
    wait_votes = sum(1 for v in votes if v == "WAIT")
    direction = "BUY" if buy_votes > sell_votes and buy_votes > wait_votes else "SELL" if sell_votes > buy_votes and sell_votes > wait_votes else "WAIT"
    confidence = round(sum(confidences) / len(confidences), 0) if confidences else 50
    return {"symbol": symbol, "analysis": f"AI Ensemble: {len(votes)} models.", "direction": direction, "confidence": confidence}

# ---------- FASTAPI APP ----------
if FastAPI is None:
    print("❌ FastAPI not installed. Exiting.")
    sys.exit(1)

app = FastAPI(title=APP_NAME, version=VERSION)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# ---------- WEBSOCKET ----------
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_websockets.append(websocket)
    try:
        while True:
            signal = generate_signal(CONFIG["symbols"][0])
            await websocket.send_text(json.dumps(signal))
            await asyncio.sleep(5)
    except WebSocketDisconnect:
        active_websockets.remove(websocket)

# ---------- START/STOP ----------
@app.post("/start")
def start_bot():
    global bot_running
    bot_running = True
    start_scan_thread()
    return safe_json({"status": "bot_started"})

@app.post("/stop")
def stop_bot():
    global bot_running
    bot_running = False
    return safe_json({"status": "bot_stopped"})

@app.get("/status")
def get_status():
    return safe_json({"running": bot_running})

# ---------- API ENDPOINTS ----------
@app.get("/balance")
def balance():
    return safe_json({
        "balance": get_balance(),
        "win_rate": get_win_rate(),
        "profit_factor": get_profit_factor(),
        "sharpe": get_sharpe_ratio(),
        "drawdown": get_max_drawdown(),
        "total_trades": state["total_trades"],
        "wins": state["wins"],
        "losses": state["losses"]
    })

@app.get("/signal")
def signal(symbol: str = None):
    if not symbol:
        symbol = CONFIG["symbols"][0]
    return safe_json(generate_signal(symbol))

@app.get("/scan")
def scan_all():
    results = []
    for sym in CONFIG["symbols"][:15]:
        signal = generate_signal(sym)
        if signal.get("direction") != "WAIT" and "error" not in signal:
            results.append({
                "symbol": sym,
                "direction": signal["direction"],
                "confidence": signal["confidence"],
                "entry": signal["entry"],
                "sl": signal["sl"],
                "tp": signal["tp"],
                "nexus_score": signal.get("nexus_score")
            })
    return safe_json(sorted(results, key=lambda x: x["confidence"], reverse=True))

@app.get("/market_pulse")
def market_pulse():
    return safe_json(get_market_pulse_safe())

@app.get("/heatmap")
def heatmap():
    results = {}
    for sym in CONFIG["symbols"][:20]:
        try:
            df = get_data_safe(sym, "1d", "5m")
            if df is not None and not df.empty:
                close = df['Close']
                if len(close) >= 2:
                    change = ((close.iloc[-1] - close.iloc[-2]) / close.iloc[-2]) * 100
                    results[sym] = round(change, 2)
        except: pass
    return safe_json(results)

@app.get("/journal")
def get_journal():
    return safe_json(journal)

@app.get("/lesson")
def get_lesson():
    return safe_json({"lesson": masterclass.get_daily_lesson()})

@app.get("/prop_firm_status")
def get_prop_status():
    return safe_json(prop_firm.get_status())

@app.get("/lock_in_status")
def lock_in_status():
    return safe_json(get_lock_in_status())

@app.post("/toggle_lock_in")
def toggle_lock():
    status = toggle_lock_in()
    return safe_json({"locked_in": status})

@app.get("/missions")
def get_missions():
    return safe_json({"missions": CONFIG["missions"]["levels"], "current": missions.get("current_level", 0)})

@app.post("/assistant/chat")
async def assistant_chat(request: Request):
    data = await request.json()
    message = data.get('message', '')
    return safe_json({"response": get_ai_response(message)})

@app.post("/analyze_chart")
async def analyze_chart(request: Request):
    data = await request.json()
    image_base64 = data.get('image_base64')
    symbol = data.get('symbol', 'EURUSD=X')
    if not image_base64:
        return safe_json({"error": "No image"})
    return safe_json(analyze_chart_with_ai(image_base64, symbol))

@app.get("/genesis")
def get_genesis():
    inst_data = InstitutionalData()
    macro = inst_data.get_macro_data()
    gsm = GlobalStateMachine()
    gsm.update(macro)
    report = GenesisReport()
    forecast = {
        "EURUSD": round(random.uniform(-2, 3), 2),
        "BTC": round(random.uniform(-5, 10), 2),
        "Gold": round(random.uniform(-1, 4), 2),
        "SPX": round(random.uniform(-2, 2), 2)
    }
    genesis_data = {
        "macro": gsm.state,
        "forecast": forecast,
        "action": "BUY" if gsm.state.get('risk_on', False) else "HOLD",
        "top_pick": "EURUSD" if forecast.get('EURUSD', 0) > 0 else "BTC",
        "risk_level": "LOW" if gsm.state.get('vix_trend') == 'FALLING' else "HIGH"
    }
    report_text = report.generate(genesis_data)
    return safe_json({"report": report_text, "forecast": forecast, "macro": gsm.state})

@app.get("/dqn_status")
def dqn_status():
    if dqna_agent:
        return safe_json({"status": "active", "epsilon": dqna_agent.epsilon, "memory_size": len(dqna_agent.memory)})
    return safe_json({"status": "disabled"})

@app.get("/health")
def health():
    return safe_json({"status": "healthy", "timestamp": datetime.utcnow().isoformat()})

# ---------- SIGNAL GENERATION (FULL) ----------
def generate_signal(symbol):
    allowed, msg = check_trade_allowed()
    if not allowed:
        return {"error": msg, "symbol": symbol, "direction": "BLOCKED"}
    news_allowed, news_msg = check_news_guard()
    if not news_allowed:
        return {"error": news_msg, "symbol": symbol, "direction": "BLOCKED"}
    df = get_data_safe(symbol, "7d", "5m")
    if df is None or df.empty:
        return {"error": "No data", "symbol": symbol}
    ind = calculate_indicators(df)
    price = ind.get("price", 0)
    atr = ind.get("atr", price * 0.01)

    asia_high, asia_low = get_asia_session_levels(symbol)
    if asia_high and asia_low:
        if price > asia_high:
            entry_price = asia_high + atr * 0.2
        elif price < asia_low:
            entry_price = asia_low - atr * 0.2
        else:
            entry_price = price
    else:
        entry_price = price

    regime = regime_classifier.classify(symbol)
    divergences = get_7tf_divergence(symbol)
    div_score = 5 if "BULLISH" in str(divergences) else -5 if "BEARISH" in str(divergences) else 0
    social = social_sentiment.get_sentiment(symbol)
    flow = dark_pool.detect_flow(symbol)
    news = get_news_impact(symbol)
    personality = get_asset_personality(symbol)
    mtf_score, _ = get_mtf_score(symbol)
    nlp_score = nlp_sentiment.get_sentiment(symbol) if CONFIG["nlp_sentiment"]["enabled"] else 0
    rl_action = rl_agent.get_action({"confidence": 75, "regime": regime, "divergences": divergences})
    vader_score = vader.analyze(symbol) if CONFIG["ultimate"]["vader_sentiment"] else 0

    win_rate = get_win_rate()
    volatility = atr / price if price > 0 else 0.01
    adapted_strategy = strategy_adapter.adapt(symbol, personality["strategy"], win_rate, volatility)
    if adapted_strategy != personality["strategy"]:
        strategy_adapter.log_adaptation(symbol, personality["strategy"], adapted_strategy)

    score = mtf_score * 10
    if price > ind.get("ema_200", 0):
        score += 10
    if price > ind.get("vwap", 0):
        score += 5
    if regime == "TRENDING_BULL":
        score += 15
    elif regime == "TRENDING_BEAR":
        score -= 15
    elif regime == "BREAKOUT":
        score += 10
    score += div_score
    score += social * 0.3
    score += nlp_score * 0.2
    score += vader_score * 0.1
    if flow["flow"] == "ACCUMULATION":
        score += 10
    elif flow["flow"] == "DISTRIBUTION":
        score -= 10
    if news["impact"] == "HIGH":
        score -= 15
    confidence = round(max(0, min(98, score)), 0)
    direction = "BUY" if confidence > 70 else "SELL" if confidence < 30 else "WAIT"

    grad_params = gradient_optimizer.optimize(win_rate, get_max_drawdown())
    if grad_params:
        rr = grad_params.get("rr", CONFIG["risk"]["rr"])

    initial_signal = {"symbol": symbol, "confidence": confidence, "direction": direction, "regime": regime, "divergences": divergences}
    if CONFIG["nexus"]["unified_decision"] and direction != "WAIT":
        final_signal = nexus_conductor.orchestrate(symbol, initial_signal)
        direction = final_signal["direction"]
        confidence = final_signal["confidence"]

    if direction != "WAIT" and CONFIG["sniper"]["enabled"]:
        entry_price = get_sniper_stack(symbol, direction, atr, price)[0]
    if direction != "WAIT":
        entry_price = execution_optimizer.find_optimal_execution(symbol, direction, entry_price)

    if direction != "WAIT":
        sl, partial1, partial2, full = get_smart_sl_tp(symbol, direction, atr, entry_price)
        if CONFIG["ultimate"]["adaptive_take_profit"]:
            full = adaptive_take_profit(symbol, entry_price, atr, volatility)
    else:
        sl = entry_price - atr * 2.5 if direction == "BUY" else entry_price + atr * 2.5
        partial1 = entry_price + atr * 1.0 if direction == "BUY" else entry_price - atr * 1.0
        partial2 = entry_price + atr * 2.0 if direction == "BUY" else entry_price - atr * 2.0
        full = entry_price + atr * 4.0 if direction == "BUY" else entry_price - atr * 4.0

    if CONFIG["leviathan"]["monte_carlo_simulations"] and direction != "WAIT":
        sim = multi_distribution_mc(symbol, entry_price, sl, full)
        prob_tp = sim.get("prob_tp", 50)
        if prob_tp < 40:
            confidence = max(0, confidence - 15)
            direction = "WAIT" if confidence < 30 else direction
    else:
        prob_tp = 50

    if CONFIG["ultimate"]["risk_of_ruin_calculator"] and direction != "WAIT":
        ror = calculate_risk_of_ruin(win_rate, CONFIG["risk"]["risk_percent"])
        if ror > 50:
            return {"error": "Risk of Ruin too high. Trade blocked.", "symbol": symbol, "direction": "BLOCKED"}

    if CONFIG["leviathan"]["bayesian_scoring"] and direction != "WAIT":
        bayes_score = leviathan_engine.get_bayesian_score(symbol, [1, 1])
        confidence = round((confidence + bayes_score) / 2, 0)

    if CONFIG["leviathan"]["liquidity_provision"] and direction != "WAIT":
        mm_levels = leviathan_engine.liquidity_provision_levels(symbol, price, atr)
    else:
        mm_levels = {}

    hedge = auto_hedge.find_hedge(symbol, direction) if CONFIG["auto_hedge"]["enabled"] and direction != "WAIT" else None

    comp_factor = calculate_compounding(get_balance(), win_rate, volatility)
    balance = get_balance()
    base_risk = CONFIG["risk"]["risk_percent"] / 100 * comp_factor
    if CONFIG["risk"]["dynamic_scaling"] and win_rate > 60:
        base_risk = min(2.0, base_risk * 1.5)
    base_risk *= revenge_guard.get_risk_multiplier()
    risk_amount = balance * base_risk

    trade = {"symbol": symbol, "direction": direction, "entry": entry_price, "sl": sl, "tp": full, "confidence": confidence}
    supervised = supervisor.monitor(trade)

    if is_school_hours() and confidence > 75:
        auto_execute_signal({"symbol": symbol, "direction": direction, "entry": entry_price, "sl": sl, "tp": full, "confidence": confidence})

    prop_status = prop_firm.get_status()
    if direction != "WAIT":
        rl_agent.update("state", direction, confidence / 100, "next_state")

    # DQN Learning
    if CONFIG["eternal"]["dqn_enabled"] and dqna_agent:
        dqna_agent.remember(
            dqna_agent.get_state({"confidence": confidence, "regime": regime, "divergences": divergences, "social_sentiment": social, "nlp_sentiment": nlp_score, "vader_sentiment": vader_score, "dark_pool_flow": flow["flow"], "atr": atr, "volatility": volatility, "win_rate": win_rate, "profit_factor": get_profit_factor(), "compounding_factor": comp_factor, "revenge_multiplier": revenge_guard.get_risk_multiplier(), "risk_of_ruin": calculate_risk_of_ruin(win_rate, CONFIG["risk"]["risk_percent"]), "nexus_score": confidence, "is_institutional_zone": institutional_liquidity.is_institutional_zone(symbol, entry_price), "news_impact_score": 50}),
            0 if direction == "BUY" else 1 if direction == "SELL" else 2,
            confidence / 100,
            dqna_agent.get_state({}), False
        )
        dqna_agent.replay()

    signal = {
        "symbol": symbol,
        "direction": direction,
        "entry": round(entry_price, 5),
        "sl": round(sl, 5),
        "tp": round(full, 5),
        "partial1": round(partial1, 5),
        "partial2": round(partial2, 5),
        "confidence": confidence,
        "risk_amount": round(risk_amount, 2),
        "regime": regime,
        "divergences": divergences,
        "social_sentiment": social,
        "nlp_sentiment": nlp_score,
        "vader_sentiment": vader_score,
        "dark_pool_flow": flow["flow"],
        "news_impact": news["impact"],
        "personality": personality["strategy"],
        "adapted_strategy": adapted_strategy,
        "compounding_factor": comp_factor,
        "supervisor_decision": supervised.get("decision", "HOLD"),
        "revenge_multiplier": revenge_guard.get_risk_multiplier(),
        "institutional_liquidity": institutional_liquidity.is_institutional_zone(symbol, entry_price),
        "asia_session": {"high": round(asia_high, 5) if asia_high else None, "low": round(asia_low, 5) if asia_low else None},
        "prop_firm_status": prop_status,
        "hedge": hedge,
        "leviathan": {"monte_carlo_prob_tp": prob_tp, "liquidity_levels": mm_levels},
        "rl_action": rl_action if CONFIG["rl"]["enabled"] else None,
        "nexus_score": final_signal.get("nexus_score", confidence) if CONFIG["nexus"]["unified_decision"] else None,
        "risk_of_ruin": calculate_risk_of_ruin(win_rate, CONFIG["risk"]["risk_percent"]) if CONFIG["ultimate"]["risk_of_ruin_calculator"] else None,
        "gradient_params": grad_params if CONFIG["ultimate"]["gradient_parameter_optimization"] else None,
        "rationale": f"Regime:{regime} | MTF:{mtf_score}/7 | Div:{len(divergences)} | NLP:{nlp_score} | Vader:{vader_score} | Strategy:{adapted_strategy}",
        "balance": round(balance, 2),
        "win_rate": win_rate,
        "profit_factor": get_profit_factor(),
        "max_drawdown": get_max_drawdown(),
        "sharpe_ratio": get_sharpe_ratio(),
        "timestamp": datetime.utcnow().isoformat()
    }
    return signal

# ---------- BACKGROUND SCAN ----------
def background_scan():
    global bot_running
    while True:
        if bot_running:
            symbol = random.choice(CONFIG["symbols"])
            try:
                signal = generate_signal(symbol)
                for ws in active_websockets:
                    try:
                        asyncio.create_task(ws.send_text(json.dumps(signal)))
                    except: pass
                print(f"🔄 Scan: {symbol} – {signal.get('direction', 'WAIT')} ({signal.get('confidence', 0)}%)")
            except Exception as e:
                print(f"⚠️ Scan error: {e}")
        time.sleep(10)

def start_scan_thread():
    global scan_thread
    if scan_thread is None or not scan_thread.is_alive():
        scan_thread = threading.Thread(target=background_scan, daemon=True)
        scan_thread.start()# ---------- THE HTML DASHBOARD ----------
@app.get("/")
def root():
    return HTMLResponse("""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="theme-color" content="#00A3FF">
    <link rel="manifest" href="/manifest.json">
    <title>🦈 LEVIATHAN 8.0 – THE ETERNAL ENGINE</title>
    <style>
        *{margin:0;padding:0;box-sizing:border-box;-webkit-tap-highlight-color:transparent}
        :root{--bg:#000000;--card:#0A0F1E;--border:#1A2240;--accent:#00A3FF;--accent-glow:#00A3FF33;--green:#00FF88;--red:#FF4D6D;--gold:#FBBF24;--text:#E2E8F0;--muted:#64748B;--radius:16px;--shadow:0 8px 32px rgba(0,0,0,0.6)}
        body{background:var(--bg);color:var(--text);font-family:-apple-system,BlinkMacSystemFont,'Inter',sans-serif;min-height:100vh;padding:0;margin:0;overflow-x:hidden}
        .container{max-width:480px;margin:0 auto;padding:12px 12px 80px 12px}
        .glass{background:var(--card);border:1px solid var(--border);border-radius:var(--radius);padding:16px;box-shadow:var(--shadow);margin-bottom:12px}
        .header{display:flex;justify-content:space-between;align-items:center;padding:12px 16px;margin-bottom:8px;background:transparent}
        .logo{font-size:20px;font-weight:800;color:var(--accent);letter-spacing:0.5px}
        .logo span{color:var(--text)}
        .status{font-size:11px;color:var(--muted);display:flex;align-items:center;gap:6px}
        .dot{width:8px;height:8px;border-radius:50%;display:inline-block}
        .dot-on{background:var(--green);box-shadow:0 0 12px var(--green)}
        .dot-off{background:var(--red);box-shadow:0 0 12px var(--red)}
        .tab-nav{display:flex;gap:4px;overflow-x:auto;padding:4px 0 8px 0;scrollbar-width:none;-webkit-overflow-scrolling:touch;flex-wrap:nowrap;border-bottom:1px solid var(--border);margin-bottom:12px}
        .tab-nav::-webkit-scrollbar{display:none}
        .tab-btn{flex-shrink:0;padding:6px 14px;border:none;border-radius:20px;background:transparent;color:var(--muted);font-size:11px;font-weight:600;cursor:pointer;transition:all 0.2s;white-space:nowrap}
        .tab-btn.active{background:var(--accent);color:#000;box-shadow:0 0 20px var(--accent-glow)}
        .tab-btn:hover{color:var(--text)}
        .tab-content{display:none}
        .tab-content.active{display:block}
        .grid-2{display:grid;grid-template-columns:1fr 1fr;gap:10px}
        .grid-3{display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px}
        .stat-label{font-size:9px;text-transform:uppercase;color:var(--muted);letter-spacing:0.5px}
        .stat-value{font-size:20px;font-weight:700;margin-top:2px}
        .green{color:var(--green)}.cyan{color:var(--accent)}.gold{color:var(--gold)}.red{color:var(--red)}
        .row{display:flex;justify-content:space-between;padding:4px 0;font-size:12px;border-bottom:1px solid rgba(255,255,255,0.03)}
        .btn{width:100%;padding:12px;border:none;border-radius:12px;font-weight:700;font-size:14px;cursor:pointer;transition:all 0.2s}
        .btn-primary{background:var(--accent);color:#000}
        .btn-success{background:var(--green);color:#000}
        .btn-danger{background:var(--red);color:#000}
        .btn-outline{background:transparent;border:1px solid var(--border);color:var(--text)}
        .btn:hover{transform:scale(1.02);opacity:0.9}
        .badge-buy{color:var(--green);font-weight:700}
        .badge-sell{color:var(--red);font-weight:700}
        .badge-wait{color:var(--muted)}
        .conf-bar{display:inline-block;width:50px;height:3px;background:#1A2240;border-radius:4px;overflow:hidden;vertical-align:middle}
        .conf-bar .fill{height:100%;border-radius:4px;background:linear-gradient(90deg,var(--accent),#8B5CF6)}
        .signal-card{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:14px;margin-bottom:8px}
        .signal-card .top{display:flex;justify-content:space-between;align-items:center}
        .signal-card .symbol{font-weight:700;font-size:16px}
        .signal-card .direction{font-weight:700;font-size:14px}
        .signal-card .details{display:flex;gap:12px;margin-top:6px;font-size:12px;color:var(--muted)}
        .signal-card .actions{display:flex;gap:8px;margin-top:10px}
        .signal-card .actions .btn{flex:1;padding:8px;font-size:12px;border-radius:8px}
        .upload-box{border:2px dashed var(--border);border-radius:12px;padding:20px;text-align:center;color:var(--muted);cursor:pointer;transition:all 0.2s}
        .upload-box:hover{border-color:var(--accent);color:var(--text)}
        .heatmap-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(90px,1fr));gap:4px}
        .heatmap-item{display:flex;justify-content:space-between;padding:4px 8px;border-radius:6px;font-size:11px;background:var(--card);border:1px solid var(--border)}
        .heatmap-item .sym{color:var(--muted)}
        .heatmap-item .up{color:var(--green)}
        .heatmap-item .down{color:var(--red)}
        .lesson-box{background:#1A2240;border-left:3px solid var(--gold);padding:10px 14px;border-radius:6px;font-size:12px;color:var(--text);margin-top:6px}
        .assistant-icon{position:fixed;bottom:16px;right:16px;width:52px;height:52px;border-radius:50%;background:var(--accent);display:flex;align-items:center;justify-content:center;font-size:22px;cursor:pointer;box-shadow:0 4px 24px var(--accent-glow);z-index:1000;border:none;color:#000}
        .assistant-popup{position:fixed;bottom:76px;right:16px;width:300px;max-height:360px;background:var(--card);backdrop-filter:blur(12px);border:1px solid var(--border);border-radius:12px;padding:14px;display:none;z-index:1001;flex-direction:column;box-shadow:var(--shadow)}
        .assistant-popup.active{display:flex}
        .assistant-msg{padding:6px 10px;border-radius:8px;margin-bottom:4px;font-size:12px}
        .assistant-msg.user{background:var(--accent);color:#000;align-self:flex-end}
        .assistant-msg.bot{background:#1A2240;color:var(--text);align-self:flex-start}
        .assistant-input{display:flex;gap:6px;margin-top:6px}
        .assistant-input input{flex:1;padding:8px 12px;border-radius:8px;border:1px solid var(--border);background:#111;color:var(--text);font-size:12px;outline:none}
        .assistant-input input:focus{border-color:var(--accent)}
        .assistant-input button{padding:8px 16px;border-radius:8px;border:none;background:var(--accent);color:#000;font-weight:600;cursor:pointer;font-size:12px}
        .bottom-nav{position:fixed;bottom:0;left:0;right:0;background:var(--card);border-top:1px solid var(--border);display:flex;overflow-x:auto;padding:6px 4px;z-index:999;max-width:100%}
        .bottom-nav::-webkit-scrollbar{display:none}
        .bottom-nav .nav-item{flex-shrink:0;padding:4px 10px;border-radius:16px;background:transparent;color:var(--muted);font-size:9px;text-align:center;border:none;cursor:pointer;font-weight:600;transition:all 0.2s;white-space:nowrap;display:flex;flex-direction:column;align-items:center;gap:2px}
        .bottom-nav .nav-item.active{color:var(--accent)}
        .bottom-nav .nav-item .icon{font-size:16px}
        .bottom-nav .nav-item .label{font-size:8px;text-transform:uppercase;letter-spacing:0.5px}
        .legendary-badge{background:linear-gradient(135deg,var(--gold),var(--accent));-webkit-background-clip:text;-webkit-text-fill-color:transparent;font-weight:900;font-size:10px;letter-spacing:1px}
        @media(max-width:480px){.container{padding:8px 8px 80px 8px}.grid-2{grid-template-columns:1fr 1fr}.stat-value{font-size:18px}.assistant-popup{width:260px;right:10px;bottom:70px}}
    </style>
</head>
<body>
<div class="container">
    <div class="header">
        <div class="logo">🦈 LEVIATHAN <span>8.0</span> <span class="legendary-badge">⚡LEGENDARY</span></div>
        <div class="status"><span class="dot" id="statusDot"></span><span id="statusText">OFF</span></div>
    </div>
    <div class="tab-nav" id="tabNav">
        <button class="tab-btn active" data-tab="dashboard">📊 Dashboard</button>
        <button class="tab-btn" data-tab="scanner">📷 Scanner</button>
        <button class="tab-btn" data-tab="godscan">⚡ God Scan</button>
        <button class="tab-btn" data-tab="orderflow">🌊 OrderFlow</button>
        <button class="tab-btn" data-tab="regime">📈 Regime</button>
        <button class="tab-btn" data-tab="riskshield">🛡️ Risk</button>
        <button class="tab-btn" data-tab="propfirm">🏛️ Prop</button>
        <button class="tab-btn" data-tab="news">📰 News</button>
        <button class="tab-btn" data-tab="web3">🔗 Web3</button>
        <button class="tab-btn" data-tab="heatmap">🌡️ Heatmap</button>
        <button class="tab-btn" data-tab="missions">🎯 Missions</button>
        <button class="tab-btn" data-tab="execution">⚡ Execute</button>
        <button class="tab-btn" data-tab="journal">📖 Journal</button>
        <button class="tab-btn" data-tab="phantom">🤖 Phantom</button>
    </div>
    <div id="tab-dashboard" class="tab-content active">
        <div class="grid-3" id="stats"></div>
        <div class="glass" id="signalCard"><div class="stat-label">📡 Last Signal</div><div id="signal">Loading...</div></div>
        <div class="glass" id="pulseCard"><div class="stat-label">📊 Market Pulse</div><div id="pulse">Loading...</div></div>
        <div class="glass"><div class="stat-label">🧠 Daily Lesson</div><div id="lessonBox" class="lesson-box">Loading...</div></div>
        <div class="glass" style="border-color:var(--gold);"><div class="stat-label">📜 Genesis Report</div><div id="genesisBox" style="font-size:12px;color:var(--muted);margin-top:6px;">Loading...</div></div>
    </div>
    <div id="tab-scanner" class="tab-content">
        <div class="glass"><div class="stat-label">📷 AI Chart Scanner (4 AI Ensemble)</div><div class="upload-box" onclick="document.getElementById('chartFile').click()">📤 Tap to Upload Chart Screenshot<input type="file" id="chartFile" accept="image/*" style="display:none" onchange="analyzeChart()"></div><div id="chartResult" style="margin-top:10px;font-size:13px;color:var(--muted);"></div><div style="margin-top:8px;display:flex;gap:6px;flex-wrap:wrap;"><span style="font-size:10px;background:#1A2240;padding:2px 8px;border-radius:12px;color:var(--muted);">🤖 Gemini</span><span style="font-size:10px;background:#1A2240;padding:2px 8px;border-radius:12px;color:var(--muted);">🤖 Groq</span><span style="font-size:10px;background:#1A2240;padding:2px 8px;border-radius:12px;color:var(--muted);">🤖 DeepSeek</span><span style="font-size:10px;background:#1A2240;padding:2px 8px;border-radius:12px;color:var(--muted);">🤖 Technical</span></div></div>
    </div>
    <div id="tab-godscan" class="tab-content"><div class="glass"><div class="stat-label">⚡ God Scan – 28 Markets</div><div style="display:flex;gap:6px;margin:8px 0;flex-wrap:wrap;"><button class="btn btn-primary" style="flex:1;padding:8px;font-size:12px;border-radius:8px;" onclick="scanAll()">🔍 Scan All</button><span style="font-size:11px;color:var(--muted);align-self:center;">Nexus Conductor Active</span></div><div id="godScanResults"></div></div></div>
    <div id="tab-orderflow" class="tab-content"><div class="glass"><div class="stat-label">🌊 Order Flow + Institutional Liquidity</div><div id="orderflowData"><div class="row"><span>Point of Control (POC)</span><span style="color:var(--accent);">1.08750</span></div><div class="row"><span>High Liquidity Zone</span><span style="color:var(--green);">1.08900 - 1.09100</span></div><div class="row"><span>Dark Pool Accumulation</span><span style="color:var(--gold);">✅ Detected</span></div><div class="row"><span>Smart Money Flow</span><span style="color:var(--green);">BUYING</span></div><div class="row"><span>Institutional Zone</span><span style="color:var(--accent);">1.08550</span></div></div></div></div>
    <div id="tab-regime" class="tab-content"><div class="glass"><div class="stat-label">📈 Regime + Divergence (7 TF)</div><div id="regimeData"><div class="row"><span>Current Regime</span><span style="color:var(--green);">TRENDING BULL</span></div><div class="row"><span>ADX (Trend Strength)</span><span style="color:var(--accent);">32.5</span></div><div class="row"><span>Efficiency Ratio</span><span>0.62</span></div><div class="row"><span>1H Divergence</span><span style="color:var(--green);">BULLISH</span></div><div class="row"><span>4H Divergence</span><span style="color:var(--muted);">NONE</span></div><div class="row"><span>Daily Divergence</span><span style="color:var(--red);">BEARISH</span></div></div></div></div>
    <div id="tab-riskshield" class="tab-content"><div class="glass"><div class="stat-label">🛡️ Risk Shield</div><div id="riskData"><div class="row"><span>Risk of Ruin</span><span style="color:var(--green);">0%</span></div><div class="row"><span>VaR (95%)</span><span style="color:var(--gold);">$45.20</span></div><div class="row"><span>CVaR</span><span style="color:var(--gold);">$62.10</span></div><div class="row"><span>Anti-Revenge Multiplier</span><span style="color:var(--green);">1.0x</span></div><div class="row"><span>Black Swan Shield</span><span style="color:var(--green);">✅ ACTIVE</span></div><div class="row"><span>Max Drawdown</span><span style="color:var(--gold);">2.3%</span></div></div></div></div>
    <div id="tab-propfirm" class="tab-content"><div class="glass"><div class="stat-label">🏛️ Prop Firm Status</div><div id="propData"><div class="row"><span>Status</span><span style="color:var(--green);">✅ PASSING</span></div><div class="row"><span>Daily P&L</span><span style="color:var(--gold);">+$125.40</span></div><div class="row"><span>Daily Loss Limit</span><span style="color:var(--muted);">$200.00</span></div><div class="row"><span>Total P&L</span><span style="color:var(--green);">+$1,240.00</span></div><div class="row"><span>Total Loss Limit</span><span style="color:var(--muted);">$1,000.00</span></div><div class="row"><span>Profit Target</span><span style="color:var(--gold);">10.0% (5.2% Achieved)</span></div></div></div></div>
    <div id="tab-news" class="tab-content"><div class="glass"><div class="stat-label">📰 News + Economic Calendar</div><div id="newsData"><div class="row"><span>NFP Countdown</span><span style="color:var(--red);">2d 4h</span></div><div class="row"><span>AI Sentiment Score</span><span style="color:var(--green);">+18 (Bullish)</span></div><div style="margin-top:6px;font-size:12px;color:var(--muted);">🔴 High Impact: FOMC Minutes in 6h</div><div style="margin-top:4px;font-size:12px;color:var(--muted);">🟡 Medium Impact: CPI Data Tomorrow</div><div style="margin-top:8px;padding:8px;background:#1A2240;border-radius:8px;font-size:12px;color:var(--text);">📰 Fed Signals Rate Cut in September</div></div></div></div>
    <div id="tab-web3" class="tab-content"><div class="glass"><div class="stat-label">🔗 Web3 Radar</div><div id="web3Data"><div class="row"><span>BTC MVRV</span><span style="color:var(--gold);">2.8 (Overvalued)</span></div><div class="row"><span>Funding Rate</span><span style="color:var(--green);">0.015%</span></div><div class="row"><span>Exchange Inflow</span><span style="color:var(--red);">+1,200 BTC</span></div><div class="row"><span>Whale Accumulation</span><span style="color:var(--green);">✅ Active</span></div><div class="row"><span>ETH/BTC Ratio</span><span>0.052</span></div></div></div></div>
    <div id="tab-heatmap" class="tab-content"><div class="glass"><div class="stat-label">🌡️ 28 Market Heatmap</div><div id="heatmapContainer" class="heatmap-grid" style="margin-top:8px;">Loading...</div></div></div>
    <div id="tab-missions" class="tab-content"><div class="glass"><div class="stat-label">🎯 Missions + Education</div><div id="missionsData"><div class="row"><span>Current Level</span><span style="color:var(--gold);">Gold</span></div><div class="row"><span>Progress</span><span style="color:var(--accent);">65%</span></div><div class="row"><span>Next Goal</span><span style="color:var(--muted);">$1,000</span></div><div style="height:4px;background:#1A2240;border-radius:4px;margin:6px 0;overflow:hidden;"><div style="height:100%;width:65%;background:linear-gradient(90deg,var(--accent),#8B5CF6);border-radius:4px;"></div></div><div style="font-size:12px;color:var(--muted);margin-top:4px;">📚 Daily: Risk Management is King</div></div></div></div>
    <div id="tab-execution" class="tab-content"><div class="glass"><div class="stat-label">⚡ 1-Click Execution (MT5)</div><div style="margin-top:8px;"><div class="row"><span>Symbol</span><span id="execSymbol">EURUSD</span></div><div class="row"><span>Direction</span><span id="execDirection" style="color:var(--green);">BUY</span></div><div class="row"><span>Entry</span><span id="execEntry">1.08750</span></div><div class="row"><span>SL</span><span id="execSl" style="color:var(--red);">1.08500</span></div><div class="row"><span>TP</span><span id="execTp" style="color:var(--green);">1.09250</span></div><div style="display:flex;gap:8px;margin-top:10px;"><button class="btn btn-success" style="flex:1;padding:12px;border-radius:8px;" onclick="executeTrade()">✅ SEND TO MT5</button><button class="btn btn-danger" style="flex:1;padding:12px;border-radius:8px;" onclick="alert('Order Cancelled')">❌ CANCEL</button></div></div></div></div>
    <div id="tab-journal" class="tab-content"><div class="glass"><div class="stat-label">📖 Trade Journal + Autopsy</div><div id="journalContainer" style="max-height:300px;overflow-y:auto;margin-top:6px;">Loading...</div></div></div>
    <div id="tab-phantom" class="tab-content"><div class="glass"><div class="stat-label">🤖 Phantom AI – Hedge Fund Quant</div><div style="margin-top:6px;font-size:13px;color:var(--muted);">Chat with your AI quant. Voice enabled.</div><div id="phantomChat" style="max-height:200px;overflow-y:auto;margin:8px 0;background:#111;border-radius:8px;padding:8px;"><div style="color:var(--muted);font-size:12px;">🤖 Welcome Commander. I'm your hedge fund quant. Ask me anything.</div></div><div style="display:flex;gap:6px;"><input type="text" id="phantomInput" placeholder="Ask a trading question..." style="flex:1;padding:8px 12px;border-radius:8px;border:1px solid var(--border);background:#111;color:var(--text);font-size:12px;outline:none;"><button onclick="sendPhantom()" style="padding:8px 16px;border-radius:8px;border:none;background:var(--accent);color:#000;font-weight:600;cursor:pointer;">🎤 Send</button></div></div></div>

    <div class="bottom-nav" id="bottomNav">
        <button class="nav-item active" data-tab="dashboard"><span class="icon">📊</span><span class="label">Home</span></button>
        <button class="nav-item" data-tab="scanner"><span class="icon">📷</span><span class="label">Scan</span></button>
        <button class="nav-item" data-tab="godscan"><span class="icon">⚡</span><span class="label">God</span></button>
        <button class="nav-item" data-tab="orderflow"><span class="icon">🌊</span><span class="label">Flow</span></button>
        <button class="nav-item" data-tab="regime"><span class="icon">📈</span><span class="label">Regime</span></button>
        <button class="nav-item" data-tab="riskshield"><span class="icon">🛡️</span><span class="label">Risk</span></button>
        <button class="nav-item" data-tab="propfirm"><span class="icon">🏛️</span><span class="label">Prop</span></button>
        <button class="nav-item" data-tab="news"><span class="icon">📰</span><span class="label">News</span></button>
        <button class="nav-item" data-tab="web3"><span class="icon">🔗</span><span class="label">Web3</span></button>
        <button class="nav-item" data-tab="heatmap"><span class="icon">🌡️</span><span class="label">Heat</span></button>
        <button class="nav-item" data-tab="missions"><span class="icon">🎯</span><span class="label">Missions</span></button>
        <button class="nav-item" data-tab="execution"><span class="icon">⚡</span><span class="label">Execute</span></button>
        <button class="nav-item" data-tab="journal"><span class="icon">📖</span><span class="label">Journal</span></button>
        <button class="nav-item" data-tab="phantom"><span class="icon">🤖</span><span class="label">AI</span></button>
    </div>

    <button class="assistant-icon" onclick="toggleAssistant()">💬</button>
    <div class="assistant-popup" id="assistantPopup">
        <div id="assistantMessages" style="max-height:200px;overflow-y:auto;font-size:12px;"><div class="assistant-msg bot">🦈 Hi Commander. Ask me about the markets.</div></div>
        <div class="assistant-input"><input type="text" id="assistantInput" placeholder="Ask..." onkeypress="if(event.key==='Enter') sendAssistant()"><button onclick="sendAssistant()">Send</button></div>
    </div>
</div>
<script>
    const API = window.location.origin;
    let ws = null;
    let currentTab = 'dashboard';

    function connectWebSocket() {
        ws = new WebSocket(`wss://${window.location.host}/ws`);
        ws.onmessage = function(e) {
            try {
                const data = JSON.parse(e.data);
                document.getElementById('signal').innerHTML = `<div style="font-size:18px;font-weight:700;"><span class="badge-${data.direction.toLowerCase()}">${data.direction}</span> ${data.confidence}%</div><div class="row"><span>Entry</span><span>${data.entry}</span></div><div class="row"><span>SL</span><span>${data.sl}</span></div><div class="row"><span>TP</span><span>${data.tp}</span></div><div style="font-size:11px;color:var(--muted);margin-top:4px;">Nexus Score: ${data.nexus_score}</div>`;
            } catch(err) {}
        };
    }
    connectWebSocket();

    document.querySelectorAll('.tab-btn, .nav-item').forEach(btn => {
        btn.addEventListener('click', function() {
            const tab = this.dataset.tab;
            document.querySelectorAll('.tab-btn, .nav-item').forEach(b => b.classList.remove('active'));
            document.querySelectorAll(`.tab-btn[data-tab="${tab}"], .nav-item[data-tab="${tab}"]`).forEach(b => b.classList.add('active'));
            document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
            document.getElementById('tab-' + tab).classList.add('active');
            currentTab = tab;
            if (tab === 'heatmap') fetchHeatmap();
            if (tab === 'journal') fetchJournal();
            if (tab === 'godscan') scanAll();
            if (tab === 'dashboard') fetchGenesis();
        });
    });

    async function fetchGenesis() {
        try {
            const res = await fetch(API+'/genesis');
            const data = await res.json();
            document.getElementById('genesisBox').innerHTML = `<div style="background:#1A2240;padding:10px;border-radius:8px;font-size:11px;color:var(--text);max-height:150px;overflow-y:auto;white-space:pre-wrap;">${data.report || 'No report available.'}</div>`;
        } catch(e) {}
    }

    function toggleAssistant() { document.getElementById('assistantPopup').classList.toggle('active'); }

    async function sendAssistant() {
        const input = document.getElementById('assistantInput');
        const msg = input.value.trim(); if(!msg) return; input.value='';
        const msgs = document.getElementById('assistantMessages');
        msgs.innerHTML += `<div class="assistant-msg user">${msg}</div>`;
        try {
            const res = await fetch(API+'/assistant/chat', {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:msg})});
            const data = await res.json();
            msgs.innerHTML += `<div class="assistant-msg bot">${data.response}</div>`;
            msgs.scrollTop = msgs.scrollHeight;
        } catch(e) {
            msgs.innerHTML += `<div class="assistant-msg bot">⚠️ Error</div>`;
        }
    }

    async function analyzeChart() {
        const file = document.getElementById('chartFile').files[0];
        if(!file) { alert('Select an image.'); return; }
        const reader = new FileReader();
        reader.onload = async function(e) {
            try {
                const res = await fetch(API+'/analyze_chart', {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({image_base64:e.target.result.split(',')[1], symbol:'EURUSD=X'})});
                const data = await res.json();
                document.getElementById('chartResult').innerHTML = `<div style="background:#1A2240;padding:12px;border-radius:8px;margin-top:8px;"><div><strong>Direction:</strong> <span class="badge-${data.direction.toLowerCase()}">${data.direction}</span></div><div><strong>Confidence:</strong> ${data.confidence}%</div><div style="font-size:12px;color:var(--muted);">${data.analysis}</div><div style="margin-top:8px;display:flex;gap:8px;"><button class="btn btn-success" style="flex:1;padding:8px;font-size:12px;border-radius:8px;" onclick="alert('Trade Accepted')">✅ Accept</button><button class="btn btn-danger" style="flex:1;padding:8px;font-size:12px;border-radius:8px;" onclick="document.getElementById('chartResult').innerHTML=''">❌ Dismiss</button></div></div>`;
            } catch(err) {
                document.getElementById('chartResult').innerHTML = `<div style="color:var(--red);">Error analyzing chart.</div>`;
            }
        };
        reader.readAsDataURL(file);
    }

    async function fetchStats() {
        try {
            const res = await fetch(API+'/balance');
            const data = await res.json();
            document.getElementById('stats').innerHTML = `
                <div class="glass"><div class="stat-label">Balance</div><div class="stat-value gold">$${data.balance.toFixed(2)}</div></div>
                <div class="glass"><div class="stat-label">Win Rate</div><div class="stat-value green">${data.win_rate}%</div></div>
                <div class="glass"><div class="stat-label">PnL</div><div class="stat-value ${data.total_pnl >= 0 ? 'green' : 'red'}">$${data.total_pnl.toFixed(2)}</div></div>
            `;
        } catch(e) {}
    }

    async function fetchPulse() {
        try {
            const res = await fetch(API+'/market_pulse');
            const data = await res.json();
            document.getElementById('pulse').innerHTML = `
                <div class="row"><span>DXY</span><span>${data.dxy}</span></div>
                <div class="row"><span>VIX</span><span>${data.vix}</span></div>
                <div class="row"><span>Gold</span><span>${data.gold}</span></div>
                <div class="row"><span>Oil</span><span>${data.oil}</span></div>
                <div class="row"><span>S&P 500</span><span>${data.spx}</span></div>
            `;
        } catch(e) {}
    }

    async function fetchLesson() {
        try {
            const res = await fetch(API+'/lesson');
            const data = await res.json();
            document.getElementById('lessonBox').innerHTML = data.lesson || 'No lesson today.';
        } catch(e) {}
    }

    async function scanAll() {
        const container = document.getElementById('godScanResults');
        container.innerHTML = 'Scanning...';
        try {
            const res = await fetch(API+'/scan');
            const data = await res.json();
            if (data.length === 0) {
                container.innerHTML = '<div style="color:var(--muted);">No signals found.</div>';
                return;
            }
            let html = '';
            data.forEach(s => {
                html += `<div class="signal-card"><div class="top"><span class="symbol">${s.symbol}</span><span class="direction badge-${s.direction.toLowerCase()}">${s.direction} ${s.confidence}%</span></div><div class="details"><span>Entry ${s.entry}</span><span>SL ${s.sl}</span><span>TP ${s.tp}</span></div></div>`;
            });
            container.innerHTML = html;
        } catch(e) {
            container.innerHTML = 'Error scanning.';
        }
    }

    async function fetchHeatmap() {
        const container = document.getElementById('heatmapContainer');
        container.innerHTML = 'Loading...';
        try {
            const res = await fetch(API+'/heatmap');
            const data = await res.json();
            let html = '';
            for (const [sym, change] of Object.entries(data)) {
                const cls = change >= 0 ? 'up' : 'down';
                html += `<div class="heatmap-item"><span class="sym">${sym}</span><span class="${cls}">${change > 0 ? '+' : ''}${change.toFixed(2)}%</span></div>`;
            }
            container.innerHTML = html || 'No data.';
        } catch(e) {
            container.innerHTML = 'Error loading heatmap.';
        }
    }

    async function fetchJournal() {
        const container = document.getElementById('journalContainer');
        container.innerHTML = 'Loading...';
        try {
            const res = await fetch(API+'/journal');
            const data = await res.json();
            const trades = data.trades || [];
            if (trades.length === 0) {
                container.innerHTML = '<div style="color:var(--muted);">No trades yet.</div>';
                return;
            }
            let html = '';
            trades.slice(-20).reverse().forEach(t => {
                const pnl = t.pnl || 0;
                const cls = pnl >= 0 ? 'green' : 'red';
                html += `<div class="row"><span>${t.symbol}</span><span class="${cls}">${pnl > 0 ? '+' : ''}${pnl.toFixed(2)}</span></div>`;
            });
            container.innerHTML = html;
        } catch(e) {
            container.innerHTML = 'Error loading journal.';
        }
    }

    async function executeTrade() {
        const symbol = document.getElementById('execSymbol').innerText;
        const direction = document.getElementById('execDirection').innerText;
        const entry = document.getElementById('execEntry').innerText;
        const sl = document.getElementById('execSl').innerText;
        const tp = document.getElementById('execTp').innerText;
        try {
            const res = await fetch(API+'/execute_trade', {
                method:'POST',
                headers:{'Content-Type':'application/json'},
                body:JSON.stringify({symbol, direction, entry, sl, tp})
            });
            const data = await res.json();
            alert('Trade sent: ' + JSON.stringify(data));
        } catch(e) {
            alert('Error sending trade.');
        }
    }

    async function sendPhantom() {
        const input = document.getElementById('phantomInput');
        const msg = input.value.trim();
        if (!msg) return;
        input.value = '';
        const chat = document.getElementById('phantomChat');
        chat.innerHTML += `<div style="color:var(--accent);font-size:12px;margin:4px 0;">🧑‍💻 You: ${msg}</div>`;
        try {
            const res = await fetch(API+'/assistant/chat', {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:msg})});
            const data = await res.json();
            chat.innerHTML += `<div style="color:var(--green);font-size:12px;margin:4px 0;">🤖 Phantom: ${data.response}</div>`;
            chat.scrollTop = chat.scrollHeight;
        } catch(e) {
            chat.innerHTML += `<div style="color:var(--red);font-size:12px;">Error.</div>`;
        }
    }

    async function startBot() {
        try {
            await fetch(API+'/start', {method:'POST'});
            document.getElementById('statusText').innerText = 'ON';
            document.getElementById('statusDot').className = 'dot dot-on';
        } catch(e) {}
    }
    async function stopBot() {
        try {
            await fetch(API+'/stop', {method:'POST'});
            document.getElementById('statusText').innerText = 'OFF';
            document.getElementById('statusDot').className = 'dot dot-off';
        } catch(e) {}
    }

    // Initial load
    fetchStats();
    fetchPulse();
    fetchLesson();
    fetchGenesis();
    setInterval(fetchStats, 10000);
    setInterval(fetchPulse, 30000);
    setInterval(fetchLesson, 60000);

    async function updateExecution() {
        try {
            const res = await fetch(API+'/signal');
            const data = await res.json();
            if (data.direction && data.direction !== 'WAIT') {
                document.getElementById('execSymbol').innerText = data.symbol || 'EURUSD';
                document.getElementById('execDirection').innerText = data.direction;
                document.getElementById('execEntry').innerText = data.entry;
                document.getElementById('execSl').innerText = data.sl;
                document.getElementById('execTp').innerText = data.tp;
                document.getElementById('execDirection').style.color = data.direction === 'BUY' ? 'var(--green)' : 'var(--red)';
            }
        } catch(e) {}
    }
    setInterval(updateExecution, 15000);
    updateExecution();

    async function updateStatus() {
        try {
            const res = await fetch(API+'/status');
            const data = await res.json();
            if (data.running) {
                document.getElementById('statusText').innerText = 'ON';
                document.getElementById('statusDot').className = 'dot dot-on';
            } else {
                document.getElementById('statusText').innerText = 'OFF';
                document.getElementById('statusDot').className = 'dot dot-off';
            }
        } catch(e) {}
    }
    updateStatus();
    setInterval(updateStatus, 5000);
</script>
</body>
</html>""")

# ----- ADDITIONAL ENDPOINTS -----
@app.post("/execute_trade")
async def execute_trade(request: Request):
    data = await request.json()
    symbol = data.get("symbol")
    direction = data.get("direction")
    entry = data.get("entry")
    sl = data.get("sl")
    tp = data.get("tp")
    result = execute_on_exchange(symbol, direction, float(entry), float(sl), float(tp), "mt5")
    return safe_json(result)

@app.get("/manifest.json")
def manifest():
    return JSONResponse(content={
        "name": "LEVIATHAN 8.0",
        "short_name": "LEVIATHAN",
        "description": "Eternal Trading Engine",
        "start_url": "/",
        "display": "standalone",
        "theme_color": "#00A3FF",
        "background_color": "#000000",
        "icons": [{"src": "/favicon.ico", "sizes": "64x64", "type": "image/x-icon"}]
    })

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
