# ui/pos.py
import customtkinter as ctk
from tkinter import messagebox
from repositories.student_repo import StudentRepository
from repositories.product_repo import ProductRepository
from repositories.sale_repo import SaleRepository
from repositories.payment_method_repo import PaymentMethodRepository
from printer.printer import TicketPrinter


class POSFrame(ctk.CTkFrame):
    def __init__(self, parent, db_connection):
        super().__init__(parent, fg_color="transparent")
        self.parent = parent
        self.db = db_connection

        self.student_repo = StudentRepository(self.db)
        self.product_repo = ProductRepository(self.db)
        self.sale_repo = SaleRepository(self.db)
        self.pm_repo = PaymentMethodRepository(self.db)

        self.selected_student = None
        self.cart = []
        self.payment_method = ctk.StringVar(value="")  # se cargará dinámicamente

        self._build_ui()

    def _build_ui(self):
        # Layout principal con header + 3 columnas de contenido
        self.grid_columnconfigure(0, weight=1, uniform="col")
        self.grid_columnconfigure(1, weight=2, uniform="col")
        self.grid_columnconfigure(2, weight=2, uniform="col")
        self.grid_rowconfigure(0, weight=0)  # header
        self.grid_rowconfigure(1, weight=1)  # contenido

        # Header superior
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, columnspan=3, sticky="ew", padx=15, pady=(10, 0))

        ctk.CTkLabel(
            header, text="💰 Punto de Venta",
            font=ctk.CTkFont(size=22, weight="bold")
        ).pack(side="left")

        ctk.CTkButton(
            header, text="⬅️ Menú", height=35, fg_color="gray50",
            command=self._back_to_menu
        ).pack(side="right")

        # Panel alumno
        self._build_student_panel()

        # Panel productos
        self._build_products_panel()

        # Panel carrito
        self._build_cart_panel()

    # ---------- Panel alumno ----------
    def _build_student_panel(self):
        frame = ctk.CTkFrame(self, fg_color="gray15", corner_radius=10)
        frame.grid(row=1, column=0, sticky="nsew", padx=(15, 5), pady=15)

        ctk.CTkLabel(frame, text="🎓 Alumno", font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w", padx=10, pady=(10, 5))

        self.student_entry = ctk.CTkEntry(frame, placeholder_text="Nombre o matrícula...")
        self.student_entry.pack(fill="x", padx=10, pady=(0, 5))
        self.student_entry.bind("<Return>", lambda e: self._search_students())

        ctk.CTkButton(frame, text="🔍 Buscar", command=self._search_students).pack(padx=10, pady=(0, 10))

        self.student_results_frame = ctk.CTkFrame(frame, fg_color="transparent")
        self.student_results_frame.pack(fill="x", padx=10)

        # Tarjeta seleccionada
        self.student_card = ctk.CTkFrame(frame, fg_color="gray20", corner_radius=8)
        self.student_card.pack(fill="x", padx=10, pady=10)
        self.student_card_label = ctk.CTkLabel(self.student_card, text="Sin alumno seleccionado", text_color="gray70")
        self.student_card_label.pack(padx=10, pady=10)

    def _search_students(self):
        query = self.student_entry.get().strip()
        for w in self.student_results_frame.winfo_children():
            w.destroy()
        if not query:
            return

        students = self.student_repo.search(query)
        if not students:
            ctk.CTkLabel(self.student_results_frame, text="Sin resultados", text_color="gray70").pack()
            return

        for s in students[:5]:
            text = f"{s.enrollment} - {s.first_name} {s.second_name or ''}"
            ctk.CTkButton(
                self.student_results_frame, text=text,
                command=lambda st=s: self._select_student(st),
                fg_color="gray30", hover_color="gray20", height=35
            ).pack(fill="x", pady=2)

    def _select_student(self, student):
        self.selected_student = student
        self.student_card_label.configure(
            text=f"{student.first_name} {student.second_name or ''}\nMatrícula: {student.enrollment}",
            text_color="white"
        )
        for w in self.student_results_frame.winfo_children():
            w.destroy()

    # ---------- Panel productos ----------
    def _build_products_panel(self):
        frame = ctk.CTkFrame(self, fg_color="gray15", corner_radius=10)
        frame.grid(row=1, column=1, sticky="nsew", padx=5, pady=15)

        ctk.CTkLabel(frame, text="📦 Productos", font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w", padx=10, pady=(10, 5))

        # Productos frecuentes
        self.quick_frame = ctk.CTkFrame(frame, fg_color="gray18", corner_radius=8)
        self.quick_frame.pack(fill="x", padx=10, pady=(0, 10))
        ctk.CTkLabel(self.quick_frame, text="⚡ Frecuentes", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=10, pady=5)

        self._load_quick_products()

        # Búsqueda
        search_box = ctk.CTkFrame(frame, fg_color="transparent")
        search_box.pack(fill="x", padx=10, pady=(0, 5))

        self.product_entry = ctk.CTkEntry(search_box, placeholder_text="SKU o descripción...")
        self.product_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.product_entry.bind("<Return>", lambda e: self._search_products())

        ctk.CTkButton(search_box, text="➕", command=self._search_products, width=40).pack(side="right")
        self.product_results_frame = ctk.CTkFrame(frame, fg_color="transparent")
        self.product_results_frame.pack(fill="x", padx=10, pady=(0, 10))

    def _load_quick_products(self):
        # limpiar y reconstruir (para evitar duplicados de grids)
        for w in self.quick_frame.winfo_children():
            w.destroy()
        ctk.CTkLabel(self.quick_frame, text="⚡ Frecuentes", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=10, pady=5)

        products = self.product_repo.get_top_sold(limit=8) or self.product_repo.get_pos_shortcuts(limit=8)
        if not products:
            ctk.CTkLabel(self.quick_frame, text="No configurados", text_color="gray70").pack(pady=5)
            return

        grid = ctk.CTkFrame(self.quick_frame, fg_color="transparent")
        grid.pack(fill="x", padx=10, pady=(0, 10))
        grid.grid_columnconfigure((0, 1), weight=1, uniform="col")

        for idx, p in enumerate(products):
            row, col = divmod(idx, 2)
            desc = p["description"] if isinstance(p, dict) else p.description
            price = p["price"] if isinstance(p, dict) else p.price
            ctk.CTkButton(
                grid,
                text=f"{desc}\n💲{price:.2f}",
                command=lambda prod=p: self._add_to_cart(prod),
                height=60, fg_color="#374151", hover_color="#2563EB"
            ).grid(row=row, column=col, padx=5, pady=5, sticky="nsew")

    def _search_products(self):
        query = self.product_entry.get().strip()
        for w in self.product_results_frame.winfo_children():
            w.destroy()
        if not query:
            return

        products = self.product_repo.search(query)
        if not products:
            ctk.CTkLabel(self.product_results_frame, text="No se encontraron productos", text_color="gray70").pack()
            return

        for p in products[:5]:
            text = f"{p.sku} - {p.description} (${p.price:.2f})"
            ctk.CTkButton(
                self.product_results_frame, text=text,
                command=lambda prod=p: self._add_to_cart(prod),
                fg_color="gray30", hover_color="gray20", height=35
            ).pack(fill="x", pady=2)

    # ---------- Panel carrito ----------
    def _build_cart_panel(self):
        frame = ctk.CTkFrame(self, fg_color="gray15", corner_radius=10)
        frame.grid(row=1, column=2, sticky="nsew", padx=(5, 15), pady=15)

        ctk.CTkLabel(frame, text="🛒 Carrito", font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w", padx=10, pady=(10, 5))
        self.cart_frame = ctk.CTkScrollableFrame(frame, fg_color="gray20", corner_radius=8)
        self.cart_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Totales
        self.label_totals = ctk.CTkLabel(frame, text="Subtotal: $0.00   IVA: $0.00", font=ctk.CTkFont(size=14))
        self.label_totals.pack(anchor="e", padx=10, pady=(5, 0))

        self.label_total_final = ctk.CTkLabel(frame, text="Total: $0.00", font=ctk.CTkFont(size=20, weight="bold"), text_color="#2CC985")
        self.label_total_final.pack(anchor="e", padx=10, pady=(0, 10))

        # Selector dinámico de método de pago
        payment_frame = ctk.CTkFrame(frame, fg_color="transparent")
        payment_frame.pack(fill="x", padx=10, pady=(0, 10))
        ctk.CTkLabel(payment_frame, text="Método de pago:", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", pady=(0, 5))

        methods = self.pm_repo.list_all(active_only=True)
        if not methods:
            ctk.CTkLabel(payment_frame, text="⚠️ No hay métodos configurados", text_color="red").pack(anchor="w")
        else:
            self.payment_method.set(str(methods[0]["id"]))  # Guardar ID
            for pm in methods:
                ctk.CTkRadioButton(
                    payment_frame,
                    text=f"{pm['name']} ({pm['code']})",
                    variable=self.payment_method,
                    value=str(pm["id"])   # Guardar ID como string
                ).pack(anchor="w", pady=2)

        # Botón cobrar
        ctk.CTkButton(frame, text="💳 Cobrar", height=50, fg_color="#2CC985", command=self._on_pay).pack(anchor="e", padx=10, pady=(0, 10))


    # ---------- Carrito ----------
    def _add_to_cart(self, product):
        sku = product["sku"] if isinstance(product, dict) else product.sku
        found = False
        for item in self.cart:
            if item["sku"] == sku:
                item["qty"] += 1
                found = True
                break
        if not found:
            self.cart.append({
                "sku": sku,
                "description": product["description"] if isinstance(product, dict) else product.description,
                "price": product["price"] if isinstance(product, dict) else product.price,
                "tax_rate": product["tax_rate"] if isinstance(product, dict) else product.tax_rate,
                "qty": 1
            })
        self._refresh_cart()

    def _refresh_cart(self):
        for w in self.cart_frame.winfo_children():
            w.destroy()

        subtotal = 0
        tax_total = 0
        total = 0

        # Encabezados
        header = ctk.CTkFrame(self.cart_frame, fg_color="transparent")
        header.pack(fill="x", padx=5)
        ctk.CTkLabel(header, text="Producto", width=120).pack(side="left", padx=5)
        ctk.CTkLabel(header, text="Cant", width=40).pack(side="left")
        ctk.CTkLabel(header, text="Precio", width=60).pack(side="left")
        ctk.CTkLabel(header, text="Total", width=60).pack(side="left")

        for item in self.cart:
            line_total = item["price"] * item["qty"]
            tax = line_total * item["tax_rate"]
            total_line = line_total + tax

            subtotal += line_total
            tax_total += tax
            total += total_line

            row = ctk.CTkFrame(self.cart_frame, fg_color="gray30", corner_radius=6)
            row.pack(fill="x", pady=3, padx=5)

            ctk.CTkLabel(row, text=item["description"], width=120).pack(side="left", padx=5)

            ctk.CTkButton(row, text="➖", width=25,
                          command=lambda i=item: self._update_item(i, qty=i["qty"]-1)).pack(side="left", padx=(5, 0))
            ctk.CTkLabel(row, text=str(item["qty"]), width=30).pack(side="left")
            ctk.CTkButton(row, text="➕", width=25,
                          command=lambda i=item: self._update_item(i, qty=i["qty"]+1)).pack(side="left", padx=(0, 5))

            ctk.CTkLabel(row, text=f"${item['price']:.2f}", width=60).pack(side="left")
            ctk.CTkLabel(row, text=f"${total_line:.2f}", width=60).pack(side="left")

            ctk.CTkButton(row, text="❌", width=30,
                          fg_color="#EF4444", hover_color="#B91C1C",
                          command=lambda i=item: self._remove_item(i)).pack(side="right", padx=5)

        self.label_totals.configure(text=f"Subtotal: ${subtotal:.2f}   IVA: ${tax_total:.2f}")
        self.label_total_final.configure(text=f"Total: ${total:.2f}")

    def _update_item(self, item, qty):
        if qty <= 0:
            self._remove_item(item)
        else:
            item["qty"] = qty
        self._refresh_cart()

    def _remove_item(self, item):
        self.cart = [i for i in self.cart if i["sku"] != item["sku"]]
        self._refresh_cart()

    # ---------- Pago ----------
    def _on_pay(self):
        printer = TicketPrinter()
        if not self.cart:
            messagebox.showwarning("POS", "No hay productos en el carrito")
            return
        if not self.selected_student:
            messagebox.showwarning("POS", "Debe seleccionar un alumno")
            return

        subtotal = sum(i["price"] * i["qty"] for i in self.cart)
        tax = sum(i["price"] * i["qty"] * i["tax_rate"] for i in self.cart)
        total = subtotal + tax

        payment_method_id = int(self.payment_method.get())
        sale_id = self.sale_repo.create_sale(
            student=self.selected_student,
            cart=self.cart,
            seller=self.parent.current_user,
            payment_method_id=payment_method_id,
            amount=total
        )

        pm = self.pm_repo.get(payment_method_id)
        payment_method_name = pm["name"] if pm else f"ID {payment_method_id}"

        folio = f"F{sale_id:04d}"  # ejemplo: F004


        items = [
            {
                "description": i["description"],
                "qty": i["qty"],
                "unit_price": i["price"],
                "tax_rate": i["tax_rate"]
            }
            for i in self.cart
        ]

        business = {
            "name": "KINDERGARTEN REYES",
            "rfc": "XAXX010101000",
            "address": "Av. Siempre Viva 123, CDMX",
            "phone": "(55) 1234-5678",
            "footer": "Este ticket no es comprobante fiscal"
        }        

        totals = {"subtotal": subtotal, "tax": tax, "total": total}
        # ✅ Confirmación al usuario
        if messagebox.askyesno("Venta procesada",
            f"Venta procesada con el folio {folio} en {payment_method_name}.\n\n¿Imprimir ticket?"):
            
               
            printer.print_ticket(
                header={"folio": folio, "student": f"{self.selected_student.first_name} {self.selected_student.second_name or ''}", "enrollment": self.selected_student.enrollment},
                items=items,
                totals=totals,
                payment_method=payment_method_name,
                business=business
            )




    # ---------- Imprimir Ticket ---------- 
    def _print_ticket(self, items=dict, totals=float, payment_method_name=str, print_logo=False):
        """
        Imprime ticket en impresora ESC/POS.
        """      



    # ---------- Volver al menú ----------
    def _back_to_menu(self):
        for w in self.parent.winfo_children():
            w.destroy()
        main_app = self.parent.master if hasattr(self.parent, "master") else self.parent
        if hasattr(main_app, "set_window_size"):
            main_app.set_window_size("menu")
        from ui.menu import MainMenu
        MainMenu(self.parent, self.parent.current_user).pack(fill="both", expand=True)
