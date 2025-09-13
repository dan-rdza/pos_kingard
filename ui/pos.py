import customtkinter as ctk
from tkinter import messagebox
from repositories.student_repo import StudentRepository
from repositories.product_repo import ProductRepository

# Simulamos productos frecuentes desde JSON
SHORTCUT_PRODUCTS = [
    {"sku": "SERV-01", "description": "Inscripción", "price": 500.0, "tax_rate": 0.16},
    {"sku": "SERV-02", "description": "Mensualidad", "price": 1200.0, "tax_rate": 0.16},
    {"sku": "SERV-03", "description": "Transporte", "price": 350.0, "tax_rate": 0.16},
    {"sku": "SERV-04", "description": "Comedor", "price": 350.0, "tax_rate": 0.16}
]

class POSFrame(ctk.CTkFrame):
    def __init__(self, parent, db_connection):
        super().__init__(parent, fg_color="transparent")
        self.parent = parent
        self.db = db_connection

        self.student_repo = StudentRepository(self.db)
        self.product_repo = ProductRepository(self.db)

        self.selected_student = None
        self.cart = []

        self._build_ui()

    def _build_ui(self):
        self.left_panel = ctk.CTkFrame(self, fg_color="gray15", corner_radius=10)
        self.left_panel.pack(side="left", fill="both", expand=True, padx=(20, 10), pady=20)

        self.right_panel = ctk.CTkFrame(self, fg_color="gray18", corner_radius=10)
        self.right_panel.pack(side="right", fill="both", expand=True, padx=(10, 20), pady=20)

        # Header
        header = ctk.CTkFrame(self.left_panel, fg_color="transparent")
        header.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(header, text="💰 Punto de Venta", font=ctk.CTkFont(size=22, weight="bold")).pack(side="left")
        ctk.CTkButton(header, text="⬅️ Menú", command=self.parent.show_main_menu, height=35, fg_color="gray50").pack(side="right")

        # Alumno
        self._student_search_box()

        # Tarjeta de alumno seleccionado
        self.student_card = ctk.CTkFrame(self.left_panel, fg_color="gray20", corner_radius=8)
        self.student_card.pack(fill="x", padx=10, pady=(0, 10))
        self.student_card_label = ctk.CTkLabel(self.student_card, text="Sin alumno seleccionado", text_color="gray70")
        self.student_card_label.pack(padx=10, pady=10)

        # Productos frecuentes
        self._load_quick_products()

        # Búsqueda de productos
        self._product_search_box()

        # Carrito
        ctk.CTkLabel(self.right_panel, text="🛒 Carrito", font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w", padx=10, pady=(10,0))
        self.cart_frame = ctk.CTkScrollableFrame(self.right_panel, fg_color="gray25", corner_radius=8)
        self.cart_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Totales
        self.label_totals = ctk.CTkLabel(self.right_panel, text="Subtotal: $0.00   IVA: $0.00   Total: $0.00", font=ctk.CTkFont(size=14, weight="bold"))
        self.label_totals.pack(anchor="e", padx=10, pady=(5, 0))

        self.label_total_final = ctk.CTkLabel(self.right_panel, text="Total: $0.00", font=ctk.CTkFont(size=20, weight="bold"), text_color="#2CC985")
        self.label_total_final.pack(anchor="e", padx=10, pady=(0, 10))

        ctk.CTkButton(self.right_panel, text="💳 Cobrar", height=45, fg_color="#2CC985", command=self._on_pay).pack(anchor="e", padx=10, pady=(0, 10))

    def _student_search_box(self):
        frame = ctk.CTkFrame(self.left_panel, fg_color="transparent")
        frame.pack(fill="x", padx=10, pady=(10, 5))

        entry_row = ctk.CTkFrame(frame, fg_color="transparent")
        entry_row.pack(fill="x")

        self.student_entry = ctk.CTkEntry(entry_row, placeholder_text="Nombre o matrícula...")
        self.student_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.student_entry.bind("<Return>", lambda e: self._search_students())

        ctk.CTkButton(entry_row, text="🔍", command=self._search_students, width=40).pack(side="right")

        self.student_results_frame = ctk.CTkFrame(frame, fg_color="transparent")
        self.student_results_frame.pack(fill="x")

    def _search_students(self):
        query = self.student_entry.get().strip()
        for w in self.student_results_frame.winfo_children(): w.destroy()
        if not query: return

        students = self.student_repo.search(query)
        if not students:
            ctk.CTkLabel(self.student_results_frame, text="Sin resultados", text_color="gray70").pack()
            return

        for s in students[:5]:
            text = f"{s.enrollment} - {s.first_name} {s.second_name or ''}"
            ctk.CTkButton(self.student_results_frame, text=text, command=lambda st=s: self._select_student(st), fg_color="gray30", hover_color="gray20", height=35).pack(fill="x", pady=2)

    def _select_student(self, student):
        self.selected_student = student
        self.student_card_label.configure(text=f"🎓 {student.first_name} {student.second_name or ''}\nMatrícula: {student.enrollment}", text_color="white")
        for w in self.student_results_frame.winfo_children(): w.destroy()

    def _load_quick_products(self):
        frame = ctk.CTkFrame(self.left_panel, fg_color="gray18", corner_radius=8)
        frame.pack(fill="x", padx=10, pady=(0, 10))
        ctk.CTkLabel(frame, text="⚡ Productos Frecuentes", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=10, pady=5)

        for p in SHORTCUT_PRODUCTS:
            ctk.CTkButton(frame, text=f"{p['description']} (${p['price']})", command=lambda prod=p: self._add_to_cart(prod), height=40).pack(fill="x", padx=10, pady=2)

    def _product_search_box(self):
        frame = ctk.CTkFrame(self.left_panel, fg_color="transparent")
        frame.pack(fill="x", padx=10, pady=5)

        entry_row = ctk.CTkFrame(frame, fg_color="transparent")
        entry_row.pack(fill="x")

        self.product_entry = ctk.CTkEntry(entry_row, placeholder_text="SKU o descripción...")
        self.product_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.product_entry.bind("<Return>", lambda e: self._search_products())

        ctk.CTkButton(entry_row, text="➕", command=self._search_products, width=40).pack(side="right")
        self.product_results_frame = ctk.CTkFrame(frame, fg_color="transparent")
        self.product_results_frame.pack(fill="x")

    def _search_products(self):
        query = self.product_entry.get().strip()
        for w in self.product_results_frame.winfo_children(): w.destroy()
        if not query: return

        products = self.product_repo.search(query)
        if not products:
            ctk.CTkLabel(self.product_results_frame, text="No se encontraron productos", text_color="gray70").pack()
            return

        for p in products[:5]:
            text = f"{p.sku} - {p.description} (${p.price:.2f})"
            ctk.CTkButton(self.product_results_frame, text=text, command=lambda prod=p: self._add_to_cart(prod), fg_color="gray30", hover_color="gray20", height=35).pack(fill="x", pady=2)

    def _add_to_cart(self, product):
        # Si es un producto shortcut (dict), lo convertimos
        sku = product['sku'] if isinstance(product, dict) else product.sku
        found = False
        for item in self.cart:
            if item['sku'] == sku:
                item['qty'] += 1
                found = True
                break

        if not found:
            self.cart.append({
                'sku': sku,
                'description': product['description'] if isinstance(product, dict) else product.description,
                'price': product['price'] if isinstance(product, dict) else product.price,
                'tax_rate': product['tax_rate'] if isinstance(product, dict) else product.tax_rate,
                'qty': 1
            })

        self.product_entry.delete(0, ctk.END)
        for w in self.product_results_frame.winfo_children(): w.destroy()
        self._refresh_cart()

    def _refresh_cart(self):
        for w in self.cart_frame.winfo_children(): w.destroy()

        subtotal = 0
        tax_total = 0
        total = 0

        for item in self.cart:
            line_total = item['price'] * item['qty']
            tax = line_total * item['tax_rate']
            total_line = line_total + tax

            subtotal += line_total
            tax_total += tax
            total += total_line

            row = ctk.CTkFrame(self.cart_frame, fg_color="gray30", corner_radius=6)
            row.pack(fill="x", pady=5, padx=5)

            ctk.CTkLabel(row, text=item['description'], font=ctk.CTkFont(size=12)).pack(side="left", padx=(5, 0))

            qty_var = ctk.IntVar(value=item['qty'])
            qty_entry = ctk.CTkEntry(row, width=40, textvariable=qty_var)
            qty_entry.pack(side="left", padx=5)

            price_var = ctk.DoubleVar(value=item['price'])
            price_entry = ctk.CTkEntry(row, width=70, textvariable=price_var)
            price_entry.pack(side="left", padx=5)

            ctk.CTkButton(row, text="💾", width=30, command=lambda i=item, q=qty_var, p=price_var: self._update_item(i, q.get(), p.get())).pack(side="right", padx=5)

        self.label_totals.configure(text=f"Subtotal: ${subtotal:.2f}   IVA: ${tax_total:.2f}   Total: ${total:.2f}")
        self.label_total_final.configure(text=f"Total: ${total:.2f}")

    def _update_item(self, item, new_qty, new_price):
        item['qty'] = max(1, new_qty)
        item['price'] = max(0.01, new_price)
        self._refresh_cart()

    def _on_pay(self):
        messagebox.showinfo("POS", "Funcionalidad de cobro en desarrollo")
