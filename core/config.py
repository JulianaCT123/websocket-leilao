import os
from dataclasses import dataclass, field

@dataclass(frozen=True)
class Config:
    PORT: int = int(os.environ.get("PORT", "8888"))
    LISTEN_ADDRESS: str = "0.0.0.0"
    STATIC_PATH: str = os.path.join(os.path.dirname(__file__), "..", "client", "static")
    DEFAULT_PAGE: str = "index.html"

config = Config()