from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, HttpUrl, field_validator


class StockStatus(str, Enum):
    healthy = "healthy"
    watch = "watch"
    low = "low"
    out = "out"


class ItemBase(BaseModel):
    name: str = Field(min_length=2, max_length=120, examples=["Wireless Barcode Scanner"])
    description: Optional[str] = Field(default=None, max_length=500)
    category: str = Field(default="General", min_length=2, max_length=80)
    unit_price: float = Field(default=0, ge=0)
    sku: str = Field(min_length=3, max_length=40, examples=["SCAN-EDGE-001"])
    image_url: Optional[HttpUrl] = None
    quantity_on_hand: int = Field(default=0, ge=0)
    reorder_level: int = Field(default=5, ge=0)
    monthly_sales_velocity: int = Field(default=0, ge=0)
    warehouse_zone: str = Field(default="A1", min_length=1, max_length=30)

    @field_validator("sku")
    @classmethod
    def normalize_sku(cls, value: str) -> str:
        return value.strip().upper()

    @field_validator("category", "warehouse_zone")
    @classmethod
    def normalize_label(cls, value: str) -> str:
        return value.strip()


class ItemCreate(ItemBase):
    pass


class ItemUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=120)
    description: Optional[str] = Field(default=None, max_length=500)
    category: Optional[str] = Field(default=None, min_length=2, max_length=80)
    unit_price: Optional[float] = Field(default=None, ge=0)
    sku: Optional[str] = Field(default=None, min_length=3, max_length=40)
    image_url: Optional[HttpUrl] = None
    quantity_on_hand: Optional[int] = Field(default=None, ge=0)
    reorder_level: Optional[int] = Field(default=None, ge=0)
    monthly_sales_velocity: Optional[int] = Field(default=None, ge=0)
    warehouse_zone: Optional[str] = Field(default=None, min_length=1, max_length=30)


class InventoryItem(ItemBase):
    id: int
    stock_status: StockStatus
    inventory_value: float
    created_at: datetime
    updated_at: datetime


class InventoryFilters(BaseModel):
    query: Optional[str] = None
    category: Optional[str] = None
    stock_status: Optional[StockStatus] = None
    min_price: Optional[float] = Field(default=None, ge=0)
    max_price: Optional[float] = Field(default=None, ge=0)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class ActivityEvent(BaseModel):
    id: int
    item_id: Optional[int] = None
    action: str
    message: str
    created_at: datetime


class CategoryInsight(BaseModel):
    category: str
    item_count: int
    total_units: int
    inventory_value: float
    low_stock_items: int


class ProductPerformance(BaseModel):
    item_id: int
    sku: str
    name: str
    category: str
    inventory_value: float
    monthly_sales_velocity: int
    turnover_score: float
    stock_risk: StockStatus


class LowStockPrediction(BaseModel):
    item_id: int
    sku: str
    name: str
    current_quantity: int
    reorder_level: int
    monthly_sales_velocity: int
    estimated_days_until_stockout: Optional[int]
    recommendation: str


class MonthlyInventoryReport(BaseModel):
    month: str
    total_items: int
    total_units: int
    inventory_value: float
    low_stock_count: int
    out_of_stock_count: int
    categories_tracked: int


class AnalyticsDashboard(BaseModel):
    total_items: int
    total_units: int
    inventory_value: float
    low_stock_count: int
    out_of_stock_count: int
    category_count: int
    top_categories: list[CategoryInsight]
    recent_activity: list[ActivityEvent]
