import sqlite3
from typing import List, Optional, Dict, Any
from models.student import Student

class StudentRepository:
    def __init__(self, db_connection):
        self.conn = db_connection

    def create(self, student: Student) -> Optional[Student]:
        errors = student.validate()
        if errors:
            raise ValueError(f"Errores de validación: {', '.join(errors)}")
        
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO customers 
                (enrollment, first_name, second_name, address, grade_id, 
                 group_id, shift_id, gender, birth_date, curp, pay_reference, active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                student.enrollment, student.first_name, student.second_name,
                student.address, student.grade_id, student.group_id,
                student.shift_id, student.gender, student.birth_date,
                student.curp, student.pay_reference, student.active
            ))
            
            student.student_id = cursor.lastrowid
            self.conn.commit()
            return student
            
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed: customers.enrollment" in str(e):
                raise ValueError("La matrícula ya existe")
            elif "UNIQUE constraint failed: customers.curp" in str(e):
                raise ValueError("El CURP ya está registrado")
            raise

    def get_by_id(self, student_id: int) -> Optional[Student]:
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM customers WHERE id = ? AND active = 1
        ''', (student_id,))
        
        row = cursor.fetchone()
        return Student.from_dict(dict(row)) if row else None

    def get_by_enrollment(self, enrollment: str) -> Optional[Student]:
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM customers WHERE enrollment = ? AND active = 1
        ''', (enrollment.upper(),))
        
        row = cursor.fetchone()
        return Student.from_dict(dict(row)) if row else None

    def get_all(self, active_only: bool = True) -> List[Student]:
        cursor = self.conn.cursor()
        if active_only:
            cursor.execute('SELECT * FROM customers WHERE active = 1 ORDER BY first_name, second_name')
        else:
            cursor.execute('SELECT * FROM customers ORDER BY first_name, second_name')
        
        return [Student.from_dict(dict(row)) for row in cursor.fetchall()]

    def search(self, query: str, active_only: bool = True) -> List[Student]:
        cursor = self.conn.cursor()
        search_term = f"%{query.lower()}%"
        
        if active_only:
            cursor.execute('''
                SELECT * FROM customers 
                WHERE active = 1 AND 
                (LOWER(first_name) LIKE ? OR LOWER(second_name) LIKE ? OR enrollment LIKE ?)
                ORDER BY first_name, second_name
            ''', (search_term, search_term, search_term))
        else:
            cursor.execute('''
                SELECT * FROM customers 
                WHERE LOWER(first_name) LIKE ? OR LOWER(second_name) LIKE ? OR enrollment LIKE ?
                ORDER BY first_name, second_name
            ''', (search_term, search_term, search_term))
        
        return [Student.from_dict(dict(row)) for row in cursor.fetchall()]

    def update(self, student: Student) -> Optional[Student]:
        errors = student.validate()
        if errors:
            raise ValueError(f"Errores de validación: {', '.join(errors)}")
        
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                UPDATE customers 
                SET enrollment = ?, first_name = ?, second_name = ?, address = ?,
                    grade_id = ?, group_id = ?, shift_id = ?, gender = ?,
                    birth_date = ?, curp = ?, pay_reference = ?, active = ?,
                    updated_at = datetime('now', 'localtime')
                WHERE id = ?
            ''', (
                student.enrollment, student.first_name, student.second_name,
                student.address, student.grade_id, student.group_id,
                student.shift_id, student.gender, student.birth_date,
                student.curp, student.pay_reference, student.active,
                student.student_id
            ))
            
            self.conn.commit()
            return student
            
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed: customers.enrollment" in str(e):
                raise ValueError("La matrícula ya existe")
            elif "UNIQUE constraint failed: customers.curp" in str(e):
                raise ValueError("El CURP ya está registrado")
            raise

    def deactivate(self, student_id: int) -> bool:
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                UPDATE customers SET active = 0, updated_at = datetime('now', 'localtime')
                WHERE id = ?
            ''', (student_id,))
            
            self.conn.commit()
            return cursor.rowcount > 0
            
        except sqlite3.Error:
            return False

    def get_related_parents(self, student_id: int) -> List[Dict[str, Any]]:
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT p.*, cp.is_primary, cp.can_pickup, cp.emergency_contact
            FROM parents p
            JOIN customer_parents cp ON p.id = cp.parent_id
            WHERE cp.customer_id = ?
            ORDER BY cp.is_primary DESC, p.first_name
        ''', (student_id,))
        
        return [dict(row) for row in cursor.fetchall()]