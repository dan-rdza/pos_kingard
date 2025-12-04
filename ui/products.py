# ui/products.py
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
        self.show_inactive = False 
        
        self._create_widgets()
        self._load_products()

    def _create_widgets(self):
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=10, pady=(15, 10))

        ctk.CTkLabel(
            header, text="📦 Productos y Servicios",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(side="left")

        ctk.CTkButton(
            header, text="⬅️ Volver", height=35,
            fg_color="gray50", command=self._back_to_menu
        ).pack(side="right", padx=(10, 0))

        ctk.CTkButton(
            header, text="➕ Nuevo", height=35,
            fg_color="#2CC985", command=self._show_form_new
        ).pack(side="right")

        # Body con 2 paneles
        self.body = ctk.CTkFrame(self, fg_color="transparent")
        self.body.pack(fill="both", expand=True)

        self.body.grid_columnconfigure(0, weight=2, uniform="col")
        self.body.grid_columnconfigure(1, weight=1, uniform="col")
        self.body.grid_rowconfigure(0, weight=1)

        # Panel izquierdo (búsqueda + lista)
        left_panel = ctk.CTkFrame(self.body, fg_color="transparent")
        left_panel.grid(row=0, column=0, sticky="nsew")

        # Búsqueda
        search_container = ctk.CTkFrame(left_panel, fg_color="transparent")
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

        # Botón para ver inactivos - MEJORADO
        self.toggle_inactive_btn = ctk.CTkButton(
            self.search_frame, text="👁️ Ver Inactivos", height=40,
            fg_color="#6B7280", hover_color="#4B5563", command=self._toggle_inactive_view
        )
        self.toggle_inactive_btn.pack(side="right", padx=(5, 5))

        # Contador de productos - NUEVO
        self.count_label = ctk.CTkLabel(
            search_container, 
            text="", 
            text_color="gray60",
            font=ctk.CTkFont(size=12)
        )
        self.count_label.pack(anchor="w", padx=10, pady=(5, 0))

        # Lista
        self.list_frame = ctk.CTkScrollableFrame(left_panel, fg_color="transparent")
        self.list_frame.pack(fill="both", expand=True)

        # Panel derecho (formulario/placeholder)
        self.form_frame = ctk.CTkFrame(self.body, fg_color="transparent")
        self.form_frame.grid(row=0, column=1, sticky="nsew")

        self._show_placeholder()

    def _toggle_inactive_view(self):
        """Alterna entre ver solo activos y ver todos los productos"""
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
        
        self._load_products(self.q_var.get().strip())

    def _show_placeholder(self):
        self._clear_container(self.form_frame)
        ph = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        ph.pack(expand=True, fill="both")
        ctk.CTkLabel(
            ph,
            text="👈 Selecciona un producto o da clic en ➕ Nuevo",
            font=ctk.CTkFont(size=14),
            text_color="gray70"
        ).pack(expand=True)

    def _clear_container(self, container):
        for w in container.winfo_children():
            w.destroy()

    def _back_to_menu(self):
        for w in self.parent.winfo_children():
            w.destroy()
        main_app = self.parent.master if hasattr(self.parent, 'master') else self.parent
        if hasattr(main_app, "set_window_size"):
            main_app.set_window_size("menu")
        from ui.menu import MainMenu
        MainMenu(self.parent, self.parent.current_user).pack(fill="both", expand=True)

    # -------- LISTA --------
    def _load_products(self, query: str = ""):
        """Carga productos con opción de incluir inactivos"""
        for w in self.list_frame.winfo_children():
            w.destroy()
        
        # Usar active_only=False cuando show_inactive es True
        items = self.repo.search(query, active_only=not self.show_inactive) if query else self.repo.list_all(active_only=not self.show_inactive)

        # Actualizar contador - NUEVO
        active_count = len([p for p in items if p.active])
        inactive_count = len([p for p in items if not p.active])
        
        if self.show_inactive:
            self.count_label.configure(
                text=f"Mostrando {len(items)} productos ({active_count} activos, {inactive_count} inactivos)"
            )
        else:
            self.count_label.configure(
                text=f"Mostrando {len(items)} productos activos"
            )

        if not items:
            no_products_text = "Sin productos" if not self.show_inactive else "Sin productos (activos o inactivos)"
            ctk.CTkLabel(self.list_frame, text=no_products_text, text_color="gray60").pack(pady=40)
            return

        self.list_frame.grid_columnconfigure((0, 1), weight=1, uniform="col")

        for idx, p in enumerate(items):
            row = idx // 2
            col = idx % 2
            card = self._product_card(p)
            card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

    def _product_card(self, p: Product):
        """Crea una tarjeta de producto con indicador de estado"""
        card = ctk.CTkFrame(self.list_frame, corner_radius=10, border_width=1)
        
        # Cambiar color de borde para productos inactivos
        if not p.active:
            card.configure(border_color="#EF4444", fg_color="#4d4c4c")

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=12, pady=10)

        # Header de la tarjeta con indicador de estado
        header_frame = ctk.CTkFrame(inner, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 5))

        title = f"{p.sku} — {p.description}"
        
        # Indicadores visuales
        indicators = []
        if getattr(p, "is_pos_shortcut", False):
            indicators.append("📌 POS")
        if getattr(p, "print_logo", False):
            indicators.append("🖨️ Logo")
        if not p.active:
            indicators.append("❌ INACTIVO")

        if indicators:
            title += "   " + " • ".join(indicators)

        ctk.CTkLabel(header_frame, text=title, font=ctk.CTkFont(weight="bold")).pack(side="left")
        
        # Info del producto
        ctk.CTkLabel(
            inner,
            text=f"💲 {p.price:.2f}  •  IVA {int(p.tax_rate*100)}%  •  {p.unit}  •  {p.kind}",
            text_color="gray70"
        ).pack(anchor="w", pady=(2, 8))

        # Botones de acción
        actions = ctk.CTkFrame(inner, fg_color="transparent")
        actions.pack(fill="x")

        # Botón para fijar/desfijar en POS
        text_shortcut = "📌 Desfijar" if p.is_pos_shortcut else "📌 Fijar"
        ctk.CTkButton(
            actions, text=text_shortcut, height=28, width=90,
            fg_color="#F59E0B", command=lambda: self._toggle_shortcut(p)
        ).pack(side="right", padx=(5, 0))

        # Botón editar
        ctk.CTkButton(
            actions, text="✏️ Editar", height=28, width=90,
            fg_color="gray40", command=lambda sku=p.sku: self._show_form_edit(sku)
        ).pack(side="right", padx=(5, 0))

        # Botón activar/desactivar - MEJORADO
        if p.active:
            ctk.CTkButton(
                actions, text="🚫 Desactivar", height=28, width=110,
                fg_color="#EF4444", hover_color="#DC2626",
                command=lambda sku=p.sku: self._toggle_active(sku, True)
            ).pack(side="right", padx=(5, 0))
        else:
            ctk.CTkButton(
                actions, text="✅ Activar", height=28, width=110,
                fg_color="#10B981", hover_color="#059669",
                command=lambda sku=p.sku: self._toggle_active(sku, False)
            ).pack(side="right", padx=(5, 0))

        return card

    def _on_search(self, event=None):
        self._load_products(self.q_var.get().strip())

    def _show_all(self, event=None):
        self._show_all_products()

    def _toggle_shortcut(self, p: Product):
        try:
            self.repo.toggle_shortcut(p.sku, p.is_pos_shortcut)
            self._load_products()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo actualizar POS: {e}")

    def _toggle_print_logo(self, p: Product):
        try:
            self.repo.toggle_print_logo(p.sku, p.print_logo)
            self._load_products()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo actualizar POS: {e}")

    # -------- FORM --------
    def _show_form_new(self):
        self.current_sku = None
        self._show_form()

    def _show_form_edit(self, sku: str):
        self.current_sku = sku
        self._show_form(edit=True)

    def _show_form(self, edit: bool = False):
        self._clear_container(self.form_frame)

        form = ctk.CTkScrollableFrame(self.form_frame, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=10, pady=20)
        form.grid_columnconfigure(0, weight=1)

        title_text = "➕ Nuevo Producto" if not edit else "✏️ Editar Producto"
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

        self.sku = ctk.StringVar()
        self.desc = ctk.StringVar()
        self.price = ctk.StringVar()
        self.cost = ctk.StringVar(value="0")
        self.unit = ctk.StringVar(value="SERV")
        self.kind = ctk.StringVar(value="SERVICIO")
        self.tax = ctk.StringVar(value="0.0")
        self.is_pos_shortcut = ctk.BooleanVar(value=False)
        self.print_logo = ctk.BooleanVar(value=False)

        sku_e   = ctk.CTkEntry(form, textvariable=self.sku, height=40, placeholder_text="SKU (único)")
        desc_e  = ctk.CTkEntry(form, textvariable=self.desc, height=40, placeholder_text="Descripción")
        price_e = ctk.CTkEntry(form, textvariable=self.price, height=40, placeholder_text="Precio (ej. 150.00)")
        cost_e  = ctk.CTkEntry(form, textvariable=self.cost, height=40, placeholder_text="Costo (opcional)")
        unit_e  = ctk.CTkComboBox(form, values=["PZA","SERV","UNIDAD"], height=40, variable=self.unit)
        kind_e  = ctk.CTkComboBox(form, values=["SERVICIO","PRODUCTO"], height=40, variable=self.kind)
        tax_e   = ctk.CTkComboBox(form, values=["0.00","0.08","0.16"], height=40, variable=self.tax)
        is_pos_shortcut_e = ctk.CTkCheckBox(form, text="📌 Mostrar en POS", variable=self.is_pos_shortcut)
        print_logo_e = ctk.CTkCheckBox(form, text="🖨️ Imprimir Logo", variable=self.print_logo)

        add_field("SKU *", sku_e)
        add_field("Descripción *", desc_e)
        add_field("Precio *", price_e)
        add_field("Costo", cost_e)
        add_field("Unidad", unit_e)
        add_field("Tipo", kind_e)
        add_field("Impuesto", tax_e)
        add_field("Favorita", is_pos_shortcut_e)
        add_field("Logo", print_logo_e)

        btns = ctk.CTkFrame(form, fg_color="transparent")
        btns.grid(row=row, column=0, sticky="ew", pady=(15, 0))

        ctk.CTkButton(
            btns, text="↩️ Cancelar", fg_color="gray50", height=40,
            command=self._cancel_form
        ).pack(side="left")

        btn_text = "💾 Guardar" if not edit else "🔄 Actualizar"
        btn_color = "#2CC985" if not edit else "#3B82F6"
        ctk.CTkButton(
            btns, text=btn_text, fg_color=btn_color, height=40,
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
            self.unit.set(p.unit or "SERV")
            self.kind.set(p.kind or "SERVICIO")
            self.tax.set(f"{p.tax_rate:.2f}")
            self.is_pos_shortcut.set(bool(getattr(p, "is_pos_shortcut", False)))
            self.print_logo.set(bool(getattr(p, "print_logo", False)))
            sku_e.configure(state="disabled")

    def _cancel_form(self):
        self._show_placeholder()
        self._load_products(self.q_var.get().strip())

    def _save(self):
        try:
            sku = self.sku.get().strip()
            desc = self.desc.get().strip()
            price = float(self.price.get().strip() or "0")
            cost = float(self.cost.get().strip() or "0")
            unit = self.unit.get() or "SERV"
            kind = self.kind.get() or "SERVICIO"
            tax = float(self.tax.get().strip() or "0.0")
            is_shortcut = bool(self.is_pos_shortcut.get())
            is_print_logo = bool(self.print_logo.get())

            p = Product(
                sku=sku, description=desc, price=price, cost=cost,
                unit=unit, kind=kind, tax_rate=tax,
                is_pos_shortcut=is_shortcut,
                print_logo=is_print_logo,
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

    def _toggle_active(self, sku: str, currently_active: bool):
        """Activa o desactiva un producto con confirmación"""
        product = self.repo.get(sku)
        if not product:
            messagebox.showerror("Error", "Producto no encontrado")
            return

        if currently_active:
            # Desactivar producto
            if messagebox.askyesno(
                "Desactivar Producto", 
                f"¿Desactivar el producto '{product.description}'?\n\n"
                f"Este producto ya no estará disponible en el POS."
            ):
                try:
                    self.repo.deactivate(sku)
                    messagebox.showinfo("Éxito", "Producto desactivado correctamente")
                    self._load_products(self.q_var.get().strip())
                except Exception as e:
                    messagebox.showerror("Error", f"No se pudo desactivar: {e}")
        else:
            # Activar producto
            if messagebox.askyesno(
                "Activar Producto", 
                f"¿Activar el producto '{product.description}'?\n\n"
                f"Este producto estará disponible en el POS."
            ):
                try:
                    self.repo.activate(sku)  # Necesitarás implementar este método
                    messagebox.showinfo("Éxito", "Producto activado correctamente")
                    self._load_products(self.q_var.get().strip())
                except Exception as e:
                    messagebox.showerror("Error", f"No se pudo activar: {e}")

