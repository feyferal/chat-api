from __future__ import annotations

import os
from pathlib import Path
from pydantic import BaseModel
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[1]
ENV_PATH = BASE_DIR / ".env"

load_dotenv(dotenv_path=ENV_PATH)


class Settings(BaseModel):
    openai_api_key: str
    database_url: str
    default_model: str


settings = Settings(
    openai_api_key=os.getenv("OPENAI_API_KEY", ""),
    database_url=os.getenv("DATABASE_URL", "sqlite:///./app.db"),
    default_model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
)

print("ENV FILE:", ENV_PATH)
print("OPENAI_API_KEY loaded:", bool(settings.openai_api_key))
