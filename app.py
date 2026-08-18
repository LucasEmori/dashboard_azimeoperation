"""
FastAPI server para o dashboard React.
  GET /api/data   -> serve output/data.json rapidamente
  POST /api/sync  -> dispara atualizacao background (DW -> data.json)
  GET /api/status -> 'idle' ou 'syncing'
  GET /           -> serve build React (dist/)
"""
import os
import sys
import threading
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

BASE_DIR = Path(__file__).parent
DIST_DIR = BASE_DIR / "dist"
OUTPUT_DATA = BASE_DIR / "output" / "data.json"
FALLBACK_DATA = DIST_DIR / "data.json"
sys.path.insert(0, str(BASE_DIR))

sync_status = {"state": "idle", "error": None}
_sync_lock = threading.Lock()

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

app = FastAPI(title="Dashboard Alinare & Novitah", lifespan=lifespan)

def _run_pipeline_bg():
    with _sync_lock:
        sync_status["state"] = "syncing"
        sync_status["error"] = None
    try:
        from src import pipeline
        pipeline.run()
        with _sync_lock:
            sync_status["state"] = "idle"
    except Exception as e:
        with _sync_lock:
            sync_status["state"] = "idle"
            sync_status["error"] = str(e)


@app.get("/api/data")
def api_data():
    """Retorna JSON local, sem bloquear com o DW."""
    data_path = OUTPUT_DATA if OUTPUT_DATA.exists() else FALLBACK_DATA
    if data_path.exists():
        return FileResponse(data_path, headers={"Access-Control-Allow-Origin": "*"})
    return JSONResponse({"error": "Dados não disponíveis"}, status_code=404)


@app.post("/api/sync")
def api_sync():
    """Inicia ingestão em background."""
    with _sync_lock:
        if sync_status["state"] == "syncing":
            return JSONResponse({"status": "already syncing"})
    threading.Thread(target=_run_pipeline_bg, daemon=True).start()
    return JSONResponse({"status": "started"})


@app.get("/api/status")
def api_status():
    with _sync_lock:
        return JSONResponse(sync_status)


# Static frontend (SPA fallback)
@app.get("/")
def index():
    return FileResponse(DIST_DIR / "index.html")


@app.get("/assets/{rest:path}")
def assets(rest: str):
    return FileResponse(DIST_DIR / "assets" / rest)


@app.get("/{path:path}")
def spa(path: str):
    f = DIST_DIR / path
    if path and f.is_file():
        return FileResponse(f)
    if path.startswith("data.json"):
        return FileResponse(DIST_DIR / "data.json")
    return FileResponse(DIST_DIR / "index.html")


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8501))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=False)