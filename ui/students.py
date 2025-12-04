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
        self.show_inactive = False  # Nuevo estado para controlar la vista

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

        # Botón para ver inactivos - NUEVO
        self.toggle_inactive_btn = ctk.CTkButton(
            self.search_frame, text="👁️ Ver Inactivos", height=40, width=120,
            fg_color="#6B7280", hover_color="#4B5563", command=self._toggle_inactive_view
        )
        self.toggle_inactive_btn.pack(side="right", padx=(5, 10))

        # Contador de alumnos - NUEVO
        self.count_label = ctk.CTkLabel(
            self.search_container, 
            text="", 
            text_color="gray60",
            font=ctk.CTkFont(size=12)
        )
        self.count_label.pack(anchor="w", padx=10, pady=(5, 0))

        # Lista
        self.list_frame = ctk.CTkScrollableFrame(left_panel, fg_color="transparent")
        self.list_frame.pack(fill="both", expand=True)

        # Panel derecho (formulario o placeholder)
        self.form_frame = ctk.CTkFrame(self.body, fg_color="transparent")
        self.form_frame.grid(row=0, column=1, sticky="nsew")

        self._show_placeholder()

    def _toggle_inactive_view(self):
        """Alterna entre ver solo activos y ver todos los alumnos"""
        self.show_inactive = not self.show_inactive
        
        if self.show_inactive:
            self.toggle_inactive_btn.configure(
                text="✅ Ver Solo Activos",
                fg_color="#10B981",
                hover_color="#059669"
            )
        else:
            self.toggle_inactive_btn.configure(
                text="👁️ Ver Inactivos",
                fg_color="#6B7280",
                hover_color="#4B5563"
            )
        
        self.load_students()

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

        # Usar active_only=False cuando show_inactive es True
        students = self.repo.get_all(active_only=not self.show_inactive)

        # Actualizar contador - NUEVO
        active_count = len([s for s in students if s.active])
        inactive_count = len([s for s in students if not s.active])
        
        if self.show_inactive:
            self.count_label.configure(
                text=f"Mostrando {len(students)} alumnos ({active_count} activos, {inactive_count} inactivos)"
            )
        else:
            self.count_label.configure(
                text=f"Mostrando {len(students)} alumnos activos"
            )

        if not students:
            no_students_text = "No hay alumnos registrados" if not self.show_inactive else "No hay alumnos (activos o inactivos)"
            ctk.CTkLabel(
                self.list_frame, text=no_students_text,
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
        
        # Pasar active_only=False cuando se muestran inactivos
        students = self.repo.search(query, active_only=not self.show_inactive)
        
        # Actualizar contador en búsqueda también
        active_count = len([s for s in students if s.active])
        inactive_count = len([s for s in students if not s.active])
        
        if self.show_inactive:
            self.count_label.configure(
                text=f"Encontrados {len(students)} alumnos ({active_count} activos, {inactive_count} inactivos)"
            )
        else:
            self.count_label.configure(
                text=f"Encontrados {len(students)} alumnos activos"
            )
        
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
        
        # Cambiar color de borde para alumnos inactivos
        if not student.active:
            card.configure(border_color="#EF4444", fg_color="#FEF2F2")

        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.pack(fill="both", expand=True, padx=15, pady=10)

        # Header con indicadores
        header_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 5))

        title_text = f"{student.enrollment}"
        if not student.active:
            title_text += " ❌ INACTIVO"

        ctk.CTkLabel(
            header_frame,
            text=title_text,
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w")

        # Información educativa si está disponible
        educational_info = []
        if student.grade_id:
            grade_name = self._get_educational_name(student.grade_id, 'grade')
            if grade_name:
                educational_info.append(f"🎓 {grade_name}")
        
        if student.group_id:
            group_name = self._get_educational_name(student.group_id, 'group')
            if group_name:
                educational_info.append(f"👥 {group_name}")
        
        if student.shift_id:
            shift_name = self._get_educational_name(student.shift_id, 'shift')
            if shift_name:
                educational_info.append(f"⏰ {shift_name}")
        
        if educational_info:
            ctk.CTkLabel(
                info_frame,
                text=" • ".join(educational_info),
                font=ctk.CTkFont(size=12),
                text_color="#3B82F6"
            ).pack(anchor="w", pady=(2, 0))

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

        # Botón activar/desactivar
        if student.active:
            ctk.CTkButton(
                action_frame, text="🚫 Desactivar", height=30, width=100,
                fg_color="#EF4444", hover_color="#DC2626",
                command=lambda s=student: self._toggle_active(s, True)
            ).pack(side="right", padx=(5, 0))
        else:
            ctk.CTkButton(
                action_frame, text="✅ Activar", height=30, width=100,
                fg_color="#10B981", hover_color="#059669",
                command=lambda s=student: self._toggle_active(s, False)
            ).pack(side="right", padx=(5, 0))

        return card

    def _toggle_active(self, student: Student, currently_active: bool):
        """Activa o desactiva un alumno con confirmación"""
        if currently_active:
            # Desactivar alumno
            if messagebox.askyesno(
                "Desactivar Alumno", 
                f"¿Desactivar al alumno '{student.first_name} {student.second_name or ''}'?\n\n"
                f"Este alumno ya no estará disponible en el sistema."
            ):
                try:
                    self.repo.deactivate(student.student_id)
                    messagebox.showinfo("Éxito", "Alumno desactivado correctamente")
                    self.load_students()
                except Exception as e:
                    messagebox.showerror("Error", f"No se pudo desactivar: {e}")
        else:
            # Activar alumno
            if messagebox.askyesno(
                "Activar Alumno", 
                f"¿Activar al alumno '{student.first_name} {student.second_name or ''}'?\n\n"
                f"Este alumno estará disponible en el sistema."
            ):
                try:
                    self.repo.activate(student.student_id)  # Necesitarás implementar este método
                    messagebox.showinfo("Éxito", "Alumno activado correctamente")
                    self.load_students()
                except Exception as e:
                    messagebox.showerror("Error", f"No se pudo activar: {e}")

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
        
        # Obtener opciones educativas
        grade_options, group_options, shift_options = self._get_educational_options()
        
        # Campos existentes
        self.enrollment_entry = ctk.CTkEntry(form, height=40, placeholder_text="Matrícula")
        self.first_name_entry = ctk.CTkEntry(form, height=40, placeholder_text="Nombre")
        self.second_name_entry = ctk.CTkEntry(form, height=40, placeholder_text="Apellido")
        
        # NUEVOS CAMPOS EDUCATIVOS
        self.grade_var = ctk.StringVar(value="")
        self.group_var = ctk.StringVar(value="") 
        self.shift_var = ctk.StringVar(value="")
        
        self.grade_cb = ctk.CTkComboBox(form, values=grade_options, variable=self.grade_var, height=40)
        self.group_cb = ctk.CTkComboBox(form, values=group_options, variable=self.group_var, height=40)
        self.shift_cb = ctk.CTkComboBox(form, values=shift_options, variable=self.shift_var, height=40)

        self.curp_entry = ctk.CTkEntry(form, height=40, placeholder_text="CURP",validate="key", validatecommand=vcmd)
        self.gender_var = ctk.StringVar(value="")
        self.gender_cb = ctk.CTkComboBox(form, values=["", "M", "F"], variable=self.gender_var, height=40)
        self.birth_date_entry = ctk.CTkEntry(form, height=40, placeholder_text="YYYY-MM-DD")
        self.pay_ref_entry = ctk.CTkEntry(form, height=40, placeholder_text="Referencia de pago")
        self.address_entry = ctk.CTkEntry(form, height=40, placeholder_text="Dirección")

        add_field("Matrícula *", self.enrollment_entry)
        add_field("Nombre *", self.first_name_entry)
        add_field("Apellido", self.second_name_entry)
        
        # Sección educativa
        ctk.CTkLabel(form, text="📚 Información Educativa", 
                    font=ctk.CTkFont(weight="bold", size=14)).grid(row=row, column=0, sticky="w", pady=(15, 5))
        row += 1
        
        add_field("Grado", self.grade_cb)
        add_field("Grupo", self.group_cb)
        add_field("Turno", self.shift_cb)
        
        # Resto de campos
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
        
        # Llenar campos educativos
        if student.grade_id:
            grade_name = self._get_educational_name(student.grade_id, 'grade')
            if grade_name:
                self.grade_var.set(f"{grade_name} ({student.grade_id})")
        
        if student.group_id:
            group_name = self._get_educational_name(student.group_id, 'group')
            if group_name:
                self.group_var.set(f"{group_name} ({student.group_id})")
        
        if student.shift_id:
            shift_name = self._get_educational_name(student.shift_id, 'shift')
            if shift_name:
                self.shift_var.set(f"{shift_name} ({student.shift_id})")
        
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
            # Extraer IDs de los combobox (formato: "Nombre (ID)")
            grade_text = self.grade_var.get()
            group_text = self.group_var.get()
            shift_text = self.shift_var.get()
            
            # Extraer el ID del texto (ej: "Primer Grado (1)" -> 1)
            grade_id = int(grade_text.split('(')[-1].rstrip(')')) if grade_text and '(' in grade_text else None
            group_id = int(group_text.split('(')[-1].rstrip(')')) if group_text and '(' in grade_text else None
            shift_id = int(shift_text.split('(')[-1].rstrip(')')) if shift_text and '(' in grade_text else None

            student_data = {
                'enrollment': self.enrollment_entry.get().strip(),
                'first_name': self.first_name_entry.get().strip(),
                'second_name': self.second_name_entry.get().strip() or None,
                'address': self.address_entry.get().strip() or None,
                'grade_id': grade_id,
                'group_id': group_id,
                'shift_id': shift_id,
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

    def _get_educational_options(self):
        """Obtiene las opciones para los combobox educativos"""
        from repositories.educational_repo import EducationalRepository
        repo = EducationalRepository(self.db_connection)
        
        grades = repo.get_all_grades()
        groups = repo.get_all_groups() 
        shifts = repo.get_all_shifts()
        
        grade_options = [""] + [f"{grade.name} ({grade.id})" for grade in grades]
        group_options = [""] + [f"{group.name} ({group.id})" for group in groups]
        shift_options = [""] + [f"{shift.name} ({shift.id})" for shift in shifts]
        
        return grade_options, group_options, shift_options   

    def _get_educational_name(self, educational_id: int, educational_type: str) -> str:
        """Obtiene el nombre de un grado, grupo o turno por su ID"""
        from repositories.educational_repo import EducationalRepository
        repo = EducationalRepository(self.db_connection)
        
        try:
            if educational_type == 'grade':
                grade = repo.get_grade_by_id(educational_id)
                return grade.name if grade else ""
            elif educational_type == 'group':
                group = repo.get_group_by_id(educational_id)
                return group.name if group else ""
            elif educational_type == 'shift':
                shift = repo.get_shift_by_id(educational_id)
                return shift.name if shift else ""
            return ""
        except Exception:
            return ""
