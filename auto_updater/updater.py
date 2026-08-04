# leviathan/auto_updater/updater.py
import subprocess, os
from pathlib import Path
from loguru import logger

class AutoUpdater:
    def __init__(self, repo_url: str = None):
        self.repo_url = repo_url; self.repo_dir = Path(".")
    def check_for_updates(self) -> bool:
        try:
            result = subprocess.run(["git", "fetch", "--dry-run"], capture_output=True, text=True, cwd=self.repo_dir)
            if "up to date" not in result.stdout: return True
            return False
        except Exception as e: logger.error(f"Update check failed: {e}"); return False
    def pull_updates(self) -> bool:
        try:
            subprocess.run(["git", "pull"], check=True, cwd=self.repo_dir)
            logger.info("Update pulled successfully"); return True
        except Exception as e: logger.error(f"Pull failed: {e}"); return False
    def restart_server(self):
        logger.info("Restarting server...")
        os._exit(0)
