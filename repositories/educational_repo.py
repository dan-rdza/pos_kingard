# repositories/educational_repo.py
import sqlite3
from typing import List, Optional
from models.educational import Grade, Group, Shift

class EducationalRepository:
    def __init__(self, db_connection):
        self.conn = db_connection

    # ---------- GRADES ----------
    def get_all_grades(self) -> List[Grade]:
        """Obtiene todos los grados ordenados por código"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, code, name FROM grades ORDER BY code")
        rows = cursor.fetchall()
        return [Grade(id=row[0], code=row[1], name=row[2]) for row in rows]

    def get_grade_by_id(self, grade_id: int) -> Optional[Grade]:
        """Obtiene un grado por ID"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, code, name FROM grades WHERE id = ?", (grade_id,))
        row = cursor.fetchone()
        return Grade(id=row[0], code=row[1], name=row[2]) if row else None

    def create_grade(self, grade: Grade) -> bool:
        """Crea un nuevo grado"""
        errors = grade.validate()
        if errors:
            raise ValueError(", ".join(errors))
            
        try:
            cursor = self.conn.cursor()
            cursor.execute("INSERT INTO grades (code, name) VALUES (?, ?)", 
                          (grade.code, grade.name))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def delete_grade(self, grade_id: int) -> bool:
        """Elimina un grado"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM grades WHERE id = ?", (grade_id,))
            self.conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error:
            return False

    # ---------- GROUPS ----------
    def get_all_groups(self) -> List[Group]:
        """Obtiene todos los grupos ordenados por código"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, code, name FROM groups ORDER BY code")
        rows = cursor.fetchall()
        return [Group(id=row[0], code=row[1], name=row[2]) for row in rows]

    def get_group_by_id(self, group_id: int) -> Optional[Group]:
        """Obtiene un grupo por ID"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, code, name FROM groups WHERE id = ?", (group_id,))
        row = cursor.fetchone()
        return Group(id=row[0], code=row[1], name=row[2]) if row else None

    def create_group(self, group: Group) -> bool:
        """Crea un nuevo grupo"""
        errors = group.validate()
        if errors:
            raise ValueError(", ".join(errors))
            
        try:
            cursor = self.conn.cursor()
            cursor.execute("INSERT INTO groups (code, name) VALUES (?, ?)", 
                          (group.code, group.name))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def delete_group(self, group_id: int) -> bool:
        """Elimina un grupo"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM groups WHERE id = ?", (group_id,))
            self.conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error:
            return False

    # ---------- SHIFTS ----------
    def get_all_shifts(self) -> List[Shift]:
        """Obtiene todos los turnos ordenados por código"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, code, name FROM shifts ORDER BY code")
        rows = cursor.fetchall()
        return [Shift(id=row[0], code=row[1], name=row[2]) for row in rows]

    def get_shift_by_id(self, shift_id: int) -> Optional[Shift]:
        """Obtiene un turno por ID"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, code, name FROM shifts WHERE id = ?", (shift_id,))
        row = cursor.fetchone()
        return Shift(id=row[0], code=row[1], name=row[2]) if row else None

    def create_shift(self, shift: Shift) -> bool:
        """Crea un nuevo turno"""
        errors = shift.validate()
        if errors:
            raise ValueError(", ".join(errors))
            
        try:
            cursor = self.conn.cursor()
            cursor.execute("INSERT INTO shifts (code, name) VALUES (?, ?)", 
                          (shift.code, shift.name))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def delete_shift(self, shift_id: int) -> bool:
        """Elimina un turno"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM shifts WHERE id = ?", (shift_id,))
            self.conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error:
            return False