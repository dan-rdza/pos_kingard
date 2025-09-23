# repositories/payment_method_repo.py
from typing import List, Dict

class PaymentMethodRepository:
    def __init__(self, db):
        self.db = db

    def list_all(self, active_only=True) -> List[Dict]:
        cur = self.db.cursor()
        if active_only:
            cur.execute("SELECT id, name, code, active FROM payment_methods WHERE active = 1 ORDER BY name")
        else:
            cur.execute("SELECT id, name, code, active FROM payment_methods ORDER BY name")
        return [dict(row) for row in cur.fetchall()]

    def get(self, pm_id: int) -> Dict | None:
        cur = self.db.cursor()
        cur.execute("SELECT id, name, code, active FROM payment_methods WHERE id = ?", (pm_id,))
        row = cur.fetchone()
        return dict(row) if row else None

    def create(self, name: str, code: str):
        cur = self.db.cursor()
        cur.execute("INSERT INTO payment_methods (name, code, active) VALUES (?, ?, 1)", (name, code))
        self.db.commit()
        return cur.lastrowid

    def update(self, pm_id: int, name: str, code: str, active: bool):
        cur = self.db.cursor()
        cur.execute(
            "UPDATE payment_methods SET name = ?, code = ?, active = ? WHERE id = ?",
            (name, code, 1 if active else 0, pm_id)
        )
        self.db.commit()

    def deactivate(self, pm_id: int):
        cur = self.db.cursor()
        cur.execute("UPDATE payment_methods SET active = 0 WHERE id = ?", (pm_id,))
        self.db.commit()
