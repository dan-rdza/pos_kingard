# ui/students.py
import customtkinter as ctk
from tkinter import messagebox
from models.student import Student
from repositories.student_repo import StudentRepository
from repositories.tutor_repo import TutorRepository  # solo para mostrar tutor principal
from ui.tutors import TutorsPanel

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
        # Header / Título (corregido: ahora es atributo de instancia)
        self.title_frame = ctk.CTkFrame(self, fg_color='transparent')
        self.title_frame.pack(fill='x', padx=(10, 10), pady=(15, 15))

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

        # Contenedor ancho completo
        search_container = ctk.CTkFrame(self, fg_color="transparent")
        search_container.pack(fill="x", padx=(10, 10), pady=(10, 20))

        # Frame con 60% de ancho dentro del contenedor
        frame_width = int(self.winfo_screenwidth() * 0.6)

        self.search_frame = ctk.CTkFrame(search_container, fg_color="transparent", width=frame_width)
        self.search_frame.pack(anchor="w")  # "w" izquierda, "center" centro, "e" derecha

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
        self.list_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.list_frame.pack(fill="both", expand=True)
        
        self.tutors_container = None
        
        # Formulario
        self.form_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.create_form_widgets()

    def create_form_widgets(self):
        form = ctk.CTkScrollableFrame(self.form_frame, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=10, pady=20)
        form.grid_columnconfigure(0, weight=1)

        fields = [
            ("Matrícula *", "enrollment_entry", "entry", ""),
            ("Nombre *", "first_name_entry", "entry", ""),
            ("Apellido", "second_name_entry", "entry", ""),
            ("CURP", "curp_entry", "entry", ""),
            ("Género", "gender_var", "combobox", ["", "M", "F"]),
            ("Fecha Nacimiento", "birth_date_entry", "entry", "YYYY-MM-DD"),
            ("Referencia Pago", "pay_ref_entry", "entry", ""),
            ("Dirección", "address_entry", "entry", "")
        ]

        for i, (label_text, attr_name, field_type, options) in enumerate(fields):
            ctk.CTkLabel(form, text=label_text, font=ctk.CTkFont(weight="bold")).grid(
                row=i*2, column=0, sticky="w", pady=(10 if i == 0 else 0, 5)
            )
            if field_type == "combobox":
                var = ctk.StringVar(value="")
                field = ctk.CTkComboBox(form, values=options, variable=var, height=40)
                setattr(self, attr_name, var)
            else:
                field = ctk.CTkEntry(form, height=40, placeholder_text=options)
                setattr(self, attr_name, field)
            field.grid(row=i*2 + 1, column=0, sticky="ew", pady=(0, 10))

        btn_frame = ctk.CTkFrame(form, fg_color="transparent")
        btn_frame.grid(row=len(fields)*2, column=0, sticky="ew", pady=(20, 0))
        btn_frame.grid_columnconfigure(0, weight=1)
        btn_frame.grid_columnconfigure(1, weight=0)

        ctk.CTkButton(
            btn_frame, text="↩️ Cancelar",
            command=self.hide_form, height=40, fg_color="gray50"
        ).grid(row=0, column=0, sticky="w", padx=(0, 10))

        ctk.CTkButton(
            btn_frame, text="💾 Guardar Alumno",
            command=self.save_student, height=40, fg_color="#2CC985"
        ).grid(row=0, column=1, sticky="e")

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

        for student in students:
            self.create_student_card(student)

    def on_search(self, event=None):
        query = self.search_var.get().strip()
        if not query:
            self.load_students()
            return
        
        # Limpiar lista
        for widget in self.list_frame.winfo_children():
            widget.destroy()
        
        # Buscar estudiantes
        students = self.repo.search(query)
        
        if not students:
            ctk.CTkLabel(
                self.list_frame,
                text=f"No se encontraron alumnos para '{query}'",
                text_color="gray60",
                font=ctk.CTkFont(size=14)
            ).pack(pady=50)
            return
        
        for student in students:
            self.create_student_card(student)


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
        card.pack(fill="x", pady=5, padx=5)

        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.pack(fill="x", padx=15, pady=10)

        ctk.CTkLabel(
            info_frame,
            text=f"{student.enrollment} - {student.first_name} {student.second_name or ''}",
            font=ctk.CTkFont(weight="bold")
        ).pack(anchor="w")

        if student.curp:
            ctk.CTkLabel(
                info_frame, text=f"CURP: {student.curp}",
                font=ctk.CTkFont(size=12), text_color="gray60"
            ).pack(anchor="w", pady=(2, 0))

        # tutor principal (solo lectura aquí)
        tutors = self.tutor_repo.get_by_student(student.student_id)
        primary_tutor = next((t for t in tutors if t.is_primary), None)
        if primary_tutor:
            ctk.CTkLabel(
                info_frame,
                text=f"📞 {primary_tutor.full_name()} ({primary_tutor.relationship})",
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

    def show_new_form(self):
        self.current_student = None
        self.clear_form()
        self.form_frame.pack(fill="both", expand=True)
        self.list_frame.pack_forget()
        self.title_frame.pack_forget()
        self.search_frame.pack_forget()        
        self.enrollment_entry.focus()

    def hide_form(self):
        self.form_frame.pack_forget()
        self.title_frame.pack(fill='x', padx=(10, 10), pady=(15, 15))
        self.search_frame.pack(fill="x", padx=(10, 10), pady=(15, 15))
        self.list_frame.pack(fill="both", expand=True)
        self.load_students()

    def clear_form(self):
        self.enrollment_entry.delete(0, ctk.END)
        self.first_name_entry.delete(0, ctk.END)
        self.second_name_entry.delete(0, ctk.END)
        self.curp_entry.delete(0, ctk.END)
        self.birth_date_entry.delete(0, ctk.END)
        self.pay_ref_entry.delete(0, ctk.END)
        self.address_entry.delete(0, ctk.END)
        self.gender_var.set("")

    def edit_student(self, student):
        self.current_student = student
        self.show_new_form()
        self.fill_form(student)

    def fill_form(self, student):
        self.clear_form()
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

 # 🔹 Abrir tutores como panel embebido (capa propia)
    def manage_tutors(self, student):
        self.current_student = student
        # ocultar UI de alumnos
        self.list_frame.pack_forget()
        self.search_frame.pack_forget()
        self.title_frame.pack_forget()

        # montar panel si no existe
        if self.tutors_container is None:
            self.tutors_container = ctk.CTkFrame(self, fg_color="transparent")
            self.tutors_container.pack(fill="both", expand=True, padx=10, pady=10)

        # limpiar contenedor y montar panel
        for w in self.tutors_container.winfo_children():
            w.destroy()

        def _back():
            # destruir panel y restaurar alumnos
            for w in self.tutors_container.winfo_children():
                w.destroy()
            self.tutors_container.pack_forget()
            self.tutors_container = None
            self.title_frame.pack(fill='x', padx=(10,10), pady=(15, 15))
            self.search_frame.pack(fill="x", padx=(10,10), pady=(15, 15))
            self.list_frame.pack(fill="both", expand=True)
            self.load_students()  # refresca para mostrar tutor principal

        panel = TutorsPanel(self.tutors_container, self.db_connection, student, on_back=_back)
        panel.pack(fill="both", expand=True)
