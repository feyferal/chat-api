from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from starlette import status

from .db import Base, engine
from .routers.sessions import router as sessions_router
from .services.openai_client import (
    OpenAIServiceError,
    OpenAIAuthError,
    OpenAIRateLimitError,
    OpenAIUpstreamError,
)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Chat API")
app.include_router(sessions_router)


@app.exception_handler(OpenAIAuthError)
async def openai_auth_error_handler(request: Request, exc: OpenAIAuthError):
    return JSONResponse(
        status_code=status.HTTP_502_BAD_GATEWAY,
        content={"detail": str(exc)},
    )


@app.exception_handler(OpenAIRateLimitError)
async def openai_rate_limit_error_handler(request: Request, exc: OpenAIRateLimitError):
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={"detail": str(exc)},
    )


@app.exception_handler(OpenAIUpstreamError)
async def openai_upstream_error_handler(request: Request, exc: OpenAIUpstreamError):
    return JSONResponse(
        status_code=status.HTTP_502_BAD_GATEWAY,
        content={"detail": str(exc)},
    )


@app.exception_handler(OpenAIServiceError)
async def openai_service_error_handler(request: Request, exc: OpenAIServiceError):
    return JSONResponse(
        status_code=status.HTTP_502_BAD_GATEWAY,
        content={"detail": str(exc)},
    )


@app.get("/", include_in_schema=False)
def ui():
    path = Path(__file__).resolve().parent / "frontend" / "index.html"
    return FileResponse(path)
