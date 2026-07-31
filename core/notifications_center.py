# leviathan/core/notification_center.py
import json
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from loguru import logger

class NotificationCenter:
    def __init__(self, storage_path: str = "notifications.json", max_stored: int = 1000):
        self.storage_path = Path(storage_path)
        self.max_stored = max_stored
        self.notifications: List[Dict[str, Any]] = []
        self._load()

    def _load(self):
        if self.storage_path.exists():
            try:
                with open(self.storage_path, "r") as f:
                    self.notifications = json.load(f)
            except:
                self.notifications = []
        else:
            self.notifications = []

    def _save(self):
        try:
            with open(self.storage_path, "w") as f:
                json.dump(self.notifications[:self.max_stored], f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save notifications: {e}")

    def add(self, notification: Dict[str, Any]) -> Dict[str, Any]:
        """Add a notification and return it with an id and timestamp."""
        notification["id"] = str(int(time.time() * 1000)) + "_" + notification.get("type", "general")
        notification["timestamp"] = datetime.utcnow().isoformat()
        notification["read"] = False
        self.notifications.insert(0, notification)
        if len(self.notifications) > self.max_stored:
            self.notifications = self.notifications[:self.max_stored]
        self._save()
        return notification

    def get_all(self, limit: int = 100) -> List[Dict[str, Any]]:
        return self.notifications[:limit]

    def get_unread(self) -> List[Dict[str, Any]]:
        return [n for n in self.notifications if not n.get("read", False)]

    def get_latest(self, n: int = 10) -> List[Dict[str, Any]]:
        return self.notifications[:n]

    def mark_read(self, notification_id: str):
        for n in self.notifications:
            if n.get("id") == notification_id:
                n["read"] = True
                break
        self._save()

    def mark_all_read(self):
        for n in self.notifications:
            n["read"] = True
        self._save()

    def clear_read(self):
        self.notifications = [n for n in self.notifications if not n.get("read", False)]
        self._save()

    def count_unread(self) -> int:
        return len(self.get_unread())
