# leviathan/feature_requests/manager.py
import json
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
from loguru import logger

class FeatureRequestManager:
    def __init__(self, storage_path: str = "feature_requests.json"):
        self.storage_path = Path(storage_path); self.requests = []; self._load()
    def _load(self):
        if self.storage_path.exists():
            try:
                with open(self.storage_path, "r") as f: self.requests = json.load(f)
            except: self.requests = []
        else: self.requests = []
    def _save(self):
        with open(self.storage_path, "w") as f: json.dump(self.requests, f, indent=2)
    def add_request(self, description: str, requester: str = "user") -> Dict[str, Any]:
        req = {"id": str(len(self.requests)+1), "description": description, "requester": requester, "status": "pending", "created_at": datetime.utcnow().isoformat(), "updated_at": datetime.utcnow().isoformat()}
        self.requests.append(req); self._save(); logger.info(f"Feature request added: {description}"); return req
    def update_status(self, request_id: str, status: str):
        for req in self.requests:
            if req["id"] == request_id:
                req["status"] = status; req["updated_at"] = datetime.utcnow().isoformat(); self._save(); return True
        return False
    def list_requests(self, status: str = None) -> List[Dict[str, Any]]:
        if status: return [r for r in self.requests if r["status"] == status]
        return self.requests
