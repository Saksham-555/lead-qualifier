import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    api_key: str
    base_url: Optional[str] = None
    model: str = "claude-haiku-5-5"
    timeout_seconds: float = 30.0

    def __repr__(self) -> str:  # never expose the key
        return f"Settings(model={self.model!r}, base_url={self.base_url!r})"


def load_settings() -> Settings:
    load_dotenv()
    key = os.getenv("LQ_API_KEY")
    if not key:
        raise RuntimeError("LQ_API_KEY is required")
    return Settings(
        api_key=key,
        base_url=os.getenv("LQ_BASE_URL") or None,
        model=os.getenv("LQ_MODEL") or "claude-haiku-5-5",
        timeout_seconds=float(os.getenv("LQ_TIMEOUT_SECONDS") or 30),
    )
