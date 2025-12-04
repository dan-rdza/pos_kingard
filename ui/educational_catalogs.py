# ui/educational_catalogs.py
import customtkinter as ctk
from tkinter import messagebox
from repositories.educational_repo import EducationalRepository
from models.educational import Grade, Group, Shift

class EducationalCatalogsFrame(ctk.CTkFrame):
    def __init__(self, parent, db_connection):
        super().__init__(parent, fg_color="transparent")
        self.parent = parent
        self.db_connection = db_connection
        self.repo = EducationalRepository(db_connection)
        
        self._create_widgets()
        self._load_data()

    def _create_widgets(self):
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=10, pady=(15, 10))

        ctk.CTkLabel(
            header, text="🏫 Catálogos Educativos",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(side="left")

        ctk.CTkButton(
            header, text="⬅️ Volver", height=35,
            fg_color="gray50", command=self._back_to_menu
        ).pack(side="right")

        # Pestañas para los diferentes catálogos
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Crear pestañas
        self.grades_tab = self.tabview.add("Grados")
        self.groups_tab = self.tabview.add("Grupos") 
        self.shifts_tab = self.tabview.add("Turnos")
        
        # Configurar cada pestaña
        self._setup_grades_tab()
        self._setup_groups_tab()
        self._setup_shifts_tab()

    def _setup_grades_tab(self):
        # Frame principal para grados
        main_frame = ctk.CTkFrame(self.grades_tab, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Formulario para nuevo grado
        form_frame = ctk.CTkFrame(main_frame)
        form_frame.pack(fill="x", padx=10, pady=(0, 20))
        
        ctk.CTkLabel(form_frame, text="➕ Nuevo Grado", 
                    font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(10, 5))
        
        form_content = ctk.CTkFrame(form_frame, fg_color="transparent")
        form_content.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(form_content, text="Código:").grid(row=0, column=0, padx=(0, 10), pady=5, sticky="w")
        self.grade_code_entry = ctk.CTkEntry(form_content, width=100, placeholder_text="Ej: 1RO")
        self.grade_code_entry.grid(row=0, column=1, padx=(0, 20), pady=5, sticky="w")
        
        ctk.CTkLabel(form_content, text="Nombre:").grid(row=0, column=2, padx=(0, 10), pady=5, sticky="w")
        self.grade_name_entry = ctk.CTkEntry(form_content, width=200, placeholder_text="Ej: Primer Grado")
        self.grade_name_entry.grid(row=0, column=3, padx=(0, 20), pady=5, sticky="w")
        
        ctk.CTkButton(form_content, text="💾 Guardar", width=100,
                     command=self._save_grade).grid(row=0, column=4, padx=10, pady=5)
        
        # Lista de grados existentes
        self.grades_list_frame = ctk.CTkScrollableFrame(main_frame)
        self.grades_list_frame.pack(fill="both", expand=True, padx=10, pady=10)

    def _setup_groups_tab(self):
        # Similar estructura para grupos
        main_frame = ctk.CTkFrame(self.groups_tab, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        form_frame = ctk.CTkFrame(main_frame)
        form_frame.pack(fill="x", padx=10, pady=(0, 20))
        
        ctk.CTkLabel(form_frame, text="➕ Nuevo Grupo", 
                    font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(10, 5))
        
        form_content = ctk.CTkFrame(form_frame, fg_color="transparent")
        form_content.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(form_content, text="Código:").grid(row=0, column=0, padx=(0, 10), pady=5, sticky="w")
        self.group_code_entry = ctk.CTkEntry(form_content, width=100, placeholder_text="Ej: A")
        self.group_code_entry.grid(row=0, column=1, padx=(0, 20), pady=5, sticky="w")
        
        ctk.CTkLabel(form_content, text="Nombre:").grid(row=0, column=2, padx=(0, 10), pady=5, sticky="w")
        self.group_name_entry = ctk.CTkEntry(form_content, width=200, placeholder_text="Ej: Grupo A")
        self.group_name_entry.grid(row=0, column=3, padx=(0, 20), pady=5, sticky="w")
        
        ctk.CTkButton(form_content, text="💾 Guardar", width=100,
                     command=self._save_group).grid(row=0, column=4, padx=10, pady=5)
        
        self.groups_list_frame = ctk.CTkScrollableFrame(main_frame)
        self.groups_list_frame.pack(fill="both", expand=True, padx=10, pady=10)

    def _setup_shifts_tab(self):
        # Similar estructura para turnos
        main_frame = ctk.CTkFrame(self.shifts_tab, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        form_frame = ctk.CTkFrame(main_frame)
        form_frame.pack(fill="x", padx=10, pady=(0, 20))
        
        ctk.CTkLabel(form_frame, text="➕ Nuevo Turno", 
                    font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(10, 5))
        
        form_content = ctk.CTkFrame(form_frame, fg_color="transparent")
        form_content.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(form_content, text="Código:").grid(row=0, column=0, padx=(0, 10), pady=5, sticky="w")
        self.shift_code_entry = ctk.CTkEntry(form_content, width=100, placeholder_text="Ej: MAT")
        self.shift_code_entry.grid(row=0, column=1, padx=(0, 20), pady=5, sticky="w")
        
        ctk.CTkLabel(form_content, text="Nombre:").grid(row=0, column=2, padx=(0, 10), pady=5, sticky="w")
        self.shift_name_entry = ctk.CTkEntry(form_content, width=200, placeholder_text="Ej: Matutino")
        self.shift_name_entry.grid(row=0, column=3, padx=(0, 20), pady=5, sticky="w")
        
        ctk.CTkButton(form_content, text="💾 Guardar", width=100,
                     command=self._save_shift).grid(row=0, column=4, padx=10, pady=5)
        
        self.shifts_list_frame = ctk.CTkScrollableFrame(main_frame)
        self.shifts_list_frame.pack(fill="both", expand=True, padx=10, pady=10)

    def _load_data(self):
        self._load_grades()
        self._load_groups()
        self._load_shifts()

    def _load_grades(self):
        for w in self.grades_list_frame.winfo_children():
            w.destroy()
            
        grades = self.repo.get_all_grades()
        
        if not grades:
            ctk.CTkLabel(
                self.grades_list_frame, 
                text="No hay grados registrados",
                text_color="gray60"
            ).pack(pady=20)
            return
            
        for grade in grades:
            self._create_grade_card(grade)

    def _load_groups(self):
        for w in self.groups_list_frame.winfo_children():
            w.destroy()
            
        groups = self.repo.get_all_groups()
        
        if not groups:
            ctk.CTkLabel(
                self.groups_list_frame, 
                text="No hay grupos registrados",
                text_color="gray60"
            ).pack(pady=20)
            return
            
        for group in groups:
            self._create_group_card(group)

    def _load_shifts(self):
        for w in self.shifts_list_frame.winfo_children():
            w.destroy()
            
        shifts = self.repo.get_all_shifts()
        
        if not shifts:
            ctk.CTkLabel(
                self.shifts_list_frame, 
                text="No hay turnos registrados",
                text_color="gray60"
            ).pack(pady=20)
            return
            
        for shift in shifts:
            self._create_shift_card(shift)

    def _save_grade(self):
        code = self.grade_code_entry.get().strip()
        name = self.grade_name_entry.get().strip()
        
        grade = Grade(code=code, name=name)
        
        try:
            success = self.repo.create_grade(grade)
            if success:
                messagebox.showinfo("Éxito", "Grado guardado correctamente")
                self.grade_code_entry.delete(0, 'end')
                self.grade_name_entry.delete(0, 'end')
                self._load_grades()
            else:
                messagebox.showerror("Error", "El código del grado ya existe")
                
        except ValueError as e:
            messagebox.showerror("Error de validación", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar: {e}")

    def _save_group(self):
        code = self.group_code_entry.get().strip()
        name = self.group_name_entry.get().strip()
        
        group = Group(code=code, name=name)
        
        try:
            success = self.repo.create_group(group)
            if success:
                messagebox.showinfo("Éxito", "Grupo guardado correctamente")
                self.group_code_entry.delete(0, 'end')
                self.group_name_entry.delete(0, 'end')
                self._load_groups()
            else:
                messagebox.showerror("Error", "El código del grupo ya existe")
                
        except ValueError as e:
            messagebox.showerror("Error de validación", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar: {e}")

    def _save_shift(self):
        code = self.shift_code_entry.get().strip()
        name = self.shift_name_entry.get().strip()
        
        shift = Shift(code=code, name=name)
        
        try:
            success = self.repo.create_shift(shift)
            if success:
                messagebox.showinfo("Éxito", "Turno guardado correctamente")
                self.shift_code_entry.delete(0, 'end')
                self.shift_name_entry.delete(0, 'end')
                self._load_shifts()
            else:
                messagebox.showerror("Error", "El código del turno ya existe")
                
        except ValueError as e:
            messagebox.showerror("Error de validación", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar: {e}")

    def _create_grade_card(self, grade: Grade):
        card = ctk.CTkFrame(self.grades_list_frame, corner_radius=8)
        card.pack(fill="x", padx=5, pady=5)
        
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="x", padx=10, pady=8)
        
        ctk.CTkLabel(content, text=str(grade), 
                    font=ctk.CTkFont(weight="bold")).pack(side="left")
        
        ctk.CTkButton(content, text="🗑️", width=30, height=30,
                     command=lambda: self._delete_grade(grade.id)).pack(side="right")

    def _create_group_card(self, group: Group):
        card = ctk.CTkFrame(self.groups_list_frame, corner_radius=8)
        card.pack(fill="x", padx=5, pady=5)
        
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="x", padx=10, pady=8)
        
        ctk.CTkLabel(content, text=str(group), 
                    font=ctk.CTkFont(weight="bold")).pack(side="left")
        
        ctk.CTkButton(content, text="🗑️", width=30, height=30,
                     command=lambda: self._delete_group(group.id)).pack(side="right")

    def _create_shift_card(self, shift: Shift):
        card = ctk.CTkFrame(self.shifts_list_frame, corner_radius=8)
        card.pack(fill="x", padx=5, pady=5)
        
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="x", padx=10, pady=8)
        
        ctk.CTkLabel(content, text=str(shift), 
                    font=ctk.CTkFont(weight="bold")).pack(side="left")
        
        ctk.CTkButton(content, text="🗑️", width=30, height=30,
                     command=lambda: self._delete_shift(shift.id)).pack(side="right")

    def _delete_grade(self, grade_id: int):
        if messagebox.askyesno("Confirmar", "¿Eliminar este grado?"):
            try:
                success = self.repo.delete_grade(grade_id)
                if success:
                    self._load_grades()
                else:
                    messagebox.showerror("Error", "No se pudo eliminar el grado")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar: {e}")

    def _delete_group(self, group_id: int):
        if messagebox.askyesno("Confirmar", "¿Eliminar este grupo?"):
            try:
                success = self.repo.delete_group(group_id)
                if success:
                    self._load_groups()
                else:
                    messagebox.showerror("Error", "No se pudo eliminar el grupo")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar: {e}")

    def _delete_shift(self, shift_id: int):
        if messagebox.askyesno("Confirmar", "¿Eliminar este turno?"):
            try:
                success = self.repo.delete_shift(shift_id)
                if success:
                    self._load_shifts()
                else:
                    messagebox.showerror("Error", "No se pudo eliminar el turno")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar: {e}")

    def _back_to_menu(self):
        for w in self.parent.winfo_children():
            w.destroy()
        main_app = self.parent.master if hasattr(self.parent, 'master') else self.parent
        if hasattr(main_app, "set_window_size"):
            main_app.set_window_size("menu")
        from ui.menu import MainMenu
        MainMenu(self.parent, self.parent.current_user).pack(fill="both", expand=True)