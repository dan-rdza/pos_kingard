import customtkinter as ctk
from tkinter import messagebox
from models.student import Student
from repositories.student_repo import StudentRepository

class StudentsFrame(ctk.CTkFrame):
    def __init__(self, parent, db_connection):
        super().__init__(parent, fg_color="transparent")
        self.parent = parent
        self.db_connection = db_connection
        self.repo = StudentRepository(db_connection)
        self.current_student = None
        
        self.create_widgets()
        self.load_students()
    
    def create_widgets(self):
        # Header con botón de regreso
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=(10,10), pady=(0, 20))
        
        # Botón de regreso a la izquierda
        ctk.CTkButton(
            header_frame,
            text="← Volver al Menú",
            command=self.go_back_to_menu,
            height=35,
            width=120,
            fg_color="gray50",
            hover_color="gray40"
        ).pack(side="left")
        
        # Título centrado
        title_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_frame.pack(side="left", expand=True, fill="x", padx=20)
        
        ctk.CTkLabel(
            title_frame,
            text="👥 Gestión de Alumnos",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(anchor="center")
        
        # Botones de acción a la derecha
        action_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        action_frame.pack(side="right")
        
        ctk.CTkButton(
            action_frame,
            text="➕ Nuevo Alumno",
            command=self.show_new_form,
            height=35,
            fg_color="#2CC985",
            hover_color="#207A4C"
        ).pack(side="left", padx=(0, 10))
        
        # Búsqueda
        search_frame = ctk.CTkFrame(self, fg_color="transparent")
        search_frame.pack(fill="x", pady=(0, 20))
        
        self.search_var = ctk.StringVar()
        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Buscar por nombre o matrícula...",
            textvariable=self.search_var,
            height=40
        )
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.search_entry.bind("<KeyRelease>", self.on_search)
        
        ctk.CTkButton(
            search_frame,
            text="🔍 Buscar",
            command=self.on_search,
            height=40,
            width=100
        ).pack(side="right")
        
        # Lista de alumnos
        self.list_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.list_frame.pack(fill="both", expand=True)
        
        # Formulario (oculto inicialmente)
        self.form_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.create_form_widgets()
    
    def create_form_widgets(self):
        # Formulario de creación/edición
        form = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=50, pady=20)
        
        # Dos columnas
        left_col = ctk.CTkFrame(form, fg_color="transparent")
        left_col.pack(side="left", fill="both", expand=True, padx=(0, 20))
        
        right_col = ctk.CTkFrame(form, fg_color="transparent")
        right_col.pack(side="right", fill="both", expand=True)
        
        # Campos izquierda
        ctk.CTkLabel(left_col, text="Matrícula *", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 5))
        self.enrollment_entry = ctk.CTkEntry(left_col, height=40)
        self.enrollment_entry.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(left_col, text="Nombre *", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 5))
        self.first_name_entry = ctk.CTkEntry(left_col, height=40)
        self.first_name_entry.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(left_col, text="Apellido", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 5))
        self.second_name_entry = ctk.CTkEntry(left_col, height=40)
        self.second_name_entry.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(left_col, text="CURP", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 5))
        self.curp_entry = ctk.CTkEntry(left_col, height=40)
        self.curp_entry.pack(fill="x", pady=(0, 15))
        
        # Campos derecha
        ctk.CTkLabel(right_col, text="Género", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 5))
        self.gender_var = ctk.StringVar(value="")
        gender_combo = ctk.CTkComboBox(right_col, values=["", "M", "F"], variable=self.gender_var, height=40)
        gender_combo.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(right_col, text="Fecha Nacimiento", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 5))
        self.birth_date_entry = ctk.CTkEntry(right_col, height=40, placeholder_text="YYYY-MM-DD")
        self.birth_date_entry.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(right_col, text="Referencia Pago", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 5))
        self.pay_ref_entry = ctk.CTkEntry(right_col, height=40)
        self.pay_ref_entry.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(right_col, text="Dirección", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 5))
        self.address_entry = ctk.CTkEntry(right_col, height=40)
        self.address_entry.pack(fill="x", pady=(0, 20))
        
        # Botones formulario
        btn_frame = ctk.CTkFrame(form, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(20, 0))
        
        ctk.CTkButton(
            btn_frame,
            text="↩️ Cancelar",
            command=self.hide_form,
            height=40,
            fg_color="gray50"
        ).pack(side="left", padx=(0, 10))
        
        ctk.CTkButton(
            btn_frame,
            text="💾 Guardar Alumno",
            command=self.save_student,
            height=40,
            fg_color="#2CC985"
        ).pack(side="right")
    
    def load_students(self):
        # Limpiar lista actual
        for widget in self.list_frame.winfo_children():
            widget.destroy()
        
        # Cargar estudiantes
        students = self.repo.get_all()
        
        if not students:
            ctk.CTkLabel(
                self.list_frame,
                text="No hay alumnos registrados",
                text_color="gray60",
                font=ctk.CTkFont(size=14)
            ).pack(pady=50)
            return
        
        for student in students:
            self.create_student_card(student)
    
    def go_back_to_menu(self):
        """Regresar al menú principal"""
        from ui.menu import MainMenu
        # Limpiar ventana actual
        for widget in self.parent.winfo_children():
            widget.destroy()
        # Mostrar menú principal
        menu_frame = MainMenu(self.parent, self.parent.current_user)
        menu_frame.pack(fill="both", expand=True)

    def create_student_card(self, student):
        card = ctk.CTkFrame(self.list_frame, corner_radius=10, border_width=1)
        card.pack(fill="x", pady=5, padx=5)
        
        # Información principal
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.pack(fill="x", padx=15, pady=10)
        
        ctk.CTkLabel(
            info_frame,
            text=f"{student.enrollment} - {student.first_name} {student.second_name or ''}",
            font=ctk.CTkFont(weight="bold")
        ).pack(anchor="w")
        
        if student.curp:
            ctk.CTkLabel(
                info_frame,
                text=f"CURP: {student.curp}",
                font=ctk.CTkFont(size=12),
                text_color="gray60"
            ).pack(anchor="w", pady=(2, 0))
        
        # Botones de acción
        action_frame = ctk.CTkFrame(card, fg_color="transparent")
        action_frame.pack(fill="x", padx=15, pady=(5, 10))
        
        ctk.CTkButton(
            action_frame,
            text="✏️ Editar",
            command=lambda s=student: self.edit_student(s),
            height=30,
            width=80,
            fg_color="gray40"
        ).pack(side="right", padx=(5, 0))
        
        ctk.CTkButton(
            action_frame,
            text="👥 Tutores",
            command=lambda s=student: self.manage_tutors(s),
            height=30,
            width=80,
            fg_color="#3B82F6"
        ).pack(side="right", padx=(5, 0))
    
    def show_new_form(self):
        self.current_student = None
        self.clear_form()
        self.form_frame.pack(fill="both", expand=True)
        self.list_frame.pack_forget()
        self.enrollment_entry.focus()
    
    def hide_form(self):
        self.form_frame.pack_forget()
        self.list_frame.pack(fill="both", expand=True)
        self.load_students()
    
    def clear_form(self):
        self.enrollment_entry.delete(0, ctk.END)
        self.first_name_entry.delete(0, ctk.END)
        self.second_name_entry.delete(0, ctk.END)
        self.curp_entry.delete(0, ctk.END)
        self.gender_var.set("")
        self.birth_date_entry.delete(0, ctk.END)
        self.pay_ref_entry.delete(0, ctk.END)
        self.address_entry.delete(0, ctk.END)
    
    def edit_student(self, student):
        self.current_student = student
        self.fill_form(student)
        self.show_new_form()
    
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
                # Editar existente
                student_data['student_id'] = self.current_student.student_id
                student_data['active'] = self.current_student.active
                student = Student(**student_data)
                self.repo.update(student)
                messagebox.showinfo("Éxito", "Alumno actualizado correctamente")
            else:
                # Crear nuevo
                student = Student(**student_data)
                self.repo.create(student)
                messagebox.showinfo("Éxito", "Alumno creado correctamente")
            
            self.hide_form()
            
        except ValueError as e:
            messagebox.showerror("Error de validación", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar: {str(e)}")
    
    def manage_tutors(self, student):
        messagebox.showinfo("Próximamente", f"Gestión de tutores para {student.first_name}")
    
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