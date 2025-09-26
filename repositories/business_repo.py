# repositories/business_repo.py
class BusinessRepository:
    def __init__(self, db):
        self.db = db

    def get_config(self):
        cur = self.db.cursor()
        cur.execute("SELECT id, name, rfc, address, phone, thank_you, tax_rate, currency FROM business_config LIMIT 1")
        row = cur.fetchone()
        if not row:
            return None
        return {
            "id": row[0],
            "name": row[1],
            "rfc": row[2],
            "address": row[3],
            "phone": row[4],
            "footer": row[5],  # usamos thank_you como pie de ticket
            "tax_rate": row[6],
            "currency": row[7],
        }
