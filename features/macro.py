# leviathan/features/macro.py
import yfinance as yf
import time
from typing import Dict, Any
from loguru import logger

class MacroData:
    def __init__(self):
        self.cache = {}
        self.last_update = None
    async def compute(self) -> Dict[str, Any]:
        if self.last_update and time.time() - self.last_update < 300:
            return self.cache
        macro = {}
        try:
            dxy = yf.Ticker("DX-Y.NYB").history(period="1d", interval="5m")
            if not dxy.empty:
                macro["dxy"] = float(dxy['Close'].iloc[-1])
                macro["dxy_change"] = float((dxy['Close'].iloc[-1] - dxy['Close'].iloc[0]) / dxy['Close'].iloc[0] * 100)
            vix = yf.Ticker("^VIX").history(period="1d", interval="5m")
            if not vix.empty:
                macro["vix"] = float(vix['Close'].iloc[-1])
                macro["vix_change"] = float((vix['Close'].iloc[-1] - vix['Close'].iloc[0]) / vix['Close'].iloc[0] * 100)
            gold = yf.Ticker("GC=F").history(period="1d", interval="5m")
            if not gold.empty:
                macro["gold"] = float(gold['Close'].iloc[-1])
                macro["gold_change"] = float((gold['Close'].iloc[-1] - gold['Close'].iloc[0]) / gold['Close'].iloc[0] * 100)
            oil = yf.Ticker("CL=F").history(period="1d", interval="5m")
            if not oil.empty:
                macro["oil"] = float(oil['Close'].iloc[-1])
                macro["oil_change"] = float((oil['Close'].iloc[-1] - oil['Close'].iloc[0]) / oil['Close'].iloc[0] * 100)
            spx = yf.Ticker("^GSPC").history(period="1d", interval="5m")
            if not spx.empty:
                macro["spx"] = float(spx['Close'].iloc[-1])
                macro["spx_change"] = float((spx['Close'].iloc[-1] - spx['Close'].iloc[0]) / spx['Close'].iloc[0] * 100)
            btc = yf.Ticker("BTC-USD").history(period="1d", interval="5m")
            if not btc.empty:
                macro["btc"] = float(btc['Close'].iloc[-1])
                macro["btc_change"] = float((btc['Close'].iloc[-1] - btc['Close'].iloc[0]) / btc['Close'].iloc[0] * 100)
            macro["risk_on"] = macro.get("vix", 20) < 18 and macro.get("dxy", 100) < 105
            self.cache = macro
            self.last_update = time.time()
        except Exception as e:
            logger.warning(f"Macro fetch failed: {e}")
            if self.cache: return self.cache
            macro = {"dxy":0,"vix":0,"gold":0,"oil":0,"spx":0,"btc":0,"risk_on": False}
        return macro
