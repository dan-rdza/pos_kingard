# ui/students.py
import customtkinter as ctk
from tkinter import messagebox
from models.student import Student
from repositories.student_repo import StudentRepository
from repositories.tutor_repo import TutorRepository
from ui.tutors import TutorsFrame


class StudentsFrame(ctk.CTkFrame):
    def __init__(self, parent, db_connection):
        super().__init__(parent, fg_color="transparent")
        self.parent = parent
        self.db_connection = db_connection
        self.repo = StudentRepository(db_connection)
        self.tutor_repo = TutorRepository(db_connection)
        self.current_student = None

        self.create_widgets()
        self.load_students()

    def create_widgets(self):
        # Header
        self.title_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.title_frame.pack(fill="x", padx=(10, 10), pady=(15, 15))

        ctk.CTkLabel(
            self.title_frame,
            text="👥 Gestión de Alumnos",
            font=ctk.CTkFont(size=22, weight="bold")
        ).pack(side="left")

        ctk.CTkButton(
            self.title_frame,
            text="⬅️ Volver al Menú",
            command=self.go_back_to_menu,
            height=35, fg_color="gray50", hover_color="gray40"
        ).pack(side="right", padx=(10, 0))

        ctk.CTkButton(
            self.title_frame,
            text="➕ Nuevo Alumno",
            command=self.show_new_form,
            height=35, fg_color="#2CC985", hover_color="#207A4C"
        ).pack(side="right")

        # Body con 2 paneles
        self.body = ctk.CTkFrame(self, fg_color="transparent")
        self.body.pack(fill="both", expand=True)

        self.body.grid_columnconfigure(0, weight=2, uniform="col")
        self.body.grid_columnconfigure(1, weight=1, uniform="col")
        self.body.grid_rowconfigure(0, weight=1)

        # Panel izquierdo (lista + búsqueda)
        self.list_frame = ctk.CTkScrollableFrame(self.body, fg_color="transparent")
        self.list_frame.grid(row=0, column=0, sticky="nsew")

        # Panel derecho (formulario o placeholder)
        self.form_frame = ctk.CTkFrame(self.body, fg_color="transparent")
        self.form_frame.grid(row=0, column=1, sticky="nsew")

        self._show_placeholder()

    def _show_placeholder(self):
        self._clear_container(self.form_frame)
        placeholder = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        placeholder.pack(expand=True, fill="both")
        ctk.CTkLabel(
            placeholder,
            text="👈 Selecciona un alumno o da clic en ➕ Nuevo",
            font=ctk.CTkFont(size=14),
            text_color="gray70"
        ).pack(expand=True)

    def _clear_container(self, container):
        for w in container.winfo_children():
            w.destroy()

    def load_students(self):
        for w in self.list_frame.winfo_children():
            w.destroy()

        students = self.repo.get_all()
        if not students:
            ctk.CTkLabel(
                self.list_frame, text="No hay alumnos registrados",
                text_color="gray60", font=ctk.CTkFont(size=14)
            ).pack(pady=50)
            return

        self.list_frame.grid_columnconfigure((0, 1), weight=1, uniform="col")

        for idx, student in enumerate(students):
            row = idx // 2
            col = idx % 2
            card = self.create_student_card(student)
            card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

    def go_back_to_menu(self):
        for widget in self.parent.winfo_children():
            widget.destroy()
        main_app = self.parent.master if hasattr(self.parent, 'master') else self.parent
        if hasattr(main_app, 'set_window_size'):
            main_app.set_window_size("menu")
        from ui.menu import MainMenu
        menu_frame = MainMenu(self.parent, self.parent.current_user)
        menu_frame.pack(fill="both", expand=True)

    def create_student_card(self, student):
        card = ctk.CTkFrame(self.list_frame, corner_radius=10, border_width=1)

        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.pack(fill="both", expand=True, padx=15, pady=10)

        ctk.CTkLabel(
            info_frame,
            text=f"{student.enrollment}",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w")

        ctk.CTkLabel(
            info_frame,
            text=f"{student.first_name} {student.second_name or ''}",
            font=ctk.CTkFont(size=14)
        ).pack(anchor="w")

        action_frame = ctk.CTkFrame(card, fg_color="transparent")
        action_frame.pack(fill="x", padx=15, pady=(5, 10))

        ctk.CTkButton(
            action_frame, text="✏️ Editar",
            command=lambda s=student: self.edit_student(s),
            height=30, width=80, fg_color="gray40"
        ).pack(side="right", padx=(5, 0))

        ctk.CTkButton(
            action_frame, 
            text="👥 Tutores",
            command=lambda s=student: self.manage_tutors(s),
            height=30, width=80, fg_color="#2b3d78"
        ).pack(side="right", padx=(5, 0))

        return card

    def show_new_form(self):
        self.current_student = None
        self._show_form()

    def edit_student(self, student):
        self.current_student = student
        self._show_form(student)

    def manage_tutors(self, student):
        # Destruir la pantalla actual (alumnos)
        for w in self.parent.winfo_children():
            w.destroy()

        # Crear nueva pantalla de tutores, independiente
        TutorsFrame(self.parent, self.db_connection, student).pack(fill="both", expand=True)



    def __manage_tutors(self, student):
        self.current_student = student

        def _back():
            # reconstruir vista de alumnos
            for w in self.body.winfo_children():
                w.destroy()
            self.create_widgets()
            self.load_students()

        # limpiar body y mostrar tutores a pantalla completa
        for w in self.body.winfo_children():
            w.destroy()

        panel = TutorsPanel(self.body, self.db_connection, student, on_back=_back)
        panel.grid(row=0, column=0, sticky="nsew")
        self.body.grid_columnconfigure(0, weight=1)
