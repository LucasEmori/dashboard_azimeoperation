"""
FastAPI server para o dashboard React.
  GET /api/data?month=YYYY-MM  -> roda pipeline no DW ao vivo (sem JSON intermediario)
  GET /api/months              -> lista meses disponiveis no DW
  GET /                        -> serve build React (dist/)
"""
import os
import sys
import threading
from contextlib import asynccontextmanager
from datetime import date, datetime
from pathlib import Path

from fastapi import FastAPI, Query
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

BASE_DIR = Path(__file__).parent
DIST_DIR = BASE_DIR / "dist"
sys.path.insert(0, str(BASE_DIR))

# lock de unico processamento por vez (pipeline muta config module-level)
_pipeline_lock = threading.Lock()

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

app = FastAPI(title="Dashboard Alinare & Novitah", lifespan=lifespan)


@app.get("/api/months")
def api_months():
    """Lista os últimos meses com dado no DW (2024-01..hoje)."""
    from src import config
    today = config.TODAY
    months = []
    for y in range(today.year - 2, today.year + 1):
        for m in range(1, 13):
            if date(y, m, 1) < date(today.year, today.month, 1):
                months.append(date(y, m, 1).isoformat())
            elif date(y, m, 1) == date(today.year, today.month, 1):
                months.append(date(y, m, 1).isoformat())
                break
        else:
            continue
        if date(y, m, 1) >= date(today.year, today.month, 1):
            break
    # ordena mais recente primeiro
    return JSONResponse({"months": sorted(set(months), reverse=True)})


@app.get("/api/data")
def api_data(month: str = Query(..., description="Mês alvo YYYY-MM")):
    """Roda pipeline completo para o mês alvo e devolve JSON vivo."""
    try:
        target = datetime.strptime(month, "%Y-%m").date()
    except ValueError:
        return JSONResponse({"error": "mês deve ser YYYY-MM"}, status_code=400)

    with _pipeline_lock:
        try:
            from src import config
            config.set_destaque(target)
            from src import pipeline
            data = pipeline.run()  # usa config já setado
            return JSONResponse(data)
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=500)


# Static frontend (SPA fallback)
@app.get("/")
def index():
    return FileResponse(DIST_DIR / "index.html")


@app.get("/assets/{rest:path}")
def assets(rest: str):
    return FileResponse(DIST_DIR / "assets" / rest)


@app.get("/{path:path}")
def spa(path: str):
    # data.json/logos servidos do dist; resto -> index.html (SPA)
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