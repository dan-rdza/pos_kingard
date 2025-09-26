# models/product.py
from dataclasses import dataclass
from typing import Optional, List

@dataclass
class Product:
    sku: str
    description: str
    price: float
    cost: float = 0.0
    unit: str = "pz"
    kind: str = "Servicio"   # Servicio | Producto
    tax_rate: float = 0.16
    category_id: Optional[int] = None
    active: bool = True
    is_pos_shortcut: bool = False
    print_logo: bool = False
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    def validate(self) -> List[str]:
        errors = []
        if not self.sku or not self.sku.strip():
            errors.append("El SKU es obligatorio")
        if not self.description or not self.description.strip():
            errors.append("La descripción es obligatoria")
        if self.price is None or self.price < 0:
            errors.append("El precio debe ser mayor o igual a 0")
        if self.cost is not None and self.cost < 0:
            errors.append("El costo debe ser mayor o igual a 0")
        if self.tax_rate is None or self.tax_rate < 0:
            errors.append("La tasa de impuesto debe ser mayor o igual a 0")
        if self.unit is None or not self.unit.strip():
            errors.append("La unidad es obligatoria")
        if self.kind not in ("SERVICIO", "PRODUCTO"):
            errors.append("El tipo debe ser 'Servicio' o 'Producto'")
        return errors
