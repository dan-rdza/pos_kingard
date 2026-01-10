# ui/pos.py

import customtkinter as ctk
from datetime import datetime
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
        self.payment_method = ctk.StringVar(value="")

        self._build_ui()

    # ---------- Layout principal ----------
    def _build_ui(self):
        self.grid_columnconfigure(0, weight=2, uniform="col")   # Alumno
        self.grid_columnconfigure(1, weight=2, uniform="col")   # Productos
        self.grid_columnconfigure(2, weight=4, uniform="col")   # Carrito
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)

        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, columnspan=3, sticky="ew", padx=15, pady=(10, 0))
        
        ctk.CTkLabel(header, text="💰 Punto de Venta", font=ctk.CTkFont(size=22, weight="bold")).pack(side="left")      

                # Frame para elementos derechos
        right_frame = ctk.CTkFrame(header, fg_color="transparent")
        right_frame.pack(side="right")

        # Reloj (actualizable)
        self.clock_label = ctk.CTkLabel(right_frame, text="", 
                                       font=ctk.CTkFont(size=13, weight="bold"))
        self.clock_label.pack(side="left", padx=(0, 10))
        
        # Botón menú
        ctk.CTkButton(right_frame, text="⬅️ Menú", height=35, fg_color="gray50", 
                     command=self._back_to_menu).pack(side="right")
        
        # Iniciar reloj
        self._update_clock()
        

        # Paneles
        self._build_student_panel()
        self._build_products_panel()
        self._build_cart_panel()

    # ---------- Panel alumno ----------
    def _build_student_panel(self):
        frame = ctk.CTkFrame(self, fg_color="gray15", corner_radius=10)
        frame.grid(row=1, column=0, sticky="nsew", padx=(15, 5), pady=15)

        ctk.CTkLabel(frame, text="🎓 Alumno", font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w", padx=10, pady=(10, 5))

        # Label fijo arriba
        self.student_card_label = ctk.CTkLabel(frame, text="Nombre del alumno o matrícula", font=ctk.CTkFont(size=13, weight="bold"), justify='left')
        self.student_card_label.pack(anchor="w", padx=10, pady=(10, 5))

        # Buscador
        self.search_var = ctk.StringVar()
        search_entry = ctk.CTkEntry(frame, placeholder_text="Buscar alumno...", textvariable=self.search_var)
        search_entry.pack(fill="x", padx=(10, 25), pady=(5, 10))
        search_entry.bind("<KeyRelease>", self._on_search_student)

        # Resultados
        self.students_frame = ctk.CTkScrollableFrame(frame, fg_color="transparent")
        self.students_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def _on_search_student(self, event=None):
        for w in self.students_frame.winfo_children():
            w.destroy()

        query = self.search_var.get().strip()
        results = self.student_repo.search(query) if query else self.student_repo.get_all()

        for student in results:
            btn = ctk.CTkButton(
                self.students_frame,
                text=f"{student.enrollment} - {student.first_name} {student.second_name or ''}",
                command=lambda s=student: self._select_student(s),
                height=35, fg_color="gray30"
            )
            btn.pack(fill="x", padx=(0,15), pady=2)

    def _select_student(self, student):
        self.selected_student = student
        self.student_card_label.configure(text=f"Matrícula: {student.enrollment}\n{student.first_name} {student.second_name or ''}")

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
        ctk.CTkLabel(
            frame, 
            text="SKU o Descripción del producto",
            font=ctk.CTkFont(weight="bold")
        ).pack(anchor="w", padx=(10, 10), pady=(10, 5))  # pady: 10 arriba, 5 abajo

        search_box = ctk.CTkFrame(frame, fg_color="transparent")
        search_box.pack(fill="x", pady=(0, 5))

        # Buscador        
        self.search_product_var = ctk.StringVar()        
        self.product_entry = ctk.CTkEntry(search_box, placeholder_text="SKU o descripción...", textvariable=self.search_product_var)
        self.product_entry.pack(side="left", fill="x", expand=True, padx=(10, 10))
        self.product_entry.bind("<KeyRelease>", self._on_search_products)

        # Resultados
        self.product_results_frame = ctk.CTkScrollableFrame(frame, fg_color="transparent")
        self.product_results_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

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
                text=f"{desc}\n💲{price:,.2f}",
                command=lambda prod=p: self._add_to_cart(prod),
                height=60, fg_color="#374151", hover_color="#2563EB"
            ).grid(row=row, column=col, padx=5, pady=5, sticky="nsew")

    def _on_search_products(self, event:None):
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
            text = f"{p.sku} - {p.description} (${p.price:,.2f})"
            ctk.CTkButton(
                self.product_results_frame, text=text,
                command=lambda prod=p: self._add_to_cart(prod),
                fg_color="gray30", height=35
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

        # Métodos de pago dinámicos
        payment_frame = ctk.CTkFrame(frame, fg_color="transparent")
        payment_frame.pack(fill="x", padx=10, pady=(0, 10))
        ctk.CTkLabel(payment_frame, text="Método de pago:", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", pady=(0, 5))
        methods = self.pm_repo.list_all(active_only=True)
        if not methods:
            ctk.CTkLabel(payment_frame, text="⚠️ No hay métodos configurados", text_color="red").pack(anchor="w")
        else:
            self.payment_method.set(str(methods[0]["id"]))
            for pm in methods:
                ctk.CTkRadioButton(
                    payment_frame,
                    text=f"{pm['name']} ({pm['code']})",
                    variable=self.payment_method,
                    value=str(pm["id"])
                ).pack(anchor="w", pady=2)

        ctk.CTkButton(frame, text="💳 Cobrar", height=50, fg_color="#2CC985", command=self._on_pay).pack(anchor="e", padx=10, pady=(0, 10))

    # ---------- Carrito ----------    
    def _add_to_cart(self, product):
        sku = product["sku"] if isinstance(product, dict) else product.sku
        price = product["price"] if isinstance(product, dict) else product.price        
        found = False
        print(f"Product: {product}")
        for item in self.cart:
            if item["sku"] == sku and item["price"] == price:
                item["qty"] += 1
                found = True
                break
        if not found:
            self.cart.append({
                "sku": sku,
                "description": product["description"] if isinstance(product, dict) else product.description,
                "price": product["price"] if isinstance(product, dict) else product.price,
                "tax_rate": product["tax_rate"] if isinstance(product, dict) else product.tax_rate,
                "qty": 1,
                "print_logo": product["print_logo"] if isinstance(product, dict) else product.print_logo,
            })

            print(f"Cart: {self.cart}")
        self._refresh_cart()

    def _refresh_cart(self):
        for w in self.cart_frame.winfo_children():
            w.destroy()

        if not self.cart:
            ctk.CTkLabel(self.cart_frame, text="Carrito vacío", text_color="gray70").pack(pady=20)
            self.label_totals.configure(text="Subtotal: $0.00   IVA: $0.00")
            self.label_total_final.configure(text="Total: $0.00")
            return

        subtotal = 0
        tax = 0

        # Crear contenedor principal con grid
        table_container = ctk.CTkFrame(self.cart_frame, fg_color="transparent")
        table_container.pack(fill="both", expand=True)
        
        # Configurar columnas con anchos fijos/proporcionales
        table_container.grid_columnconfigure(0, weight=4, minsize=200)  # Descripción
        table_container.grid_columnconfigure(1, weight=1, minsize=60)   # Cantidad
        table_container.grid_columnconfigure(2, weight=1, minsize=80)   # Precio Unitario
        table_container.grid_columnconfigure(3, weight=1, minsize=80)   # Importe
        table_container.grid_columnconfigure(4, weight=1, minsize=60)   # Editar
        table_container.grid_columnconfigure(5, weight=1, minsize=60)   # Eliminar

        # Encabezados - Fila 0
        row = 0
        ctk.CTkLabel(table_container, text="Descripción", font=ctk.CTkFont(size=13, weight="bold"), 
                    anchor="w").grid(row=row, column=0, sticky="ew", padx=5, pady=(0, 10))
        ctk.CTkLabel(table_container, text="Cant", font=ctk.CTkFont(size=13, weight="bold"), 
                    anchor="center").grid(row=row, column=1, sticky="ew", padx=5, pady=(0, 10))
        ctk.CTkLabel(table_container, text="P.U.", font=ctk.CTkFont(size=13, weight="bold"), 
                    anchor="center").grid(row=row, column=2, sticky="ew", padx=5, pady=(0, 10))
        ctk.CTkLabel(table_container, text="Importe", font=ctk.CTkFont(size=13, weight="bold"), 
                    anchor="center").grid(row=row, column=3, sticky="ew", padx=5, pady=(0, 10))
        ctk.CTkLabel(table_container, text="Acciones", font=ctk.CTkFont(size=13, weight="bold"), 
                    anchor="center").grid(row=row, column=4, columnspan=2, sticky="ew", padx=5, pady=(0, 10))

        
        row += 1

        for idx, item in enumerate(self.cart):
            # Acortar descripción si es muy larga
            description = item["description"]
            if len(description) > 35:
                description = description[:32] + "..."

            # Fila de producto
            ctk.CTkLabel(table_container, text=description, font=ctk.CTkFont(size=13), 
                        anchor="w").grid(row=row, column=0, sticky="ew", padx=5, pady=8)
            ctk.CTkLabel(table_container, text=f"{item['qty']}", font=ctk.CTkFont(size=13), 
                        anchor="center").grid(row=row, column=1, sticky="ew", padx=5, pady=8)
            ctk.CTkLabel(table_container, text=f"${item['price']:,.2f}", font=ctk.CTkFont(size=13), 
                        anchor="center").grid(row=row, column=2, sticky="ew", padx=5, pady=8)
            ctk.CTkLabel(table_container, text=f"${item['qty'] * item['price']:,.2f}", 
                        font=ctk.CTkFont(size=13, weight="bold"), anchor="center").grid(row=row, column=3, sticky="ew", padx=5, pady=8)

            # Frame para botones (para mejor alineación)
            btn_frame = ctk.CTkFrame(table_container, fg_color="transparent", width=120)
            btn_frame.grid(row=row, column=4, columnspan=2, sticky="ew", padx=5)
            btn_frame.grid_columnconfigure((0, 1), weight=1)
            
            ctk.CTkButton(btn_frame, text="✏️", width=35, height=30, fg_color="gray40",
                        command=lambda i=idx: self._edit_price(i)).grid(row=0, column=0, padx=2)
            ctk.CTkButton(btn_frame, text="❌", width=35, height=30, fg_color="#EF4444",
                        command=lambda i=idx: self._remove_item(i)).grid(row=0, column=1, padx=2)
            
            row += 1

            subtotal += item["price"] * item["qty"]
            tax += item["price"] * item["qty"] * item["tax_rate"]

        total = subtotal + tax
        self.label_totals.configure(text=f"Subtotal: ${subtotal:,.2f}   IVA: ${tax:,.2f}")
        self.label_total_final.configure(text=f"Total: ${total:,.2f}")

    def _edit_price(self, index):
        item = self.cart[index]

        popup = ctk.CTkToplevel(self)
        popup.title("Editar precio")
        popup.geometry("300x150")
        popup.transient(self)
        popup.grab_set()
        popup.focus()

        ctk.CTkLabel(popup, text=f"{item['description']}", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=10)
        new_price_var = ctk.StringVar(value=f"{item['price']:,.2f}")
        entry = ctk.CTkEntry(popup, textvariable=new_price_var, justify="center")
        entry.pack(pady=5)
        entry.focus()

        def save_price():
            try:
                new_price = float(new_price_var.get())
                if new_price <= 0:
                    raise ValueError
                self.cart[index]["price"] = new_price
                self._refresh_cart()
                popup.destroy()
            except ValueError:
                messagebox.showerror("Error", "Ingrese un precio válido")

        ctk.CTkButton(popup, text="Guardar", fg_color="#2CC985", command=save_price).pack(pady=10)

    def _remove_item(self, index):
        if 0 <= index < len(self.cart):
            del self.cart[index]
        self._refresh_cart()

    # ---------- Pago ----------
    def _on_pay(self):
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
        folio = f"F{sale_id:04d}"

        if messagebox.askyesno("Venta procesada", f"Venta procesada con el folio {folio} en {payment_method_name}.\n\n¿Imprimir ticket?"):
            printer = TicketPrinter()
            items = [
                {"description": i["description"], "qty": i["qty"], "unit_price": i["price"], "tax_rate": i["tax_rate"], "print_logo": i["print_logo"]}
                for i in self.cart
            ]
            totals = {"subtotal": subtotal, "tax": tax, "total": total}

            # Business config debería venir de repositorio
            business = {
                "nombre": "LIBERTAD Y CREATIVIDAD",
                "title": "PREESCOLAR LIBERTAD Y CREATIVIDAD A.C",
                "clave": "CCT 11PJN08 39V",
                "eslogan": "Educar con el corazón para llegar a la razón",
                "rfc": "LCR030414IB8",
                "direccion": "EL TUNEL 103-B, LA JOYA EJIDO, LEON, GTO. MX.",
                "contacto": "TEL(S). 477-449-7752 / 477-290-8432",
                "notas01": "Conserve su ticket para cualquier aclaración.",
                "notas02": "Este ticket no es comprobante fiscal."
            }

            printer.print_ticket(
                header={"folio": folio, "student": f"{self.selected_student.first_name} {self.selected_student.second_name or ''}", "enrollment": self.selected_student.enrollment},
                items=items,
                totals=totals,
                payment_method=payment_method_name,
                business=business
            )

        self.cart = []
        self._refresh_cart()

    # ---------- Back ----------
    def _back_to_menu(self):
        for w in self.parent.winfo_children():
            w.destroy()
        main_app = self.parent.master if hasattr(self.parent, "master") else self.parent
        if hasattr(main_app, "set_window_size"):
            main_app.set_window_size("menu")
        from ui.menu import MainMenu
        MainMenu(self.parent, self.parent.current_user).pack(fill="both", expand=True)


    # ---------- Clock ----------
    def _format_datetime(self):
        """Formatea la fecha y hora al formato deseado"""
        now = datetime.now()
        
        # Diccionarios para traducción
        days = {
            'Monday': 'Lunes', 'Tuesday': 'Martes', 'Wednesday': 'Miércoles',
            'Thursday': 'Jueves', 'Friday': 'Viernes', 'Saturday': 'Sábado',
            'Sunday': 'Domingo'
        }
        
        months = {
            'January': 'Enero', 'February': 'Febrero', 'March': 'Marzo',
            'April': 'Abril', 'May': 'Mayo', 'June': 'Junio',
            'July': 'Julio', 'August': 'Agosto', 'September': 'Septiembre',
            'October': 'Octubre', 'November': 'Noviembre', 'December': 'Diciembre'
        }
        
        # Obtener nombre del día y mes en español
        day_name_en = now.strftime("%A")
        month_name_en = now.strftime("%B")
        
        day_name_es = days.get(day_name_en, day_name_en)
        month_name_es = months.get(month_name_en, month_name_en)
        
        # Formatear hora en formato 12 horas con a.m./p.m.
        hour_12 = now.strftime("%I").lstrip('0')  # Hora en 12h sin cero inicial
        minute = now.strftime("%M")
        second = now.strftime("%S")
        am_pm = now.strftime("%p").lower()  # "AM" o "PM" en minúsculas
        
        # Convertir a español
        am_pm_es = "a.m." if am_pm == "am" else "p.m."
        
        # Construir el string final
        formatted = f"{day_name_es}, {now.day} de {month_name_es} del {now.year} {hour_12}:{minute}:{second} {am_pm_es}"
        
        return formatted
    
    def _update_clock(self):
        """Actualiza el reloj cada segundo"""
        current_time = self._format_datetime()
        self.clock_label.configure(text=current_time)
        # Programar próxima actualización en 1 segundo
        self.clock_label.after(1000, self._update_clock) 