# leviathan/data/cache.py
import time
from typing import Dict, Any, Optional
from collections import defaultdict
from loguru import logger

class Cache:
    """In-memory TTL cache. No external dependencies."""

    def __init__(self, default_ttl: int = 5):
        self.default_ttl = default_ttl
        self._data: Dict[str, Dict[str, Any]] = defaultdict(dict)
        self._expiry: Dict[str, Dict[str, float]] = defaultdict(dict)

    def get(self, key: str, subkey: str = "default") -> Optional[Any]:
        """Retrieve cached value if not expired."""
        if key in self._expiry and subkey in self._expiry[key]:
            if time.time() < self._expiry[key][subkey]:
                return self._data[key].get(subkey)
            else:
                # expired
                self._data[key].pop(subkey, None)
                self._expiry[key].pop(subkey, None)
                if not self._data[key]:
                    self._data.pop(key, None)
                    self._expiry.pop(key, None)
        return None

    def set(self, key: str, value: Any, subkey: str = "default", ttl: Optional[int] = None):
        """Store value with TTL (seconds)."""
        if ttl is None:
            ttl = self.default_ttl
        self._data[key][subkey] = value
        self._expiry[key][subkey] = time.time() + ttl

    def clear(self, key: Optional[str] = None, subkey: Optional[str] = None):
        """Clear cache entries."""
        if key is None:
            self._data.clear()
            self._expiry.clear()
        elif subkey is None:
            self._data.pop(key, None)
            self._expiry.pop(key, None)
        else:
            self._data.get(key, {}).pop(subkey, None)
            self._expiry.get(key, {}).pop(subkey, None)
