# test_student.py
from database import Database
from models.student import Student
from repositories.student_repo import StudentRepository

db = Database()
repo = StudentRepository(db.get_connection())

# Crear estudiante de prueba
new_student = Student(
    enrollment="MAT2024001",
    first_name="Juan",
    second_name="Pérez",
    gender="M",
    curp="PEMJ000101HDFRRRA8"
)

try:
    created = repo.create(new_student)
    print("✅ Estudiante creado:", created)
except ValueError as e:
    print("❌ Error:", e)