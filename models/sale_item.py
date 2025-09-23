# models/sale_item.py
from dataclasses import dataclass
from typing import Optional

@dataclass
class SaleItem:
    item_id: Optional[int]
    sale_id: int
    product_sku: str
    qty: int
    price: float
    tax_rate: float
