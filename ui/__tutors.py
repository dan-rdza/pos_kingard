# ui/tutors.py
import customtkinter as ctk
from tkinter import messagebox
from models.tutor import Tutor
from repositories.tutor_repo import TutorRepository


class TutorsFrame(ctk.CTkFrame):
    def __init__(self, parent, db_connection, student):
        super().__init__(parent, fg_color="transparent")
        self.parent = parent
        self.db_connection = db_connection
        self.repo = TutorRepository(db_connection)
        self.student = student
        self.current_tutor = None

        self._build_ui()
        self._load_tutors()

    def _build_ui(self):
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=10, pady=(15, 10))

        ctk.CTkLabel(
            header,
            text=f"👥 Tutores de {self.student.first_name} {self.student.second_name or ''}",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(side="left")

        ctk.CTkButton(
            header, text="⬅️ Volver",
            fg_color="gray50", command=self._back_to_students
        ).pack(side="right")

        ctk.CTkButton(
            header, text="➕ Nuevo",
            fg_color="#2CC985", command=self._show_form_new
        ).pack(side="right", padx=(10, 0))

        # Body (igual que ya tenías)
        self.body = ctk.CTkFrame(self, fg_color="transparent")
        self.body.pack(fill="both", expand=True)
        self.body.grid_columnconfigure(0, weight=2, uniform="col")
        self.body.grid_columnconfigure(1, weight=1, uniform="col")
        self.body.grid_rowconfigure(0, weight=1)

        self.list_frame = ctk.CTkScrollableFrame(self.body, fg_color="transparent")
        self.list_frame.grid(row=0, column=0, sticky="nsew")

        self.form_frame = ctk.CTkFrame(self.body, fg_color="transparent")
        self.form_frame.grid(row=0, column=1, sticky="nsew")

        self._show_placeholder()

    def _back(self):
        if self.on_back:
            self.on_back()

    def _show_placeholder(self):
        self._clear_container(self.form_frame)
        ph = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        ph.pack(expand=True, fill="both")
        ctk.CTkLabel(ph, text="👈 Selecciona o crea un tutor",
                     font=ctk.CTkFont(size=14), text_color="gray70").pack(expand=True)

    def _clear_container(self, container):
        for w in container.winfo_children():
            w.destroy()

    def _load_tutors(self):
        for w in self.list_frame.winfo_children():
            w.destroy()

        tutors = self.repo.get_by_student(self.student.student_id)
        if not tutors:
            ctk.CTkLabel(self.list_frame, text="No hay tutores", text_color="gray60").pack(pady=40)
            return

        self.list_frame.grid_columnconfigure((0, 1), weight=1, uniform="col")

        for idx, tutor in enumerate(tutors):
            row, col = divmod(idx, 2)
            card = self._tutor_card(tutor)
            card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

    def _tutor_card(self, tutor: Tutor):
        card = ctk.CTkFrame(self.list_frame, corner_radius=10, border_width=1)
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=12, pady=10)

        ctk.CTkLabel(inner, text=f"{tutor.first_name} {tutor.second_name or ''}", font=ctk.CTkFont(weight="bold")).pack(anchor="w")
        ctk.CTkLabel(inner, text=f"{tutor.relationship}", text_color="gray70").pack(anchor="w")

        actions = ctk.CTkFrame(inner, fg_color="transparent")
        actions.pack(fill="x", pady=(5, 0))

        ctk.CTkButton(actions, text="✏️ Editar", height=28, width=80,
                      fg_color="gray40", command=lambda: self._show_form_edit(tutor)).pack(side="right", padx=(5, 0))
        return card

    def _show_form_new(self):
        self.current_tutor = None
        self._show_form()

    def _show_form_edit(self, tutor):
        self.current_tutor = tutor
        self._show_form(tutor)

    def _show_form(self, tutor: Tutor | None = None):
        self._clear_container(self.form_frame)
        form = ctk.CTkScrollableFrame(self.form_frame, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=10, pady=20)

        title = "➕ Nuevo Tutor" if tutor is None else "✏️ Editar Tutor"
        ctk.CTkLabel(form, text=title, font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w", pady=(0, 10))

        # Campos...
        self.first_name = ctk.StringVar(value=tutor.first_name if tutor else "")
        self.second_name = ctk.StringVar(value=tutor.second_name if tutor else "")
        self.relationship = ctk.StringVar(value=tutor.relationship if tutor else "")

        ctk.CTkEntry(form, textvariable=self.first_name, placeholder_text="Nombre").pack(fill="x", pady=5)
        ctk.CTkEntry(form, textvariable=self.second_name, placeholder_text="Apellido").pack(fill="x", pady=5)
        ctk.CTkEntry(form, textvariable=self.relationship, placeholder_text="Parentesco").pack(fill="x", pady=5)

        btns = ctk.CTkFrame(form, fg_color="transparent")
        btns.pack(fill="x", pady=(15, 0))

        ctk.CTkButton(btns, text="↩️ Cancelar", fg_color="gray50", command=self._show_placeholder).pack(side="left", padx=(0, 10))
        ctk.CTkButton(btns, text="💾 Guardar", fg_color="#2CC985", command=self._save).pack(side="right")

    def _save(self):
        data = {
            "first_name": self.first_name.get().strip(),
            "second_name": self.second_name.get().strip() or None,
            "relationship": self.relationship.get().strip(),
            "student_id": self.student.student_id
        }

        try:
            if self.current_tutor:
                data["tutor_id"] = self.current_tutor.tutor_id
                self.repo.update(Tutor(**data))
                messagebox.showinfo("Éxito", "Tutor actualizado")
            else:
                self.repo.create(Tutor(**data))
                messagebox.showinfo("Éxito", "Tutor creado")

            self._show_placeholder()
            self._load_tutors()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar tutor: {e}")

    def _back_to_students(self):
        # Destruir tutores y regresar a alumnos
        for w in self.parent.winfo_children():
            w.destroy()

        from ui.students import StudentsFrame
        StudentsFrame(self.parent, self.db_connection).pack(fill="both", expand=True)
