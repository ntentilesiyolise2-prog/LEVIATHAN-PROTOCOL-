# ----- Feature Generator (AI Plugin Creator) -----
@router.post("/plugin/generate")
async def generate_plugin(request: Request):
    """
    Accept a description, generate a plugin using Gemini (or fallback),
    save it to plugins/, and load it dynamically.
    """
    data = await request.json()
    description = data.get("description", "")
    if not description:
        raise HTTPException(status_code=400, detail="Description is required")

    # If Gemini API key is available, use it to generate plugin code.
    if gemini_key:
        try:
            prompt = f"""
You are LEVIATHAN's plugin generator. Write a Python plugin that implements the following feature:
{description}

The plugin must have a function `register_plugin()` that returns a dict with:
- name: str
- version: str
- description: str
- author: str
- type: "strategy" | "indicator" | "execution" | "risk" | "utility"
- init: a callable that receives the engine and event_bus
- get_signal: optional callable that receives features and returns a vote (if strategy/indicator)
- on_tick: optional callable that runs every second
- on_trade: optional callable that runs after a trade

Provide ONLY the Python code, no explanations, no markdown.
"""
            response = gemini_model.generate_content(prompt)
            code = response.text
        except Exception as e:
            logger.error(f"Gemini generation failed: {e}")
            # Fallback: create a simple template
            code = generate_plugin_template(description)
    else:
        code = generate_plugin_template(description)

    # Save to plugins/ directory
    plugin_dir = Path("plugins")
    plugin_dir.mkdir(exist_ok=True)
    # Create a safe filename from description
    import re
    safe_name = re.sub(r'[^a-zA-Z0-9_]', '_', description[:30])
    filename = plugin_dir / f"{safe_name}.py"
    with open(filename, "w") as f:
        f.write(code)

    # Dynamically load the plugin
    engine = get_engine()
    pm = engine.get_plugin_manager()
    # Reload plugins
    pm.discover_plugins()
    return {"status": "generated", "file": str(filename), "code": code}

def generate_plugin_template(description: str) -> str:
    """Fallback template when Gemini is unavailable."""
    safe_name = description[:30].replace(" ", "_")
    return f'''
# leviathan/plugins/{safe_name}.py
def register_plugin():
    return {{
        "name": "{safe_name}",
        "version": "1.0",
        "description": "{description}",
        "author": "LEVIATHAN Auto-Generator",
        "type": "utility",
        "init": init_plugin,
    }}

def init_plugin(engine, event_bus):
    print(f"Plugin {safe_name} loaded.")
    # Add your custom logic here
    # You can access engine and event_bus
    return True
'''

# ----- UI Customisation -----
UI_CONFIG_FILE = "ui_config.json"

@router.get("/ui/config")
async def get_ui_config():
    if os.path.exists(UI_CONFIG_FILE):
        with open(UI_CONFIG_FILE, "r") as f:
            return json.load(f)
    return {"theme": "dark", "accent": "blue", "tab_order": ["dashboard", "signals", "trading", "journal", "backtest", "settings", "ai"], "hidden_tabs": []}

@router.post("/ui/config")
async def set_ui_config(request: Request):
    data = await request.json()
    with open(UI_CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=2)
    # Broadcast UI update via WebSocket
    engine = get_engine()
    await engine.event_bus.publish(Event(type="ui_update", data=data))
    return {"status": "updated"}
