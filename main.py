# leviathan/main.py
import asyncio
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pathlib import Path

from core import Engine
from api import router, websocket_endpoint
from api.routes import set_engine

async def startup():
    engine = Engine()
    await engine.start()
    return engine

def create_app(engine: Engine) -> FastAPI:
    app = FastAPI(title="LEVIATHAN 21.0", version="21.0.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    set_engine(engine)
    app.include_router(router)
    app.add_websocket_route("/ws", websocket_endpoint)
    frontend_path = Path("frontend/index.html")
    if frontend_path.exists():
        @app.get("/", include_in_schema=False)
        async def serve_frontend():
            with open(frontend_path, "r") as f:
                return HTMLResponse(f.read())
    return app

if __name__ == "__main__":
    engine = asyncio.run(startup())
    app = create_app(engine)
    uvicorn.run(app, host=engine.settings.HOST, port=engine.settings.PORT)
