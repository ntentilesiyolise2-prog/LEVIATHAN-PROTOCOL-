# leviathan/predictive/onchain.py
from typing import Dict, Any

class OnChainData:
    def get_data(self, symbol: str) -> Dict[str, Any]:
        return {'whale_flow': 0, 'exchange_inflow': 0, 'funding_rate': 0}
