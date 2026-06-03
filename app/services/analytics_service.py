from __future__ import annotations

from collections import defaultdict
from datetime import datetime

from app.models.schemas import (
    AnalyticsDashboard,
    CategoryInsight,
    InventoryFilters,
    InventoryItem,
    LowStockPrediction,
    MonthlyInventoryReport,
    ProductPerformance,
    StockStatus,
)
from app.services.inventory_service import InventoryRepository
from app.utils.stock import estimate_stockout_days


class InventoryIntelligenceService:
    def __init__(self, repository: InventoryRepository) -> None:
        self.repository = repository

    def dashboard(self) -> AnalyticsDashboard:
        items = self.repository.list(InventoryFilters())
        categories = self.category_insights(items)
        return AnalyticsDashboard(
            total_items=len(items),
            total_units=sum(item.quantity_on_hand for item in items),
            inventory_value=round(sum(item.inventory_value for item in items), 2),
            low_stock_count=sum(item.stock_status == StockStatus.low for item in items),
            out_of_stock_count=sum(item.stock_status == StockStatus.out for item in items),
            category_count=len(categories),
            top_categories=categories[:5],
            recent_activity=self.repository.activity(limit=8),
        )

    def category_insights(self, items: list[InventoryItem] | None = None) -> list[CategoryInsight]:
        items = items or self.repository.list(InventoryFilters())
        grouped: dict[str, list[InventoryItem]] = defaultdict(list)
        for item in items:
            grouped[item.category].append(item)

        insights = [
            CategoryInsight(
                category=category,
                item_count=len(category_items),
                total_units=sum(item.quantity_on_hand for item in category_items),
                inventory_value=round(sum(item.inventory_value for item in category_items), 2),
                low_stock_items=sum(item.stock_status in {StockStatus.low, StockStatus.out} for item in category_items),
            )
            for category, category_items in grouped.items()
        ]
        return sorted(insights, key=lambda insight: insight.inventory_value, reverse=True)

    def low_stock_predictions(self) -> list[LowStockPrediction]:
        predictions = []
        for item in self.repository.list(InventoryFilters()):
            if item.stock_status not in {StockStatus.low, StockStatus.out, StockStatus.watch}:
                continue
            days = estimate_stockout_days(item.quantity_on_hand, item.monthly_sales_velocity)
            if item.stock_status == StockStatus.out:
                recommendation = "Restock immediately; this item is already unavailable."
            elif days is None:
                recommendation = "Review demand manually; no sales velocity has been recorded yet."
            elif days <= 14:
                recommendation = "Create a replenishment order within the next week."
            else:
                recommendation = "Monitor closely and prepare a scheduled reorder."
            predictions.append(
                LowStockPrediction(
                    item_id=item.id,
                    sku=item.sku,
                    name=item.name,
                    current_quantity=item.quantity_on_hand,
                    reorder_level=item.reorder_level,
                    monthly_sales_velocity=item.monthly_sales_velocity,
                    estimated_days_until_stockout=days,
                    recommendation=recommendation,
                )
            )
        return sorted(predictions, key=lambda prediction: prediction.estimated_days_until_stockout or 0)

    def performance_metrics(self) -> list[ProductPerformance]:
        metrics = []
        for item in self.repository.list(InventoryFilters()):
            turnover_score = item.monthly_sales_velocity / max(item.quantity_on_hand, 1)
            metrics.append(
                ProductPerformance(
                    item_id=item.id,
                    sku=item.sku,
                    name=item.name,
                    category=item.category,
                    inventory_value=item.inventory_value,
                    monthly_sales_velocity=item.monthly_sales_velocity,
                    turnover_score=round(turnover_score, 2),
                    stock_risk=item.stock_status,
                )
            )
        return sorted(metrics, key=lambda metric: metric.turnover_score, reverse=True)

    def monthly_report(self, month: str | None = None) -> MonthlyInventoryReport:
        items = self.repository.list(InventoryFilters())
        report_month = month or datetime.utcnow().strftime("%Y-%m")
        return MonthlyInventoryReport(
            month=report_month,
            total_items=len(items),
            total_units=sum(item.quantity_on_hand for item in items),
            inventory_value=round(sum(item.inventory_value for item in items), 2),
            low_stock_count=sum(item.stock_status == StockStatus.low for item in items),
            out_of_stock_count=sum(item.stock_status == StockStatus.out for item in items),
            categories_tracked=len({item.category for item in items}),
        )
