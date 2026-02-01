from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv


DEFAULT_ENV_PATHS = [
    Path(__file__).resolve().parents[1] / ".env",
    Path(__file__).resolve().parent / ".env",
]


def load_env() -> None:
    for path in DEFAULT_ENV_PATHS:
        if path.exists():
            load_dotenv(path)
            return
    load_dotenv()


def require_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing {name}. Add it to a .env file or export it in your shell.")
    return value
