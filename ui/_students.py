# ui/students.py
import customtkinter as ctk
from tkinter import messagebox
from models.student import Student
from repositories.student_repo import StudentRepository
from repositories.tutor_repo import TutorRepository 
from ui.tutors import TutorsFrame
from shared.utils import char_limit_validator


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
        left_panel = ctk.CTkFrame(self.body, fg_color="transparent")
        left_panel.grid(row=0, column=0, sticky="nsew")

        # Búsqueda
        self.search_container = ctk.CTkFrame(left_panel, fg_color="transparent")
        self.search_container.pack(fill="x", padx=(10, 10), pady=(10, 20))

        frame_width = int(self.winfo_screenwidth() * 0.6)

        self.search_frame = ctk.CTkFrame(self.search_container, fg_color="transparent", width=frame_width)
        self.search_frame.pack(anchor="w")

        self.search_var = ctk.StringVar()
        self.search_entry = ctk.CTkEntry(
            self.search_frame,
            placeholder_text="Buscar por nombre o matrícula...",
            textvariable=self.search_var,
            height=40,
            width=int(frame_width * 0.5)
        )
        self.search_entry.pack(side="left", fill="x", padx=(0, 10))
        self.search_entry.bind("<KeyRelease>", self.on_search)

        ctk.CTkButton(
            self.search_frame, text="🔍 Buscar",
            command=self.on_search, height=40, width=100
        ).pack(side="right")

        # Lista
        self.list_frame = ctk.CTkScrollableFrame(left_panel, fg_color="transparent")
        self.list_frame.pack(fill="both", expand=True)

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

    def on_search(self, event=None):
        query = self.search_var.get().strip()
        if not query:
            self.load_students()
            return
        
        for widget in self.list_frame.winfo_children():
            widget.destroy()
        
        students = self.repo.search(query)
        
        if not students:
            ctk.CTkLabel(
                self.list_frame,
                text=f"No se encontraron alumnos para '{query}'",
                text_color="gray60",
                font=ctk.CTkFont(size=14)
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

        if student.curp:
            ctk.CTkLabel(
                info_frame, text=f"CURP: {student.curp}",
                font=ctk.CTkFont(size=12), text_color="gray60"
            ).pack(anchor="w", pady=(2, 0))

        tutors = self.tutor_repo.get_by_student(student.student_id)
        primary_tutor = next((t for t in tutors if t.is_primary), None)
        if primary_tutor:
            ctk.CTkLabel(
                info_frame,
                text=f"👤 {primary_tutor.full_name()} ({primary_tutor.relationship})",
                font=ctk.CTkFont(size=12), text_color="gray60"
            ).pack(anchor="w", pady=(2, 0))

            ctk.CTkLabel(
                info_frame,
                text=f"📱{primary_tutor.formart_phonenumber()}",
                font=ctk.CTkFont(size=12), text_color="gray60"
            ).pack(anchor="w", pady=(2, 0))
            

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

    def hide_form(self):
        self.current_student = None
        self._show_placeholder()
        self.load_students()

    def edit_student(self, student):
        self.current_student = student
        self._show_form(student)

    def _show_form(self, student: Student | None = None):
        self._clear_container(self.form_frame)

        form = ctk.CTkScrollableFrame(self.form_frame, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=10, pady=20)
        form.grid_columnconfigure(0, weight=1)

        title_text = "➕ Nuevo Alumno" if student is None else "✏️ Editar Alumno"
        ctk.CTkLabel(form, text=title_text, font=ctk.CTkFont(size=20, weight="bold")).grid(
            row=0, column=0, sticky="w", pady=(0, 10)
        )

        row = 1
        def add_field(label, widget):
            nonlocal row
            ctk.CTkLabel(form, text=label, font=ctk.CTkFont(weight="bold")).grid(row=row, column=0, sticky="w", pady=(8, 2))
            row += 1
            widget.grid(row=row, column=0, sticky="ew", pady=(0, 5))
            row += 1

        vcmd = (self.register(char_limit_validator(18)), '%P')
        
        self.enrollment_entry = ctk.CTkEntry(form, height=40, placeholder_text="Matrícula")
        self.first_name_entry = ctk.CTkEntry(form, height=40, placeholder_text="Nombre")
        self.second_name_entry = ctk.CTkEntry(form, height=40, placeholder_text="Apellido")
        self.curp_entry = ctk.CTkEntry(form, height=40, placeholder_text="CURP",validate="key", validatecommand=vcmd)
        self.gender_var = ctk.StringVar(value="")
        self.gender_cb = ctk.CTkComboBox(form, values=["", "M", "F"], variable=self.gender_var, height=40)
        self.birth_date_entry = ctk.CTkEntry(form, height=40, placeholder_text="YYYY-MM-DD")
        self.pay_ref_entry = ctk.CTkEntry(form, height=40, placeholder_text="Referencia de pago")
        self.address_entry = ctk.CTkEntry(form, height=40, placeholder_text="Dirección")
        

        add_field("Matrícula *", self.enrollment_entry)
        add_field("Nombre *", self.first_name_entry)
        add_field("Apellido", self.second_name_entry)
        add_field("CURP", self.curp_entry)
        add_field("Género", self.gender_cb)
        add_field("Fecha de nacimiento", self.birth_date_entry)
        add_field("Referencia de pago", self.pay_ref_entry)
        add_field("Dirección", self.address_entry)

        btns = ctk.CTkFrame(form, fg_color="transparent")
        btns.grid(row=row, column=0, sticky="ew", pady=(15, 0))

        ctk.CTkButton(
            btns, text="↩️ Cancelar", fg_color="gray50", height=40,
            command=self.hide_form
        ).pack(side="left", padx=(0, 10))

        btn_text = "💾 Guardar" if student is None else "🔄 Actualizar"
        btn_color = "#2CC985" if student is None else "#3B82F6"
        ctk.CTkButton(
            btns, text=btn_text, fg_color=btn_color, height=40,
            command=self.save_student
        ).pack(side="right")

        if student:
            self.fill_form(student)

    def fill_form(self, student):
        self.enrollment_entry.insert(0, student.enrollment)
        self.first_name_entry.insert(0, student.first_name)
        if student.second_name:
            self.second_name_entry.insert(0, student.second_name)
        if student.curp:
            self.curp_entry.insert(0, student.curp)
        if student.gender:
            self.gender_var.set(student.gender)
        if student.birth_date:
            self.birth_date_entry.insert(0, student.birth_date)
        if student.pay_reference:
            self.pay_ref_entry.insert(0, student.pay_reference)
        if student.address:
            self.address_entry.insert(0, student.address)

    def save_student(self):
        try:
            student_data = {
                'enrollment': self.enrollment_entry.get().strip(),
                'first_name': self.first_name_entry.get().strip(),
                'second_name': self.second_name_entry.get().strip() or None,
                'address': self.address_entry.get().strip() or None,
                'gender': self.gender_var.get() or None,
                'birth_date': self.birth_date_entry.get().strip() or None,
                'curp': self.curp_entry.get().strip() or None,
                'pay_reference': self.pay_ref_entry.get().strip() or None
            }

            if self.current_student:
                student_data['student_id'] = self.current_student.student_id
                student_data['active'] = self.current_student.active
                student = Student(**student_data)
                self.repo.update(student)
                messagebox.showinfo("Éxito", "Alumno actualizado correctamente")
            else:
                student = Student(**student_data)
                self.repo.create(student)
                messagebox.showinfo("Éxito", "Alumno creado correctamente")

            self.hide_form()
        except ValueError as e:
            messagebox.showerror("Error de validación", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar: {str(e)}")

    def manage_tutors(self, student):
        # Destruir la pantalla actual (alumnos)
        for w in self.parent.winfo_children():
            w.destroy()

        # Crear nueva pantalla de tutores, independiente
        TutorsFrame(self.parent, self.db_connection, student).pack(fill="both", expand=True)
