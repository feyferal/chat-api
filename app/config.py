from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, Field

PROJECT_ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = PROJECT_ROOT / ".env"

load_dotenv(dotenv_path=ENV_PATH)


class Settings(BaseModel):
    openai_api_key: str = Field(min_length=1)
    database_url: str = "sqlite:///./app.db"
    default_model: str = "gpt-4o-mini"

    context_limit: int = 30
    system_prompt: str = "You are a helpful assistant."


settings = Settings(
    openai_api_key=os.getenv("OPENAI_API_KEY", "") or "",
    database_url=os.getenv("DATABASE_URL", "sqlite:///./app.db") or "sqlite:///./app.db",
    default_model=os.getenv("OPENAI_MODEL", "gpt-4o-mini") or "gpt-4o-mini",
    context_limit=int(os.getenv("CONTEXT_LIMIT", "30") or "30"),
    system_prompt=os.getenv("SYSTEM_PROMPT", "You are a helpful assistant.") or "You are a helpful assistant.",
)
