import customtkinter as ctk
from tkinter import messagebox
import tkinter as tk
from tkcalendar import DateEntry
from datetime import datetime
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

        title_frame = ctk.CTkFrame(self, fg_color='transparent', border_width = 1   )
        title_frame.pack(fill='x', padx=(10,10), pady=(15, 15), )

        # Título principal arriba
        title_label = ctk.CTkLabel(
            title_frame,
            text="👥 Gestión de Alumnos",
            font=ctk.CTkFont(size=22, weight="bold")
        )
        title_label.pack(pady=(15, 15))

        # Botones de acciones
        action_bar = ctk.CTkFrame(self, fg_color="transparent")
        action_bar.pack(fill="x", padx=(10, 10), pady=(15, 15))

        ctk.CTkButton(
            action_bar,
            text="← Volver al Menú",
            command=self.go_back_to_menu,
            height=35,
            width=140,
            fg_color="gray50",
            hover_color="gray40"
        ).pack(side="left")

        ctk.CTkButton(
            action_bar,
            text="➕ Nuevo Alumno",
            command=self.show_new_form,
            height=35,
            fg_color="#2CC985",
            hover_color="#207A4C"
        ).pack(side="right")        
        
        # Búsqueda
        search_frame = ctk.CTkFrame(self, fg_color="transparent")
        search_frame.pack(fill="x", padx=(10, 10), pady=(10, 20))
        
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
        form = ctk.CTkScrollableFrame(self.form_frame, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=10, pady=20)

        # Configurar grid con una sola columna
        form.grid_columnconfigure(0, weight=1)
        
        # Lista de campos en el orden deseado
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
            # Label
            label = ctk.CTkLabel(form, text=label_text, font=ctk.CTkFont(weight="bold"))
            label.grid(row=i*2, column=0, sticky="w", pady=(10 if i == 0 else 0, 5))
            
            # Field
            if field_type == "combobox":
                var = ctk.StringVar(value="")
                field = ctk.CTkComboBox(form, values=options, variable=var, height=40)
                setattr(self, attr_name, var)
            else:
                field = ctk.CTkEntry(form, height=40, placeholder_text=options)
                setattr(self, attr_name, field)
            
            field.grid(row=i*2 + 1, column=0, sticky="ew", pady=(0, 10))
        
        # Botones
        btn_frame = ctk.CTkFrame(form, fg_color="transparent")
        btn_frame.grid(row=len(fields)*2, column=0, sticky="ew", pady=(20, 0))
        
        btn_frame.grid_columnconfigure(0, weight=1)
        btn_frame.grid_columnconfigure(1, weight=0)
        
        cancel_btn = ctk.CTkButton(
            btn_frame,
            text="↩️ Cancelar",
            command=self.hide_form,
            height=40,
            fg_color="gray50"
        )
        cancel_btn.grid(row=0, column=0, sticky="w", padx=(0, 10))
        
        save_btn = ctk.CTkButton(
            btn_frame,
            text="💾 Guardar Alumno",
            command=self.save_student,
            height=40,
            fg_color="#2CC985"
        )
        save_btn.grid(row=0, column=1, sticky="e")
        
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
        # Limpiar ventana actual
        for widget in self.parent.winfo_children():
            widget.destroy()
        
        # Acceder a la ventana principal (App) correctamente
        main_app = self.parent.master if hasattr(self.parent, 'master') else self.parent
        if hasattr(main_app, 'set_window_size'):
            main_app.set_window_size("menu")
        
        # Importar después de configurar tamaño
        from ui.menu import MainMenu
        
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
        # Limpiar entries
        self.enrollment_entry.delete(0, ctk.END)
        self.first_name_entry.delete(0, ctk.END)
        self.second_name_entry.delete(0, ctk.END)
        self.curp_entry.delete(0, ctk.END)
        self.birth_date_entry.delete(0, ctk.END)
        self.pay_ref_entry.delete(0, ctk.END)
        self.address_entry.delete(0, ctk.END)
        
        # Limpiar combobox
        self.gender_var.set("")
    
    def edit_student(self, student):
        self.current_student = student
        print(self.current_student)
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