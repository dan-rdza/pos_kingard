# ui/products.py
from math import prod
import customtkinter as ctk
from tkinter import messagebox
from models.product import Product
from repositories.product_repo import ProductRepository

class ProductsFrame(ctk.CTkFrame):
    def __init__(self, parent, db_connection):
        super().__init__(parent, fg_color="transparent")
        self.parent = parent
        self.repo = ProductRepository(db_connection)
        self.current_sku = None

        self._create_widgets()
        self._load_products()

    def _create_widgets(self):
        # Header
        self.header = ctk.CTkFrame(self, fg_color="transparent")
        self.header.pack(fill="x", padx=10, pady=(15, 10))

        ctk.CTkLabel(
            self.header, text="📦 Productos y Servicios",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(side="left")

        ctk.CTkButton(
            self.header, text="⬅️ Volver", height=35,
            fg_color="gray50", command=self._back_to_menu
        ).pack(side="right", padx=(10,0))

        ctk.CTkButton(
            self.header, text="➕ Nuevo", height=35,
            fg_color="#2CC985", command=self._show_form_new
        ).pack(side="right")

        # Contenedor de búsqueda
        search_container = ctk.CTkFrame(self, fg_color="transparent")
        search_container.pack(fill="x", padx=(10, 10), pady=(10, 20))

        frame_width = int(self.winfo_screenwidth() * 0.6)

        self.search_frame = ctk.CTkFrame(search_container, fg_color="transparent", width=frame_width)
        self.search_frame.pack(anchor="w")

        self.q_var = ctk.StringVar()
        ent = ctk.CTkEntry(
            self.search_frame,
            textvariable=self.q_var,
            height=40,
            width=int(frame_width * 0.5),
            placeholder_text="Buscar por SKU o descripción..."
        )
        ent.pack(side="left", fill="x", expand=True, padx=(0, 10))
        ent.bind("<KeyRelease>", self._on_search)

        ctk.CTkButton(
            self.search_frame, text="🔍 Buscar", height=40,
            command=self._on_search
        ).pack(side="right")

        # Lista
        self.list_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.list_frame.pack(fill="both", expand=True)

        # Form (oculto hasta crear/editar)
        self.form_frame = ctk.CTkFrame(self, fg_color="transparent")

    def _back_to_menu(self):
        for w in self.parent.winfo_children():
            w.destroy()
        main_app = self.parent.master if hasattr(self.parent,'master') else self.parent
        if hasattr(main_app, "set_window_size"):
            main_app.set_window_size("menu")
        from ui.menu import MainMenu
        MainMenu(self.parent, self.parent.current_user).pack(fill="both", expand=True)

    # -------- LISTA --------
    def _load_products(self, query: str = ""):
        for w in self.list_frame.winfo_children():
            w.destroy()
        items = self.repo.search(query) if query else self.repo.list_all()

        if not items:
            ctk.CTkLabel(self.list_frame, text="Sin productos", text_color="gray60").pack(pady=40)
            return

        for p in items:
            self._product_card(p)

    def _product_card(self, p: Product):
        card = ctk.CTkFrame(self.list_frame, corner_radius=10, border_width=1)
        card.pack(fill="x", padx=8, pady=6)

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=12, pady=10)

        title = f"{p.sku} — {p.description}"
        if getattr(p, "is_pos_shortcut", False):
            title += "   📌 POS"

        ctk.CTkLabel(inner, text=title, font=ctk.CTkFont(weight="bold")).pack(anchor="w")
        ctk.CTkLabel(
            inner,
            text=f"💲 {p.price:.2f}  •  Impuesto: {int(p.tax_rate*100)}%  •  {p.unit}  •  {p.kind}",
            text_color="gray70"
        ).pack(anchor="w", pady=(2, 8))

        actions = ctk.CTkFrame(inner, fg_color="transparent")
        actions.pack(fill="x")

        if p.is_pos_shortcut:
            text_shortcut = "📌 Desfijar"
        else :
            text_shortcut = "📌 Fijar"

        ctk.CTkButton(
            actions, text=text_shortcut, height=30, width=90,
            fg_color="#F59E0B", command=lambda is_pos_shortcut=p.is_pos_shortcut: self._toggle_shortcut(p)
        ).pack(side="right", padx=(5,0))

        ctk.CTkButton(
            actions, text="✏️ Editar", height=28, width=90,
            fg_color="gray40", command=lambda sku=p.sku: self._show_form_edit(sku)
        ).pack(side="right", padx=(5,0))

        ctk.CTkButton(
            actions, text=("Desactivar" if p.active else "Activar"), height=28, width=110,
            fg_color="#EF4444" if p.active else "#10B981",
            command=lambda sku=p.sku, active=p.active: self._toggle_active(sku, active)
        ).pack(side="right", padx=(5,0))

    def _on_search(self, event=None):
        self._load_products(self.q_var.get().strip())

    def _toggle_shortcut(self, p: Product):
        try:
            self.repo.toggle_shortcut(p.sku, p.is_pos_shortcut)
            self._load_products()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo establecer como principal: {e}")        

    # -------- FORM --------
    def _show_form_new(self):
        self.current_sku = None
        self._show_form()

    def _show_form_edit(self, sku: str):
        self.current_sku = sku
        self._show_form(edit=True)

    def _show_form(self, edit: bool = False):
        self.list_frame.pack_forget()
        self.form_frame.pack(fill="both", expand=True)
        for w in self.form_frame.winfo_children():
            w.destroy()

        form = ctk.CTkScrollableFrame(self.form_frame, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=10, pady=20)
        form.grid_columnconfigure(0, weight=1)

        def row(label, widget):
            ctk.CTkLabel(form, text=label, font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(10,4))
            widget.pack(fill="x")

        self.sku = ctk.StringVar()
        self.desc = ctk.StringVar()
        self.price = ctk.StringVar()
        self.cost = ctk.StringVar(value="0")
        self.unit = ctk.StringVar(value="pz")
        self.kind = ctk.StringVar(value="Servicio")
        self.tax = ctk.StringVar(value="0.16")
        self.is_pos_shortcut = ctk.BooleanVar(value=False)  # ✅ ahora BooleanVar

        # Campos
        sku_e   = ctk.CTkEntry(form, textvariable=self.sku, height=40, placeholder_text="SKU (único)")
        desc_e  = ctk.CTkEntry(form, textvariable=self.desc, height=40, placeholder_text="Descripción")
        price_e = ctk.CTkEntry(form, textvariable=self.price, height=40, placeholder_text="Precio (ej. 150.00)")
        cost_e  = ctk.CTkEntry(form, textvariable=self.cost,  height=40, placeholder_text="Costo (opcional)")
        unit_e  = ctk.CTkComboBox(form, values=["pz","serv","hr","mes"], height=40, variable=self.unit)
        kind_e  = ctk.CTkComboBox(form, values=["Servicio","Producto"], height=40, variable=self.kind)
        tax_e   = ctk.CTkComboBox(form, values=["0.00","0.08","0.16"], height=40, variable=self.tax)
        is_pos_shortcut_e = ctk.CTkCheckBox(form, text="📌 Mostrar en POS", variable=self.is_pos_shortcut)

        row("SKU *", sku_e)
        row("Descripción *", desc_e)
        row("Precio *", price_e)
        row("Costo", cost_e)
        row("Unidad", unit_e)
        row("Tipo", kind_e)
        row("Impuesto", tax_e)
        row("Favorita", is_pos_shortcut_e)

        # Botones
        btns = ctk.CTkFrame(form, fg_color="transparent")
        btns.pack(fill="x", pady=(16,0))

        ctk.CTkButton(
            btns, text="↩️ Cancelar", fg_color="gray50", height=40,
            command=self._cancel_form
        ).pack(side="left")

        ctk.CTkButton(
            btns, text=("Actualizar" if edit else "Guardar"), fg_color="#2CC985", height=40,
            command=self._save
        ).pack(side="right")

        if edit and self.current_sku:
            p = self.repo.get(self.current_sku)
            if not p:
                messagebox.showerror("Edición", "Producto no encontrado")
                self._cancel_form()
                return
            self.sku.set(p.sku)
            self.desc.set(p.description)
            self.price.set(f"{p.price:.2f}")
            self.cost.set(f"{p.cost:.2f}")
            self.unit.set(p.unit or "pz")
            self.kind.set(p.kind or "Servicio")
            self.tax.set(f"{p.tax_rate:.2f}")
            self.is_pos_shortcut.set(bool(getattr(p, "is_pos_shortcut", False)))  # ✅ recuperar valor
            sku_e.configure(state="disabled")

    def _cancel_form(self):
        self.form_frame.pack_forget()
        self.list_frame.pack(fill="both", expand=True)
        self._load_products(self.q_var.get().strip())

    def _save(self):
        try:
            sku = self.sku.get().strip()
            desc = self.desc.get().strip()
            price = float(self.price.get().strip() or "0")
            cost = float(self.cost.get().strip() or "0")
            unit = self.unit.get() or "pz"
            kind = self.kind.get() or "Servicio"
            tax = float(self.tax.get().strip() or "0.16")
            is_shortcut = bool(self.is_pos_shortcut.get())

            p = Product(
                sku=sku, description=desc, price=price, cost=cost,
                unit=unit, kind=kind, tax_rate=tax,
                is_pos_shortcut=is_shortcut   # ✅ guardar valor
            )

            errors = p.validate()
            if errors:
                messagebox.showerror("Validación", "\n".join(errors))
                return

            if self.current_sku and self.current_sku == sku:
                self.repo.update(p)
                messagebox.showinfo("Productos", "Producto actualizado")
            else:
                self.repo.create(p)
                messagebox.showinfo("Productos", "Producto creado")

            self._cancel_form()
        except ValueError as e:
            messagebox.showerror("Validación", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar: {e}")

    def _toggle_active(self, sku: str, active: bool):
        if active:
            from tkinter import messagebox
            if messagebox.askyesno("Desactivar", "¿Desactivar este producto?"):
                self.repo.deactivate(sku)
        else:
            messagebox.showinfo("Activar", "Por simplicidad, la activación manual no está implementada aquí.")
        self._load_products(self.q_var.get().strip())
