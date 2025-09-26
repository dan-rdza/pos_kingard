# ui/tutors.py
from sys import maxsize
import customtkinter as ctk
import re
from tkinter import messagebox, BooleanVar
from models.tutor import Tutor
from repositories.tutor_repo import TutorRepository
from shared.utils import char_limit_validator


class TutorsFrame(ctk.CTkFrame):
    """
    Panel embebido para gestionar tutores de un alumno.
    Se monta dentro de StudentsFrame sin tocar main.py.
    """
    def __init__(self, parent, db_connection, student):
        super().__init__(parent, fg_color="transparent")
        self.parent = parent
        self.db_connection = db_connection
        self.repo = TutorRepository(db_connection)
        self.student = student
        self.current_tutor = None

        self._build_ui()
        self._load_tutors()

    # ---------- UI ----------
    def _build_ui(self):
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(
            header,
            text=f"👥 Tutores de {self.student.first_name} {self.student.second_name or ''}",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(side="left")

        ctk.CTkButton(
            header, text="⬅️ Volver", height=35, fg_color="gray50",
            command=self._back_to_students
        ).pack(side="right", padx=(10, 0))

        ctk.CTkButton(
            header, text="➕ Nuevo Tutor", height=35, fg_color="#2CC985",
            command=lambda: self._show_form()
        ).pack(side="right")

        # Contenido: lista (izquierda) y panel derecho
        self.body = ctk.CTkFrame(self, fg_color="transparent")
        self.body.pack(fill="both", expand=True)

        self.body.grid_columnconfigure(0, weight=2, uniform="col")
        self.body.grid_columnconfigure(1, weight=1, uniform="col")
        self.body.grid_rowconfigure(0, weight=1)

        # Lista
        self.list_frame = ctk.CTkScrollableFrame(self.body, fg_color="transparent")
        self.list_frame.grid(row=0, column=0, sticky="nsew")

        # Panel derecho
        self.form_frame = ctk.CTkFrame(self.body, fg_color="transparent")
        self.form_frame.grid(row=0, column=1, sticky="nsew")

        # 🔹 Placeholder inicial
        self.placeholder = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        self.placeholder.pack(expand=True, fill="both")
        ctk.CTkLabel(
            self.placeholder,
            text="👈 Selecciona un tutor o da clic en ➕ Nuevo",
            font=ctk.CTkFont(size=14),
            text_color="gray70"
        ).pack(expand=True)

    def _clear_container(self, container):
        for w in container.winfo_children():
            w.destroy()

    # ---------- LISTA ----------
    def _load_tutors(self):
        self._clear_container(self.list_frame)
        tutors = self.repo.get_by_student(self.student.student_id)
        if not tutors:
            ctk.CTkLabel(
                self.list_frame, text="No hay tutores registrados",
                text_color="gray60", font=ctk.CTkFont(size=14)
            ).pack(pady=50)
            return

        self.list_frame.grid_columnconfigure((0, 1), weight=1, uniform="col")

        for idx, t in enumerate(tutors):
            row = idx // 2
            col = idx % 2
            card = self._tutor_card(t)
            card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

        # Restaurar placeholder si no hay formulario
        if not self.current_tutor:
            self._show_placeholder()

    def _tutor_card(self, tutor: Tutor):
        card = ctk.CTkFrame(self.list_frame, corner_radius=10, border_width=1)

        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=15, pady=10)

        head = ctk.CTkFrame(content, fg_color="transparent")
        head.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            head, text=f"{tutor.full_name()} ({tutor.relationship})",
            font=ctk.CTkFont(weight="bold")
        ).pack(side="left")

        if tutor.is_primary:
            ctk.CTkLabel(
                head, text="⭐ Principal",
                text_color="#F59E0B", font=ctk.CTkFont(size=12, weight="bold")
            ).pack(side="right", padx=(10, 0))

        if tutor.phone:
            ctk.CTkLabel(content, text=f"📞 {tutor.phone}",
                         font=ctk.CTkFont(size=12), text_color="gray60").pack(anchor="w")
        if tutor.email:
            ctk.CTkLabel(content, text=f"📧 {tutor.email}",
                         font=ctk.CTkFont(size=12), text_color="gray60").pack(anchor="w", pady=(0, 8))

        actions = ctk.CTkFrame(content, fg_color="transparent")
        actions.pack(fill="x")

        if not tutor.is_primary:
            ctk.CTkButton(
                actions, text="⭐ Hacer Principal", height=28, width=140, fg_color="#F59E0B",
                command=lambda t=tutor: self._set_primary(t)
            ).pack(side="right", padx=(5, 0))

        ctk.CTkButton(
            actions, text="✏️ Seleccionar", height=28, width=90, fg_color="gray40",
            command=lambda t=tutor: self._show_form(t)
        ).pack(side="right", padx=(5, 0))

        ctk.CTkButton(
            actions, text="🗑️ Eliminar", height=28, width=90, fg_color="#EF4444",
            command=lambda t=tutor: self._delete(t)
        ).pack(side="right", padx=(5, 0))

        return card

    # ---------- PLACEHOLDER ----------
    def _show_placeholder(self):
        self._clear_container(self.form_frame)
        self.placeholder = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        self.placeholder.pack(expand=True, fill="both")
        ctk.CTkLabel(
            self.placeholder,
            text="👈 Selecciona un tutor o da clic en ➕ Nuevo",
            font=ctk.CTkFont(size=14),
            text_color="gray70"
        ).pack(expand=True)

    # ---------- FORM ----------
    def _show_form(self, tutor: Tutor | None = None):
        self.current_tutor = tutor
        self._clear_container(self.form_frame)

        form = ctk.CTkScrollableFrame(self.form_frame, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=10, pady=20)
        form.grid_columnconfigure(0, weight=1)

        title_text = "➕ Nuevo Tutor" if tutor is None else "✏️ Editar Tutor"
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

        vcmd = (self.register(char_limit_validator(10)), '%P')

        self.t_first = ctk.CTkEntry(form, height=40, placeholder_text="Nombre(s)")
        self.t_second = ctk.CTkEntry(form, height=40, placeholder_text="Apellido(s)")
        self.t_rel = ctk.CTkComboBox(form, values=["Padre", "Madre", "Tutor", "Abuelo", "Otro"], height=40)
        self.t_phone = ctk.CTkEntry(form, height=40, placeholder_text="Teléfono (10 dígitos)", validate="key", validatecommand=vcmd)
        self.t_email = ctk.CTkEntry(form, height=40, placeholder_text="Correo electrónico")
        self.t_primary_var = BooleanVar(value=False)
        self.t_primary = ctk.CTkCheckBox(form, text="⭐ Tutor Principal", variable=self.t_primary_var)

        add_field("Nombre *", self.t_first)
        add_field("Apellido", self.t_second)
        add_field("Parentesco *", self.t_rel)
        add_field("Teléfono", self.t_phone)
        add_field("Correo", self.t_email)
        add_field("Principal", self.t_primary)

        btns = ctk.CTkFrame(form, fg_color="transparent")
        btns.grid(row=row, column=0, sticky="ew", pady=(15, 0))

        ctk.CTkButton(btns, text="↩️ Cancelar", fg_color="gray50", height=40,
                      command=self._cancel_form).pack(side="left", padx=(0, 10))

        btn_text = "💾 Guardar" if tutor is None else "🔄 Actualizar"
        btn_color = "#2CC985" if tutor is None else "#3B82F6"
        ctk.CTkButton(btns, text=btn_text, fg_color=btn_color, height=40,
                      command=self._save).pack(side="right")

        if tutor:
            self.t_first.insert(0, tutor.first_name or "")
            self.t_second.insert(0, tutor.second_name or "")
            self.t_rel.set(tutor.relationship or "")
            self.t_phone.insert(0, tutor.phone or "")
            self.t_email.insert(0, tutor.email or "")
            self.t_primary_var.set(bool(tutor.is_primary))

    def _cancel_form(self):
        self.current_tutor = None
        self._show_placeholder()

    # ---------- ACCIONES ----------
    def _save(self):
        try:
            data = {
                'student_id': self.student.student_id,
                'first_name': self.t_first.get().strip(),
                'second_name': self.t_second.get().strip() or None,
                'relationship': self.t_rel.get().strip(),
                'phone': self.t_phone.get().strip() or None,
                'email': self.t_email.get().strip() or None,
                'is_primary': bool(self.t_primary_var.get())
            }
            if not data['first_name'] or len(data['first_name']) < 2:
                messagebox.showerror("Validación", "El nombre debe tener al menos 2 caracteres")
                return
            if not data['relationship']:
                messagebox.showerror("Validación", "El parentesco es obligatorio")
                return
            if data['phone'] and (not data['phone'].isdigit() or len(data['phone']) != 10):
                messagebox.showerror("Validación", "El teléfono debe tener 10 dígitos")
                return
            if data['email'] and not re.match(r"[^@]+@[^@]+\.[^@]+", data['email']):
                messagebox.showerror("Validación", "Correo inválido")
                return

            if self.current_tutor:
                data['tutor_id'] = self.current_tutor.tutor_id
                tutor = Tutor(**data)
                self.repo.update(tutor)
            else:
                tutor = Tutor(**data)
                self.repo.create(tutor)

            if data['is_primary']:
                self.repo.set_primary(tutor.tutor_id, self.student.student_id)

            self.current_tutor = None
            self._load_tutors()
            self._show_placeholder()
            messagebox.showinfo("Éxito", "Tutor guardado correctamente")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar: {e}")

    def _delete(self, tutor: Tutor):
        if messagebox.askyesno("Confirmar", "¿Eliminar este tutor?"):
            try:
                self.repo.delete(tutor.tutor_id)
                self._load_tutors()
                self._show_placeholder()
                messagebox.showinfo("Éxito", "Tutor eliminado")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar: {e}")

    def _set_primary(self, tutor: Tutor):
        try:
            self.repo.set_primary(tutor.tutor_id, self.student.student_id)
            self._load_tutors()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo establecer como principal: {e}")

    def _back_to_students(self):
        # Destruir tutores y regresar a alumnos
        for w in self.parent.winfo_children():
            w.destroy()

        from ui.students import StudentsFrame
        StudentsFrame(self.parent, self.db_connection).pack(fill="both", expand=True)