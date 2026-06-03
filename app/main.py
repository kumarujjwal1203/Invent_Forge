from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import legacy_router, router
from app.core.config import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    application = FastAPI(
        title=settings.api_title,
        version=settings.api_version,
        redoc_url="/redoc",
        description=(
            "InventEdge is a smart inventory management platform designed to help businesses track stock, "
            "monitor product movement, analyze inventory trends, and optimize warehouse operations through "
            "data-driven insights."
        ),
        contact={"name": "InventEdge Portfolio Project"},
        openapi_tags=[
            {"name": "Platform", "description": "Service health and project identity."},
            {"name": "Inventory", "description": "Inventory item lifecycle and advanced filtering."},
            {"name": "Inventory Intelligence", "description": "Analytics, reports, predictions, and timeline data."},
            {"name": "Exports", "description": "CSV and PDF inventory exports."},
        ],
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.include_router(router, prefix=settings.api_prefix)
    application.include_router(legacy_router)
    return application


app = create_app()


@app.get("/", tags=["Platform"])
async def home() -> dict[str, str]:
    return {
        "project": "InventEdge",
        "tagline": "Smart Inventory Intelligence",
        "docs": "/docs",
        "api": "/api/v1",
    }
