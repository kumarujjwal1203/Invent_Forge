from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_home_returns_inventedge_identity():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["project"] == "InventEdge"


def test_create_inventory_item():
    response = client.post(
        "/api/v1/inventory/items",
        json={
            "name": "Smart Shelf Sensor",
            "description": "Shelf-level stock tracking sensor.",
            "category": "Tracking",
            "unit_price": 29.5,
            "sku": "SHELF-EDGE-999",
            "quantity_on_hand": 9,
            "reorder_level": 5,
            "monthly_sales_velocity": 11,
            "warehouse_zone": "D4",
        },
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Smart Shelf Sensor"
    assert response.json()["stock_status"] == "watch"


def test_search_and_advanced_filters():
    response = client.get("/api/v1/inventory/items?query=label&stock_status=low&max_price=20")
    assert response.status_code == 200
    assert response.json()[0]["sku"] == "LBL-EDGE-220"


def test_analytics_dashboard():
    response = client.get("/api/v1/analytics/dashboard")
    assert response.status_code == 200
    payload = response.json()
    assert payload["total_items"] >= 4
    assert payload["category_count"] >= 3


def test_low_stock_predictions():
    response = client.get("/api/v1/analytics/low-stock-predictions")
    assert response.status_code == 200
    assert any(item["sku"] == "RFID-EDGE-114" for item in response.json())


def test_csv_export():
    response = client.get("/api/v1/exports/inventory.csv")
    assert response.status_code == 200
    assert "inventedge-inventory.csv" in response.headers["content-disposition"]
    assert "sku,name,category" in response.text
