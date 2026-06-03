from __future__ import annotations

from datetime import datetime
from typing import Annotated
from typing import Optional

from fastapi import APIRouter, Query, Response

from app.models.schemas import InventoryFilters, InventoryItem, ItemCreate, ItemUpdate, StockStatus
from app.services.analytics_service import InventoryIntelligenceService
from app.services.export_service import inventory_to_csv, inventory_to_pdf_bytes
from app.services.inventory_service import inventory_repository

router = APIRouter()
legacy_router = APIRouter(tags=["Legacy product compatibility"])
intelligence = InventoryIntelligenceService(inventory_repository)


def build_filters(
    query: Annotated[Optional[str], Query(description="Search name, SKU, or description.")] = None,
    category: Optional[str] = None,
    stock_status: Optional[StockStatus] = None,
    min_price: Optional[float] = Query(default=None, ge=0),
    max_price: Optional[float] = Query(default=None, ge=0),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
) -> InventoryFilters:
    return InventoryFilters(
        query=query,
        category=category,
        stock_status=stock_status,
        min_price=min_price,
        max_price=max_price,
        start_date=start_date,
        end_date=end_date,
    )


@router.get("/health", tags=["Platform"])
async def health_check() -> dict[str, str]:
    return {"status": "ready", "service": "InventEdge"}


@router.get("/inventory/items", response_model=list[InventoryItem], tags=["Inventory"])
async def list_inventory_items(
    query: Optional[str] = Query(default=None, description="Search name, SKU, or description."),
    category: Optional[str] = None,
    stock_status: Optional[StockStatus] = None,
    min_price: Optional[float] = Query(default=None, ge=0),
    max_price: Optional[float] = Query(default=None, ge=0),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
):
    filters = build_filters(query, category, stock_status, min_price, max_price, start_date, end_date)
    return inventory_repository.list(filters)


@router.post("/inventory/items", response_model=InventoryItem, tags=["Inventory"])
async def create_inventory_item(payload: ItemCreate):
    return inventory_repository.create(payload)


@router.get("/inventory/items/{item_id}", response_model=InventoryItem, tags=["Inventory"])
async def get_inventory_item(item_id: int):
    return inventory_repository.get(item_id)


@router.put("/inventory/items/{item_id}", response_model=InventoryItem, tags=["Inventory"])
async def update_inventory_item(item_id: int, payload: ItemUpdate):
    return inventory_repository.update(item_id, payload)


@router.delete("/inventory/items/{item_id}", response_model=InventoryItem, tags=["Inventory"])
async def delete_inventory_item(item_id: int):
    return inventory_repository.delete(item_id)


@router.get("/analytics/dashboard", tags=["Inventory Intelligence"])
async def inventory_analytics_dashboard():
    return intelligence.dashboard()


@router.get("/analytics/low-stock-predictions", tags=["Inventory Intelligence"])
async def low_stock_predictions():
    return intelligence.low_stock_predictions()


@router.get("/analytics/category-insights", tags=["Inventory Intelligence"])
async def category_insights():
    return intelligence.category_insights()


@router.get("/analytics/monthly-report", tags=["Inventory Intelligence"])
async def monthly_inventory_report(month: Optional[str] = Query(default=None, pattern=r"^\d{4}-\d{2}$")):
    return intelligence.monthly_report(month)


@router.get("/analytics/activity-timeline", tags=["Inventory Intelligence"])
async def activity_timeline(limit: int = Query(default=20, ge=1, le=100)):
    return inventory_repository.activity(limit)


@router.get("/analytics/product-performance", tags=["Inventory Intelligence"])
async def product_performance_metrics():
    return intelligence.performance_metrics()


@router.get("/exports/inventory.csv", tags=["Exports"])
async def export_inventory_csv():
    csv_body = inventory_to_csv(inventory_repository.list(InventoryFilters()))
    return Response(
        content=csv_body,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=inventedge-inventory.csv"},
    )


@router.get("/exports/inventory.pdf", tags=["Exports"])
async def export_inventory_pdf():
    pdf_body = inventory_to_pdf_bytes(inventory_repository.list(InventoryFilters()))
    return Response(
        content=pdf_body,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=inventedge-inventory.pdf"},
    )


@legacy_router.get("/products/", response_model=list[InventoryItem])
async def legacy_list_products(
    query: Optional[str] = None,
    category: Optional[str] = None,
    stock_status: Optional[StockStatus] = None,
    min_price: Optional[float] = Query(default=None, ge=0),
    max_price: Optional[float] = Query(default=None, ge=0),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
):
    filters = build_filters(query, category, stock_status, min_price, max_price, start_date, end_date)
    return inventory_repository.list(filters)


@legacy_router.post("/products/", response_model=InventoryItem)
async def legacy_create_product(payload: ItemCreate):
    return inventory_repository.create(payload)


@legacy_router.get("/products/{product_id}", response_model=InventoryItem)
async def legacy_read_product(product_id: int):
    return inventory_repository.get(product_id)


@legacy_router.put("/products/{product_id}", response_model=InventoryItem)
async def legacy_update_product(product_id: int, payload: ItemUpdate):
    return inventory_repository.update(product_id, payload)


@legacy_router.delete("/products/{product_id}", response_model=InventoryItem)
async def legacy_delete_product(product_id: int):
    return inventory_repository.delete(product_id)
