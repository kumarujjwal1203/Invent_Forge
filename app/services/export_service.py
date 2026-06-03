from __future__ import annotations

import csv
import io

from app.models.schemas import InventoryItem


def inventory_to_csv(items: list[InventoryItem]) -> str:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(
        [
            "id",
            "sku",
            "name",
            "category",
            "quantity_on_hand",
            "reorder_level",
            "unit_price",
            "inventory_value",
            "stock_status",
            "warehouse_zone",
        ]
    )
    for item in items:
        writer.writerow(
            [
                item.id,
                item.sku,
                item.name,
                item.category,
                item.quantity_on_hand,
                item.reorder_level,
                item.unit_price,
                item.inventory_value,
                item.stock_status.value,
                item.warehouse_zone,
            ]
        )
    return output.getvalue()


def inventory_to_pdf_bytes(items: list[InventoryItem]) -> bytes:
    lines = ["InventEdge Inventory Report", "Smart Inventory Intelligence", ""]
    lines.extend(f"{item.sku} | {item.name} | {item.quantity_on_hand} units | ${item.inventory_value}" for item in items)
    body = "\\n".join(lines).replace("(", "\\(").replace(")", "\\)")
    stream = f"BT /F1 12 Tf 50 760 Td ({body}) Tj ET"
    pdf = (
        "%PDF-1.4\n"
        "1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n"
        "2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj\n"
        "3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        "/Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >> endobj\n"
        "4 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj\n"
        f"5 0 obj << /Length {len(stream)} >> stream\n{stream}\nendstream endobj\n"
        "xref\n0 6\n0000000000 65535 f \n"
        "trailer << /Root 1 0 R /Size 6 >>\nstartxref\n0\n%%EOF\n"
    )
    return pdf.encode("utf-8")
