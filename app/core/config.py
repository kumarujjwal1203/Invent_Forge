from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache


@dataclass(frozen=True)
class InventEdgeSettings:
    app_name: str = "InventEdge"
    api_title: str = "InventEdge API"
    api_version: str = "2.0.0"
    api_prefix: str = "/api/v1"
    tagline: str = "Smart Inventory Intelligence"
    database_url: str = "file:inventedge.db"


@lru_cache
def get_settings() -> InventEdgeSettings:
    return InventEdgeSettings(
        database_url=os.getenv("INVENTEDGE_DATABASE_URL", "file:inventedge.db"),
    )
