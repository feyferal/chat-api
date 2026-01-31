from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse

from .db import Base, engine
from .routers.sessions import router as sessions_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Chat API")
app.include_router(sessions_router)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Chat API")
app.include_router(sessions_router)

@app.get("/", include_in_schema=False)
def ui():
    path = Path(__file__).resolve().parent / "frontend" / "index.html"
    return FileResponse(path)
