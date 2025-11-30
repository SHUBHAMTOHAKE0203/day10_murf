# src/merchant.py
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

BASE = Path(__file__).parent
CATALOG_PATH = BASE / "catalog.json"
ORDERS_PATH = BASE.parent / "data" / "orders.json"

# Ensure data folder and orders.json exist
ORDERS_PATH.parent.mkdir(parents=True, exist_ok=True)
if not ORDERS_PATH.exists():
    ORDERS_PATH.write_text("[]", encoding="utf-8")

# Load the product catalog
with open(CATALOG_PATH, "r", encoding="utf-8") as f:
    PRODUCTS: List[Dict] = json.load(f)


def _load_orders() -> List[Dict]:
    with open(ORDERS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_orders(orders: List[Dict]) -> None:
    with open(ORDERS_PATH, "w", encoding="utf-8") as f:
        json.dump(orders, f, indent=2, ensure_ascii=False)


def list_products(filters: Optional[Dict] = None) -> List[Dict]:
    """
    Return products filtered by optional filters:
      filters: { "category": str, "color": str, "max_price": int, "size": str }
    All filters optional.
    """
    results = PRODUCTS
    if not filters:
        return results

    cat = filters.get("category")
    color = filters.get("color")
    max_price = filters.get("max_price")
    size = filters.get("size")

    if cat:
        results = [p for p in results if p.get("category", "").lower() == str(cat).lower()]
    if color:
        results = [p for p in results if p.get("color", "").lower() == str(color).lower()]
    if size:
        results = [p for p in results if p.get("size", "").lower() == str(size).lower()]
    if max_price is not None:
        try:
            maxp = int(max_price)
            results = [p for p in results if int(p.get("price", 0)) <= maxp]
        except (ValueError, TypeError):
            pass

    return results


def create_order(line_items: List[Dict]) -> Dict:
    """
    line_items: [{"product_id": "...", "quantity": 1}, ...]
    Persists order to data/orders.json and returns created order.
    """
    orders = _load_orders()
    items = []
    total = 0
    currency = "INR"

    for li in line_items:
        pid = li.get("product_id")
        qty = int(li.get("quantity", 1))
        prod = next((p for p in PRODUCTS if p["id"] == pid), None)
        if not prod:
            continue
        unit_price = int(prod.get("price", 0))
        items.append({
            "product_id": prod["id"],
            "name": prod["name"],
            "quantity": qty,
            "unit_price": unit_price
        })
        total += unit_price * qty

    order = {
        "id": f"ORD{datetime.now().strftime('%Y%m%d%H%M%S')}{str(uuid.uuid4())[:4]}",
        "items": items,
        "total": total,
        "currency": currency,
        "created_at": datetime.now().isoformat()
    }

    orders.append(order)
    _save_orders(orders)
    return order


def last_order() -> Optional[Dict]:
    orders = _load_orders()
    return orders[-1] if orders else None


def remove_item_from_order(order_id: str, product_id: str) -> Optional[Dict]:
    orders = _load_orders()
    order = next((o for o in orders if o.get("id") == order_id), None)
    if not order:
        return None
    order["items"] = [i for i in order["items"] if i["product_id"] != product_id]
    order["total"] = sum(i["quantity"] * i["unit_price"] for i in order["items"])
    _save_orders(orders)
    return order
