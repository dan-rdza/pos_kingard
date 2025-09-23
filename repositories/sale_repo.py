# repositories/sale_repo.py
from typing import List, Dict
from datetime import datetime

class SaleRepository:
    def __init__(self, db):
        self.db = db

    def create_sale(self, student, cart: List[Dict], seller, payment_method_id: int, amount: float):
        """
        Crea una venta completa con items y pago.
        """
        cur = self.db.cursor()

        # 1. Insertar venta
        cur.execute("""
            INSERT INTO sales (customer_id, customer, seller_id, seller, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (
            student.student_id,
            f"{student.first_name} {student.second_name or ''}".strip(),
            seller.get("id", 0),
            f"{seller.get('first_name','')} {seller.get('second_name','')}".strip(),
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))
        sale_id = cur.lastrowid

        # 2. Insertar items
        for item in cart:
            cur.execute("""
                INSERT INTO sale_items (sale_id, sku, description_snapshot, qty, unit_price, tax_rate, line_total)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                sale_id,
                item["sku"],
                item["description"],
                item["qty"],
                item["price"],
                item["tax_rate"],
                item["price"] * item["qty"]
            ))

        # 3. Insertar pago (ahora con method_id)
        cur.execute("""
            INSERT INTO payments (sale_id, method_id, amount, created_at)
            VALUES (?, ?, ?, ?)
        """, (
            sale_id,
            payment_method_id,
            amount,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))

        self.db.commit()
        return sale_id

    def list_sales(self, limit=20):
        cur = self.db.cursor()
        cur.execute("""
            SELECT id, customer, total, payment_status, created_at
            FROM sales
            ORDER BY created_at DESC
            LIMIT ?
        """, (limit,))
        return cur.fetchall()
