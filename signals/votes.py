# leviathan/signals/votes.py
from dataclasses import dataclass

@dataclass
class Vote:
    source: str
    direction: str
    confidence: float
    reason: str
    weight: float = 1.0
