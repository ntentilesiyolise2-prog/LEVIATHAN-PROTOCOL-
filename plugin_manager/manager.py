# leviathan/plugin_manager/manager.py
import importlib, sys
from pathlib import Path
from typing import Dict, Any, List, Optional
from loguru import logger

class PluginManager:
    def __init__(self, plugin_dir: str = "plugins"):
        self.plugin_dir = Path(plugin_dir); self.plugin_dir.mkdir(exist_ok=True); self.plugins: Dict[str, Any] = {}; self._loaded = False
    def discover_plugins(self):
        if not self.plugin_dir.exists(): return
        sys.path.insert(0, str(self.plugin_dir.parent))
        for item in self.plugin_dir.iterdir():
            if item.is_dir() and (item / "__init__.py").exists():
                module_name = f"plugins.{item.name}"
                try:
                    module = importlib.import_module(module_name)
                    if hasattr(module, "register_plugin"):
                        plugin_info = module.register_plugin()
                        self.plugins[plugin_info.get("name", item.name)] = {"module": module, "info": plugin_info, "enabled": True}
                        logger.info(f"Loaded plugin: {plugin_info.get('name', item.name)}")
                except Exception as e: logger.error(f"Failed to load plugin {item.name}: {e}")
        self._loaded = True
    def get_plugin(self, name: str): return self.plugins.get(name)
    def enable_plugin(self, name: str):
        if name in self.plugins: self.plugins[name]["enabled"] = True
    def disable_plugin(self, name: str):
        if name in self.plugins: self.plugins[name]["enabled"] = False
    def list_plugins(self) -> List[Dict[str, Any]]:
        return [{"name": k, "info": v["info"], "enabled": v["enabled"]} for k,v in self.plugins.items()]
