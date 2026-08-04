# leviathan/plugin_manager/loader.py
import importlib.util
from pathlib import Path

def load_plugin(plugin_path: str):
    module_name = Path(plugin_path).stem
    spec = importlib.util.spec_from_file_location(module_name, plugin_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
