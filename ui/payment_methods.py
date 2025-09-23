# ui/payment_methods.py
import customtkinter as ctk
from tkinter import messagebox
from repositories.payment_method_repo import PaymentMethodRepository


class PaymentMethodsFrame(ctk.CTkFrame):
    def __init__(self, parent, db_connection):
        super().__init__(parent, fg_color="transparent")
        self.parent = parent
        self.repo = PaymentMethodRepository(db_connection)
        self.current_id = None
        self._build_ui()
        self._load_methods()

    def _build_ui(self):
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=10, pady=(15, 10))

        ctk.CTkLabel(header, text="💳 Métodos de Pago", font=ctk.CTkFont(size=20, weight="bold")).pack(side="left")

        ctk.CTkButton(
            header, text="⬅️ Volver", height=35, fg_color="gray50",
            command=self._back_to_menu
        ).pack(side="right", padx=(10, 0))

        ctk.CTkButton(
            header, text="➕ Nuevo", height=35, fg_color="#2CC985",
            command=self._show_form_new
        ).pack(side="right")

        # Body (lista izquierda + form derecha)
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

    def _show_placeholder(self):
        self._clear_container(self.form_frame)
        ph = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        ph.pack(expand=True, fill="both")
        ctk.CTkLabel(ph, text="👈 Selecciona o crea un método de pago",
                     font=ctk.CTkFont(size=14), text_color="gray70").pack(expand=True)

    def _clear_container(self, container):
        for w in container.winfo_children():
            w.destroy()

    def _load_methods(self):
        for w in self.list_frame.winfo_children():
            w.destroy()

        methods = self.repo.list_all(active_only=False)
        if not methods:
            ctk.CTkLabel(self.list_frame, text="No hay métodos registrados", text_color="gray60").pack(pady=40)
            return

        self.list_frame.grid_columnconfigure((0, 1), weight=1, uniform="col")

        for idx, pm in enumerate(methods):
            row, col = divmod(idx, 2)
            card = self._method_card(pm)
            card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

    def _method_card(self, pm):
        card = ctk.CTkFrame(self.list_frame, corner_radius=10, border_width=1)
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=12, pady=10)

        status = "🟢 Activo" if pm["active"] else "⚪ Inactivo"
        ctk.CTkLabel(inner, text=f"{pm['name']} ({pm['code']})", font=ctk.CTkFont(weight="bold")).pack(anchor="w")
        ctk.CTkLabel(inner, text=status, text_color="gray70").pack(anchor="w")

        actions = ctk.CTkFrame(inner, fg_color="transparent")
        actions.pack(fill="x", pady=(5, 0))

        ctk.CTkButton(actions, text="✏️ Editar", height=28, width=80, fg_color="gray40",
                      command=lambda: self._show_form_edit(pm)).pack(side="right", padx=(5, 0))
        if pm["active"]:
            ctk.CTkButton(actions, text="🚫 Desactivar", height=28, width=100, fg_color="#EF4444",
                          command=lambda: self._deactivate(pm)).pack(side="right", padx=(5, 0))
        return card

    def _show_form_new(self):
        self.current_id = None
        self._show_form()

    def _show_form_edit(self, pm):
        self.current_id = pm["id"]
        self._show_form(pm)

    def _show_form(self, pm=None):
        self._clear_container(self.form_frame)
        form = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=10, pady=20)
        form.grid_columnconfigure(0, weight=1)

        title = "➕ Nuevo Método" if pm is None else "✏️ Editar Método"
        ctk.CTkLabel(form, text=title, font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, sticky="w", pady=(0, 10))

        row = 1
        self.name_var = ctk.StringVar(value=pm["name"] if pm else "")
        self.code_var = ctk.StringVar(value=pm["code"] if pm else "")
        self.active_var = ctk.BooleanVar(value=pm["active"] if pm else True)

        def add_field(label, widget):
            nonlocal row
            ctk.CTkLabel(form, text=label, font=ctk.CTkFont(weight="bold")).grid(row=row, column=0, sticky="w", pady=(8, 2))
            row += 1
            widget.grid(row=row, column=0, sticky="ew", pady=(0, 5))
            row += 1

        add_field("Nombre *", ctk.CTkEntry(form, textvariable=self.name_var, height=40))
        add_field("Código *", ctk.CTkEntry(form, textvariable=self.code_var, height=40))
        add_field("Activo", ctk.CTkCheckBox(form, text="Disponible", variable=self.active_var))

        btns = ctk.CTkFrame(form, fg_color="transparent")
        btns.grid(row=row, column=0, sticky="ew", pady=(15, 0))

        ctk.CTkButton(btns, text="↩️ Cancelar", fg_color="gray50", height=40, command=self._show_placeholder).pack(side="left", padx=(0, 10))
        ctk.CTkButton(btns, text="💾 Guardar", fg_color="#2CC985", height=40, command=self._save).pack(side="right")

    def _save(self):
        name = self.name_var.get().strip()
        code = self.code_var.get().strip()
        active = self.active_var.get()

        if not name or not code:
            messagebox.showerror("Validación", "Nombre y código son obligatorios")
            return

        try:
            if self.current_id:
                self.repo.update(self.current_id, name, code, active)
                messagebox.showinfo("Éxito", "Método actualizado")
            else:
                self.repo.create(name, code)
                messagebox.showinfo("Éxito", "Método creado")
            self._show_placeholder()
            self._load_methods()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar: {e}")

    def _deactivate(self, pm):
        if messagebox.askyesno("Confirmar", f"¿Desactivar {pm['name']}?"):
            try:
                self.repo.deactivate(pm["id"])
                self._load_methods()
                messagebox.showinfo("Éxito", "Método desactivado")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo desactivar: {e}")

    def _back_to_menu(self):
        for w in self.parent.winfo_children():
            w.destroy()
        main_app = self.parent.master if hasattr(self.parent, "master") else self.parent
        if hasattr(main_app, "set_window_size"):
            main_app.set_window_size("menu")
        from ui.menu import MainMenu
        MainMenu(self.parent, self.parent.current_user).pack(fill="both", expand=True)
