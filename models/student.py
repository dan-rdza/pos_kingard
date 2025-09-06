from datetime import datetime
from typing import Optional, List, Dict, Any

class Student:
    def __init__(self, 
                 enrollment: str,
                 first_name: str,
                 second_name: Optional[str] = None,
                 address: Optional[str] = None,
                 grade_id: Optional[int] = None,
                 group_id: Optional[int] = None,
                 shift_id: Optional[int] = None,
                 gender: Optional[str] = None,
                 birth_date: Optional[str] = None,
                 curp: Optional[str] = None,
                 pay_reference: Optional[str] = None,
                 active: bool = True,
                 student_id: Optional[int] = None):
        
        self.student_id = student_id
        self.enrollment = enrollment.strip().upper()
        self.first_name = first_name.strip().title()
        self.second_name = second_name.strip().title() if second_name else None
        self.address = address.strip() if address else None
        self.grade_id = grade_id
        self.group_id = group_id
        self.shift_id = shift_id
        self.gender = gender.upper() if gender else None
        self.birth_date = birth_date
        self.curp = curp.upper().strip() if curp else None
        self.pay_reference = pay_reference.strip() if pay_reference else None
        self.active = active
        self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.updated_at = self.created_at

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.student_id,
            'enrollment': self.enrollment,
            'first_name': self.first_name,
            'second_name': self.second_name,
            'address': self.address,
            'grade_id': self.grade_id,
            'group_id': self.group_id,
            'shift_id': self.shift_id,
            'gender': self.gender,
            'birth_date': self.birth_date,
            'curp': self.curp,
            'pay_reference': self.pay_reference,
            'active': self.active,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Student':
        return cls(
            student_id=data.get('id'),
            enrollment=data['enrollment'],
            first_name=data['first_name'],
            second_name=data.get('second_name'),
            address=data.get('address'),
            grade_id=data.get('grade_id'),
            group_id=data.get('group_id'),
            shift_id=data.get('shift_id'),
            gender=data.get('gender'),
            birth_date=data.get('birth_date'),
            curp=data.get('curp'),
            pay_reference=data.get('pay_reference'),
            active=bool(data.get('active', True))
        )

    def validate(self) -> List[str]:
        errors = []
        
        if not self.enrollment:
            errors.append("La matrícula es obligatoria")
        
        if not self.first_name:
            errors.append("El nombre es obligatorio")
        
        if self.curp and len(self.curp) != 18:
            errors.append("El CURP debe tener 18 caracteres")
        
        if self.gender and self.gender not in ['M', 'F']:
            errors.append("El género debe ser 'M' o 'F'")
        
        return errors

    def __str__(self):
        return f"{self.enrollment} - {self.first_name} {self.second_name or ''}"