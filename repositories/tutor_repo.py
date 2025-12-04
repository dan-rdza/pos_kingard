# repositories/tutor_repo.py
import sqlite3
from models.tutor import Tutor
from datetime import datetime

class TutorRepository:
    def __init__(self, db_connection):
        self.conn = db_connection        

    def create(self, tutor: Tutor) -> Tutor:
        cursor = self.conn.execute(
            "INSERT INTO tutors (student_id, first_name, second_name, relationship, phone, email, is_primary) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (tutor.student_id, tutor.first_name, tutor.second_name, tutor.relationship, tutor.phone, tutor.email, 1 if tutor.is_primary else 0)
        )
        self.conn.commit()
        tutor.tutor_id = cursor.lastrowid
        return tutor

    def get_by_student(self, student_id: int):
        cursor = self.conn.execute(
            "SELECT tutor_id, student_id, first_name, second_name, relationship, phone, email, is_primary, active, created_at FROM tutors WHERE student_id = ? AND active = 1 ORDER BY is_primary DESC, first_name",
            (student_id,)
        )
        tutors = []
        for row in cursor.fetchall():
            tutors.append(Tutor(
                tutor_id=row[0], student_id=row[1], first_name=row[2], second_name=row[3],
                relationship=row[4], phone=row[5], email=row[6], is_primary=bool(row[7]),
                active=bool(row[8]), created_at=row[9]
            ))
        return tutors

    def update(self, tutor: Tutor):
        self.conn.execute(
            "UPDATE tutors SET first_name=?, second_name=?, relationship=?, phone=?, email=?, is_primary=? WHERE tutor_id=?",
            (tutor.first_name, tutor.second_name, tutor.relationship, tutor.phone, tutor.email, 1 if tutor.is_primary else 0, tutor.tutor_id)
        )
        self.conn.commit()

    def delete(self, tutor_id: int):
        self.conn.execute("UPDATE tutors SET active = 0 WHERE tutor_id = ?", (tutor_id,))
        self.conn.commit()

    def set_primary(self, tutor_id: int, student_id: int):
        self.conn.execute("UPDATE tutors SET is_primary = 0 WHERE student_id = ?", (student_id,))
        self.conn.execute("UPDATE tutors SET is_primary = 1 WHERE tutor_id = ?", (tutor_id,))
        self.conn.commit()
