# ui/tutors.py
import customtkinter as ctk
from tkinter import messagebox, BooleanVar
from models.tutor import Tutor
from repositories.tutor_repo import TutorRepository

class TutorsPanel(ctk.CTkFrame):
    """
    Panel embebido para gestionar tutores de un alumno.
    Se monta dentro de StudentsFrame sin tocar main.py.
    """
    def __init__(self, parent, db_connection, student, on_back):
        super().__init__(parent, fg_color="transparent")
        self.db = db_connection
        self.repo = TutorRepository(self.db)
        self.student = student
        self.on_back = on_back

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
            text=f"👥 Tutores de {self.student.first_name} {self.student.second_name}",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(side="left")

        ctk.CTkButton(
            header, text="⬅️ Volver", height=35, fg_color="gray50",
            command=self.on_back
        ).pack(side="right", padx=(10, 0))

        ctk.CTkButton(
            header, text="➕ Nuevo Tutor", height=35, fg_color="#2CC985",
            command=lambda: self._show_form()
        ).pack(side="right")

        # Contenido: lista y formulario (mutuamente excluyentes)
        self.body = ctk.CTkFrame(self, fg_color="transparent")
        self.body.pack(fill="both", expand=True)

        self.list_frame = ctk.CTkScrollableFrame(self.body, fg_color="transparent")
        self.list_frame.pack(fill="both", expand=True)

        self.form_frame = ctk.CTkFrame(self.body, fg_color="transparent")
        # se muestra sólo cuando se crea/edita

    def _clear_container(self, container):
        for w in container.winfo_children():
            w.destroy()

    # ---------- LISTA ----------
    def _load_tutors(self):
        self.form_frame.forget()
        self.list_frame.pack(fill="both", expand=True)

        self._clear_container(self.list_frame)
        tutors = self.repo.get_by_student(self.student.student_id)
        if not tutors:
            ctk.CTkLabel(
                self.list_frame, text="No hay tutores registrados",
                text_color="gray60", font=ctk.CTkFont(size=14)
            ).pack(pady=50)
            return

        for t in tutors:
            self._tutor_card(t)

    def _tutor_card(self, tutor: Tutor):
        card = ctk.CTkFrame(self.list_frame, corner_radius=10, border_width=1)
        card.pack(fill="x", pady=5, padx=5)

        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="x", padx=15, pady=10)

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
            actions, text="✏️ Editar", height=28, width=90, fg_color="gray40",
            command=lambda t=tutor: self._show_form(t)
        ).pack(side="right", padx=(5, 0))

        ctk.CTkButton(
            actions, text="🗑️ Eliminar", height=28, width=90, fg_color="#EF4444",
            command=lambda t=tutor: self._delete(t)
        ).pack(side="right", padx=(5, 0))

    # ---------- FORM (embebido, sin modal) ----------
    def _show_form(self, tutor: Tutor | None = None):
        self.current_tutor = tutor
        self.list_frame.forget()
        self.form_frame.pack(fill="both", expand=True)
        self._clear_container(self.form_frame)

        form = ctk.CTkScrollableFrame(self.form_frame, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=10, pady=20)

        tutor_title = ctk.CTkLabel(form, text="Nuevo Tutor", font=ctk.CTkFont(size=20, weight="bold"))
        tutor_title.grid(row=0, column=0, sticky = "w", pady=10)

        form.grid_columnconfigure(0, weight=1)

        rows = [0]
        def row(label_text):            
            i = len(rows)
            ctk.CTkLabel(form, text=label_text, font=ctk.CTkFont(weight="bold")).grid(
                row=i*2, column=0, sticky="w", pady=(10 if i == 0 else 6, 4)
            )
            rows.append(i);            
            return i

        i = row("Nombre *");        self.t_first = ctk.CTkEntry(form, height=40);   self.t_first.grid(row=i*2+1, column=0, sticky="ew")
        i = row("Apellido");        self.t_second = ctk.CTkEntry(form, height=40);  self.t_second.grid(row=i*2+1, column=0, sticky="ew")
        i = row("Parentesco *");    self.t_rel = ctk.CTkComboBox(form, values=["Padre","Madre","Tutor","Abuelo","Otro"], height=40); self.t_rel.grid(row=i*2+1, column=0, sticky="ew")
        i = row("Teléfono");        self.t_phone = ctk.CTkEntry(form, height=40);   self.t_phone.grid(row=i*2+1, column=0, sticky="ew")
        i = row("Email");           self.t_email = ctk.CTkEntry(form, height=40);   self.t_email.grid(row=i*2+1, column=0, sticky="ew")
        i = row("Tutor Principal"); self.t_primary_var = BooleanVar(value=False);   self.t_primary = ctk.CTkCheckBox(form, text="", variable=self.t_primary_var); self.t_primary.grid(row=i*2+1, column=0, sticky="w", pady=(0, 8))

        btns = ctk.CTkFrame(form, fg_color="transparent")
        btns.grid(row=len(rows)*2, column=0, sticky="ew", pady=(12, 0))

        ctk.CTkButton(btns, text="↩️ Cancelar", fg_color="gray50",
                      command=self._load_tutors, height=35).pack(side="left", padx=(0, 10))
        ctk.CTkButton(btns, text=("Guardar" if tutor is None else "Actualizar"),
                      fg_color="#2CC985", command=self._save, height=35).pack(side="right")

        if tutor:
            self.t_first.insert(0, tutor.first_name or "")
            self.t_second.insert(0, tutor.second_name or "")
            self.t_rel.set(tutor.relationship or "")
            self.t_phone.insert(0, tutor.phone or "")
            self.t_email.insert(0, tutor.email or "")
            self.t_primary_var.set(bool(tutor.is_primary))

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
            if not data['first_name'] or not data['relationship']:
                messagebox.showerror("Validación", "Nombre y parentesco son obligatorios")
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

            self._load_tutors()
            messagebox.showinfo("Éxito", "Tutor guardado correctamente")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar: {e}")

    def _delete(self, tutor: Tutor):
        if messagebox.askyesno("Confirmar", "¿Eliminar este tutor?"):
            try:
                self.repo.delete(tutor.tutor_id)
                self._load_tutors()
                messagebox.showinfo("Éxito", "Tutor eliminado")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar: {e}")

    def _set_primary(self, tutor: Tutor):
        try:
            self.repo.set_primary(tutor.tutor_id, self.student.student_id)
            self._load_tutors()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo establecer como principal: {e}")
