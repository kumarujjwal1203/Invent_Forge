# InventEdge

**Smart Inventory Intelligence**

InventEdge is a smart inventory management platform designed to help businesses track stock, monitor product movement, analyze inventory trends, and optimize warehouse operations through data-driven insights.

## Project Identity

- **Project name:** InventEdge
- **Tagline:** Smart Inventory Intelligence
- **Positioning:** A portfolio-ready inventory intelligence API with analytics, predictions, reporting, filtering, and export workflows.
- **Logo concept:** A sharp warehouse-edge mark combining a stacked box, upward analytics line, and subtle circuit node to communicate stock control plus intelligence.
- **Color scheme:** Graphite `#111827`, cloud `#F8FAFC`, signal teal `#14B8A6`, insight blue `#2563EB`, amber alert `#F59E0B`, critical rose `#E11D48`.
- **Dashboard design direction:** Dense operational layout with KPI strips, category insight tables, risk-focused low-stock panels, activity timeline, and export actions.

## Rebrand Scan

The original repository was scanned for legacy names and positioning before changes were made. Old branding appeared in:

- `README.md`: title, overview, endpoint descriptions, and architecture notes.
- `main.py`: API title, API description, comments, product queue naming, and CRUD-only structure.

The updated code replaces the old identity with InventEdge naming, documentation, route organization, schema naming, and API descriptions.

## New Folder Structure

```text
InventEdge/
├── app/
│   ├── api/
│   │   └── routes.py
│   ├── core/
│   │   └── config.py
│   ├── models/
│   │   └── schemas.py
│   ├── services/
│   │   ├── analytics_service.py
│   │   ├── export_service.py
│   │   └── inventory_service.py
│   ├── utils/
│   │   └── stock.py
│   └── main.py
├── tests/
│   └── test_main.py
├── main.py
├── schema.prisma
├── Dockerfile
├── docker-compose.yaml
├── makefile
├── requirements.txt
└── README.md
```

## File-Wise Changes

| File | What changed |
| --- | --- |
| `app/main.py` | New branded FastAPI app factory, OpenAPI metadata, CORS setup, and `/api/v1` routing. |
| `app/api/routes.py` | New inventory, analytics, reporting, timeline, export, and compatibility routes. |
| `app/core/config.py` | InventEdge settings with `INVENTEDGE_DATABASE_URL`. |
| `app/models/schemas.py` | Modern Pydantic models for items, filters, analytics, predictions, reports, activity, and performance metrics. |
| `app/services/inventory_service.py` | Central inventory repository, demo data, validation, duplicate SKU handling, filtering, and activity logging. |
| `app/services/analytics_service.py` | Dashboard metrics, low-stock prediction, category insights, monthly reports, and product performance scoring. |
| `app/services/export_service.py` | CSV and lightweight PDF export helpers. |
| `app/utils/stock.py` | Reusable stock status and stockout estimation utilities. |
| `main.py` | Thin compatibility entrypoint that exposes `app.main:app`. |
| `schema.prisma` | Renamed database model to `InventoryItem`, added activity table, richer inventory fields, and InventEdge database env var. |
| `tests/test_main.py` | Rewritten tests for InventEdge identity, inventory creation, filters, analytics, prediction, and CSV export. |
| `requirements.txt` | Removed duplicate and unused packages; added `pytest`. |
| `Dockerfile` | Uses the new `app.main:app` entrypoint. |
| `docker-compose.yaml` | Renamed service to `inventedge-api` and added `INVENTEDGE_DATABASE_URL`. |
| `makefile` | Updated dev command and added a test target. |

## API Highlights

### Platform

- `GET /` returns the InventEdge identity and docs links.
- `GET /api/v1/health` checks service readiness.

### Inventory

- `GET /api/v1/inventory/items`
- `POST /api/v1/inventory/items`
- `GET /api/v1/inventory/items/{item_id}`
- `PUT /api/v1/inventory/items/{item_id}`
- `DELETE /api/v1/inventory/items/{item_id}`

Search and advanced filters are available through query parameters:

```text
query=label
category=Packaging
stock_status=low
min_price=5
max_price=100
start_date=2026-01-01T00:00:00Z
end_date=2026-12-31T23:59:59Z
```

### Inventory Intelligence

- `GET /api/v1/analytics/dashboard`
- `GET /api/v1/analytics/low-stock-predictions`
- `GET /api/v1/analytics/category-insights`
- `GET /api/v1/analytics/monthly-report?month=2026-06`
- `GET /api/v1/analytics/activity-timeline`
- `GET /api/v1/analytics/product-performance`

### Exports

- `GET /api/v1/exports/inventory.csv`
- `GET /api/v1/exports/inventory.pdf`

Legacy `/products/` routes are still available as compatibility aliases, but new work should use `/api/v1/inventory/items`.

## Updated Code Snippets

Branded app metadata:

```python
application = FastAPI(
    title="InventEdge API",
    version="2.0.0",
    description=(
        "InventEdge is a smart inventory management platform designed to help businesses track stock, "
        "monitor product movement, analyze inventory trends, and optimize warehouse operations through "
        "data-driven insights."
    ),
)
```

Reusable stock status logic:

```python
def resolve_stock_status(quantity_on_hand: int, reorder_level: int) -> StockStatus:
    if quantity_on_hand == 0:
        return StockStatus.out
    if quantity_on_hand <= reorder_level:
        return StockStatus.low
    if quantity_on_hand <= reorder_level * 2:
        return StockStatus.watch
    return StockStatus.healthy
```

Low-stock prediction:

```python
days = estimate_stockout_days(item.quantity_on_hand, item.monthly_sales_velocity)
recommendation = "Create a replenishment order within the next week." if days and days <= 14 else "Monitor closely."
```

## Running Locally

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the API:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Open:

- API: `http://localhost:8000`
- Swagger docs: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

Run tests:

```bash
pytest
```

Run with Docker:

```bash
docker-compose up --build
```

## Database Schema Direction

The Prisma schema now uses InventEdge naming:

- `InventoryItem`: richer product tracking with SKU, category, price, quantity, reorder threshold, monthly velocity, warehouse zone, and timestamps.
- `InventoryActivity`: activity timeline events connected to inventory items.
- `INVENTEDGE_DATABASE_URL`: project-specific database environment variable.

The current API uses an in-memory repository for fast portfolio demos and deterministic tests. The schema is prepared for a persistent Prisma-backed repository as the next production step.

## Feature Enhancement Suggestions

- Add authenticated users and role-based permissions for warehouse operators, analysts, and admins.
- Replace the demo repository with a Prisma repository implementation backed by SQLite or PostgreSQL.
- Add a frontend dashboard with KPI cards, risk tables, charts, and export buttons.
- Add scheduled report generation and email delivery.
- Add barcode scanning workflows for receiving, picking, and cycle counts.
- Add audit logging middleware for all write operations.
- Add demand forecasting with historical sales imports.

## Portfolio Description

InventEdge is a rebranded and customized inventory intelligence platform built with FastAPI. It expands a basic CRUD service into a professional stock operations API with advanced search, inventory analytics, low-stock prediction, category insights, monthly reporting, activity timelines, product performance metrics, and CSV/PDF export support. The project is organized into clean API, model, service, utility, and configuration layers to make it easier to extend, test, and present as a modern portfolio backend.
