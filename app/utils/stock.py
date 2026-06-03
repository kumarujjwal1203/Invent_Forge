from __future__ import annotations

from app.models.schemas import StockStatus


def resolve_stock_status(quantity_on_hand: int, reorder_level: int) -> StockStatus:
    if quantity_on_hand == 0:
        return StockStatus.out
    if quantity_on_hand <= reorder_level:
        return StockStatus.low
    if quantity_on_hand <= reorder_level * 2:
        return StockStatus.watch
    return StockStatus.healthy


def estimate_stockout_days(quantity_on_hand: int, monthly_sales_velocity: int) -> int | None:
    if monthly_sales_velocity <= 0:
        return None
    daily_velocity = monthly_sales_velocity / 30
    return max(0, round(quantity_on_hand / daily_velocity))
