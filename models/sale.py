# models/sale.py
from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class Sale:
    sale_id: Optional[int]
    student_id: int
    total: float
    payment_method: str
    created_at: Optional[str] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
