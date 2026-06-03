from __future__ import annotations

from datetime import datetime, timezone
from typing import Iterable

from fastapi import HTTPException, status

from app.models.schemas import ActivityEvent, InventoryFilters, InventoryItem, ItemCreate, ItemUpdate
from app.utils.stock import resolve_stock_status


class InventoryRepository:
    def __init__(self) -> None:
        self._items: dict[int, InventoryItem] = {}
        self._activity: list[ActivityEvent] = []
        self._next_item_id = 1
        self._next_event_id = 1
        self.seed_demo_inventory()

    def seed_demo_inventory(self) -> None:
        if self._items:
            return

        seed_items = [
            ItemCreate(
                name="Wireless Barcode Scanner",
                description="Bluetooth scanner for receiving and dispatch desks.",
                category="Warehouse Tech",
                unit_price=89.99,
                sku="SCAN-EDGE-001",
                quantity_on_hand=18,
                reorder_level=8,
                monthly_sales_velocity=14,
                warehouse_zone="A1",
            ),
            ItemCreate(
                name="Thermal Label Roll",
                description="High-volume labels for shelf and package tagging.",
                category="Packaging",
                unit_price=12.5,
                sku="LBL-EDGE-220",
                quantity_on_hand=4,
                reorder_level=12,
                monthly_sales_velocity=38,
                warehouse_zone="B2",
            ),
            ItemCreate(
                name="RFID Pallet Tag",
                description="Reusable RFID tags for pallet-level visibility.",
                category="Tracking",
                unit_price=3.75,
                sku="RFID-EDGE-114",
                quantity_on_hand=0,
                reorder_level=25,
                monthly_sales_velocity=42,
                warehouse_zone="C1",
            ),
            ItemCreate(
                name="Inventory Tablet Dock",
                description="Charging dock for aisle inventory tablets.",
                category="Warehouse Tech",
                unit_price=54.0,
                sku="DOCK-EDGE-010",
                quantity_on_hand=31,
                reorder_level=10,
                monthly_sales_velocity=6,
                warehouse_zone="A3",
            ),
        ]

        for item in seed_items:
            self.create(item, "seed")

    def list(self, filters: InventoryFilters) -> list[InventoryItem]:
        items = list(self._items.values())
        return sorted(self._apply_filters(items, filters), key=lambda item: item.name.lower())

    def create(self, payload: ItemCreate, actor: str = "api") -> InventoryItem:
        if self._sku_exists(payload.sku):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"code": "SKU_ALREADY_EXISTS", "message": f"SKU {payload.sku} is already tracked."},
            )

        now = self._now()
        item = InventoryItem(
            id=self._next_item_id,
            **payload.model_dump(),
            stock_status=resolve_stock_status(payload.quantity_on_hand, payload.reorder_level),
            inventory_value=round(payload.quantity_on_hand * payload.unit_price, 2),
            created_at=now,
            updated_at=now,
        )
        self._items[item.id] = item
        self._next_item_id += 1
        self._record_activity(item.id, "created", f"{actor} added {item.name} to InventEdge.")
        return item

    def get(self, item_id: int) -> InventoryItem:
        item = self._items.get(item_id)
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "ITEM_NOT_FOUND", "message": f"No inventory item exists for id {item_id}."},
            )
        return item

    def update(self, item_id: int, payload: ItemUpdate) -> InventoryItem:
        existing = self.get(item_id)
        updates = payload.model_dump(exclude_unset=True)
        if "sku" in updates and updates["sku"] != existing.sku and self._sku_exists(updates["sku"]):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"code": "SKU_ALREADY_EXISTS", "message": f"SKU {updates['sku']} is already tracked."},
            )

        merged = existing.model_dump()
        merged.update(updates)
        merged["updated_at"] = self._now()
        merged["stock_status"] = resolve_stock_status(merged["quantity_on_hand"], merged["reorder_level"])
        merged["inventory_value"] = round(merged["quantity_on_hand"] * merged["unit_price"], 2)
        item = InventoryItem(**merged)
        self._items[item_id] = item
        self._record_activity(item.id, "updated", f"{item.name} was updated with fresh inventory data.")
        return item

    def delete(self, item_id: int) -> InventoryItem:
        item = self.get(item_id)
        del self._items[item_id]
        self._record_activity(item.id, "deleted", f"{item.name} was removed from active inventory.")
        return item

    def activity(self, limit: int = 20) -> list[ActivityEvent]:
        return list(reversed(self._activity))[:limit]

    def _sku_exists(self, sku: str) -> bool:
        return any(item.sku == sku for item in self._items.values())

    def _record_activity(self, item_id: int | None, action: str, message: str) -> None:
        self._activity.append(
            ActivityEvent(
                id=self._next_event_id,
                item_id=item_id,
                action=action,
                message=message,
                created_at=self._now(),
            )
        )
        self._next_event_id += 1

    @staticmethod
    def _apply_filters(items: Iterable[InventoryItem], filters: InventoryFilters) -> list[InventoryItem]:
        results = list(items)
        if filters.query:
            query = filters.query.lower()
            results = [
                item
                for item in results
                if query in item.name.lower() or query in item.sku.lower() or query in (item.description or "").lower()
            ]
        if filters.category:
            results = [item for item in results if item.category.lower() == filters.category.lower()]
        if filters.stock_status:
            results = [item for item in results if item.stock_status == filters.stock_status]
        if filters.min_price is not None:
            results = [item for item in results if item.unit_price >= filters.min_price]
        if filters.max_price is not None:
            results = [item for item in results if item.unit_price <= filters.max_price]
        if filters.start_date:
            results = [item for item in results if item.created_at >= filters.start_date]
        if filters.end_date:
            results = [item for item in results if item.created_at <= filters.end_date]
        return results

    @staticmethod
    def _now() -> datetime:
        return datetime.now(timezone.utc)


inventory_repository = InventoryRepository()
