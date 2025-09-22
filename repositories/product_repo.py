# repositories/product_repo.py
import sqlite3
from typing import List, Optional
from models.product import Product

class ProductRepository:
    def __init__(self, db_connection):
        self.conn = db_connection
        self._ensure_catalogs()

    def _ensure_catalogs(self):
        # Aquí podrías validar que exista la columna is_pos_shortcut, etc.
        # Por simplicidad lo omitimos (asumimos migración aplicada).
        pass

    # ---------- CATEGORIES ----------
    def list_categories(self) -> List[tuple]:
        cur = self.conn.cursor()
        cur.execute("SELECT id, name FROM categories ORDER BY name")
        return cur.fetchall()

    def ensure_category(self, name: str) -> int:
        cur = self.conn.cursor()
        cur.execute("INSERT OR IGNORE INTO categories(name) VALUES (?)", (name.strip(),))
        self.conn.commit()
        cur.execute("SELECT id FROM categories WHERE name = ?", (name.strip(),))
        row = cur.fetchone()
        return row[0] if row else None

    # ---------- PRODUCTS ----------
    def create(self, p: Product) -> Product:
        errs = p.validate()
        if errs:
            raise ValueError(", ".join(errs))

        try:
            self.conn.execute("""
                INSERT INTO products
                    (sku, description, price, cost, unit, kind, tax_rate, category_id, active, is_pos_shortcut)
                VALUES (?,   ?,           ?,     ?,    ?,    ?,    ?,        ?,           ?,      ?)
            """, (
                p.sku, p.description, p.price, p.cost, p.unit, p.kind,
                p.tax_rate, p.category_id, 1 if p.active else 0, 1 if p.is_pos_shortcut else 0
            ))
            self.conn.commit()
            return p
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed: products.sku" in str(e):
                raise ValueError("El SKU ya existe")
            raise

    def update(self, p: Product) -> Product:
        errs = p.validate()
        if errs:
            raise ValueError(", ".join(errs))

        self.conn.execute("""
            UPDATE products
               SET description = ?,
                   price = ?,
                   cost = ?,
                   unit = ?,
                   kind = ?,
                   tax_rate = ?,
                   category_id = ?,
                   active = ?,
                   is_pos_shortcut = ?,
                   updated_at = datetime('now','localtime')
             WHERE sku = ?
        """, (
            p.description, p.price, p.cost, p.unit, p.kind, p.tax_rate,
            p.category_id, 1 if p.active else 0, 1 if p.is_pos_shortcut else 0,
            p.sku
        ))
        self.conn.commit()
        return p

    def get(self, sku: str) -> Optional[Product]:
        cur = self.conn.cursor()
        # 🔧 Unificamos el orden de columnas en TODOS los SELECTs
        cur.execute("""
            SELECT sku, description, price, cost, unit, kind, tax_rate, category_id, active,
                   is_pos_shortcut, created_at, updated_at
              FROM products
             WHERE sku = ?
        """, (sku,))
        row = cur.fetchone()
        return self._row_to_product(row) if row else None

    def search(self, q: str, active_only: bool = True) -> List[Product]:
        term = f"%{q.lower()}%"
        cur = self.conn.cursor()
        base_sql = """
            SELECT sku, description, price, cost, unit, kind, tax_rate, category_id, active,
                   is_pos_shortcut, created_at, updated_at
              FROM products
        """
        if active_only:
            cur.execute(base_sql + """
                 WHERE active = 1 AND (LOWER(description) LIKE ? OR LOWER(sku) LIKE ?)
                 ORDER BY description
            """, (term, term))
        else:
            cur.execute(base_sql + """
                 WHERE (LOWER(description) LIKE ? OR LOWER(sku) LIKE ?)
                 ORDER BY description
            """, (term, term))
        return [self._row_to_product(r) for r in cur.fetchall()]

    def list_all(self, active_only: bool = True) -> List[Product]:
        cur = self.conn.cursor()
        base_sql = """
            SELECT sku, description, price, cost, unit, kind, tax_rate, category_id, active,
                   is_pos_shortcut, created_at, updated_at
              FROM products
        """
        if active_only:
            cur.execute(base_sql + " WHERE active = 1 ORDER BY description")
        else:
            cur.execute(base_sql + " ORDER BY description")
        return [self._row_to_product(r) for r in cur.fetchall()]

    def toggle_shortcut(self, sku: str, shortcut_value: bool):
        new_shortcut = not shortcut_value
        self.conn.execute("""
            UPDATE products
               SET is_pos_shortcut = ?
             WHERE sku = ?
        """, (1 if new_shortcut else 0, sku))
        self.conn.commit()

    def deactivate(self, sku: str) -> bool:
        cur = self.conn.cursor()
        cur.execute("""
            UPDATE products
               SET active = 0, updated_at = datetime('now','localtime')
             WHERE sku = ?
        """, (sku,))
        self.conn.commit()
        return cur.rowcount > 0

    # ---------- Helpers ----------
    def _row_to_product(self, r) -> Product:
        # Esperamos SIEMPRE 12 columnas en el orden unificado
        return Product(
            sku=r[0], description=r[1], price=float(r[2]), cost=float(r[3]),
            unit=r[4], kind=r[5], tax_rate=float(r[6]), category_id=r[7],
            active=bool(r[8]), is_pos_shortcut=bool(r[9]),
            created_at=r[10], updated_at=r[11]
        )

    # ---------- POS helpers ----------
    def get_pos_shortcuts(self, limit=8):
        cur = self.conn.cursor()
        cur.execute("""
            SELECT sku, description, price, tax_rate, is_pos_shortcut
              FROM products
             WHERE is_pos_shortcut = 1
             ORDER BY description ASC
             LIMIT ?
        """, (limit,))
        rows = cur.fetchall()
        return [self._map_row(r) for r in rows]

    def get_top_sold(self, limit=8):
        cur = self.conn.cursor()
        cur.execute("""
            SELECT p.sku, p.description, p.price, p.tax_rate, p.is_pos_shortcut
              FROM products p
              JOIN sale_items si ON si.sku = p.sku
             GROUP BY p.sku
             ORDER BY SUM(si.qty) DESC
             LIMIT ?
        """, (limit,))
        rows = cur.fetchall()
        return [self._map_row(r) for r in rows]

    def _map_row(self, row):
        return {
            "sku": row[0],
            "description": row[1],
            "price": float(row[2]),
            "tax_rate": float(row[3]),
            "is_pos_shortcut": bool(row[4]),
        }
