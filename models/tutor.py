from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Tutor:
    tutor_id: Optional[int] = None
    student_id: int = None
    first_name: str = ""
    second_name: str = ""
    relationship: str = ""  # Padre, Madre, Tutor, Abuelo, etc.
    phone: str = ""
    email: str = ""
    is_primary: bool = False
    active: bool = True
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
    
    def full_name(self):
        return f"{self.first_name} {self.second_name}".strip()