# models/educational.py
from dataclasses import dataclass
from typing import Optional

@dataclass
class Grade:
    id: Optional[int] = None
    code: str = ""
    name: str = ""
    
    def validate(self) -> list:
        errors = []
        if not self.code.strip():
            errors.append("El código del grado es obligatorio")
        if not self.name.strip():
            errors.append("El nombre del grado es obligatorio")
        return errors
    
    def __str__(self):
        return f"{self.code} - {self.name}"

@dataclass
class Group:
    id: Optional[int] = None
    code: str = ""
    name: str = ""
    
    def validate(self) -> list:
        errors = []
        if not self.code.strip():
            errors.append("El código del grupo es obligatorio")
        if not self.name.strip():
            errors.append("El nombre del grupo es obligatorio")
        return errors
    
    def __str__(self):
        return f"{self.code} - {self.name}"

@dataclass
class Shift:
    id: Optional[int] = None
    code: str = ""
    name: str = ""
    
    def validate(self) -> list:
        errors = []
        if not self.code.strip():
            errors.append("El código del turno es obligatorio")
        if not self.name.strip():
            errors.append("El nombre del turno es obligatorio")
        return errors
    
    def __str__(self):
        return f"{self.code} - {self.name}"