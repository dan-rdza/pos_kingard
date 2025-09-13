# ui/pos.py
import customtkinter as ctk
from tkinter import messagebox
from repositories.student_repo import StudentRepository
from repositories.product_repo import ProductRepository



class POSFrame(ctk.CTkFrame):
    def __init__(self, parent, db_connection):
        super().__init__(parent, fg_color="transparent")
        self.parent = parent
        self.db = db_connection

        # Inicializar datos de venta
        from repositories.student_repo import StudentRepository
        self.student_repo = StudentRepository(self.db)
        
        # Inicializamos datos de productos
        from repositories.product_repo import ProductRepository
        self.product_repo = ProductRepository(self.db)


        self.selected_student = None
        self.cart = []

        self.create_widgets()

    def create_widgets(self):
        # === CABECERA ===
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=10, padx=20)

        ctk.CTkLabel(
            header, text="💰 Punto de Venta",
            font=ctk.CTkFont(size=22, weight="bold")
        ).pack(side="left")

        ctk.CTkButton(
            header, text="⬅️ Volver al Menú",
            command=self.parent.show_main_menu,
            height=35, fg_color="gray50"
        ).pack(side="right")

        # === BUSCAR ALUMNO ===        
        student_frame = ctk.CTkFrame(self)
        student_frame.pack(fill="x", padx=20, pady=(10, 0))

        ctk.CTkLabel(student_frame, text="Alumno:", font=ctk.CTkFont(weight="bold")).pack(anchor="w")

        entry_row = ctk.CTkFrame(student_frame, fg_color="transparent")
        entry_row.pack(fill="x")

        self.student_entry = ctk.CTkEntry(entry_row, placeholder_text="Buscar por nombre o matrícula...")
        self.student_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.student_entry.bind("<Return>", lambda e: self._search_students())

        ctk.CTkButton(entry_row, text="🔍 Buscar", command=self._search_students, width=100).pack(side="right")

        self.student_results_frame = ctk.CTkFrame(student_frame, fg_color="transparent")
        self.student_results_frame.pack(fill="x", pady=(5, 0))

        self.selected_student_label = ctk.CTkLabel(self, text="", text_color="gray70", font=ctk.CTkFont(size=14, weight="bold"))
        self.selected_student_label.pack(padx=20, pady=(0, 10))


        # 🔍 Agregar botón más adelante: “Buscar / Seleccionar alumno”

        # === BUSCAR PRODUCTO ===        
        product_frame = ctk.CTkFrame(self)
        product_frame.pack(fill="x", padx=20, pady=(10, 0))

        ctk.CTkLabel(product_frame, text="Producto o Servicio:", font=ctk.CTkFont(weight="bold")).pack(anchor="w")

        entry_row = ctk.CTkFrame(product_frame, fg_color="transparent")
        entry_row.pack(fill="x")

        self.product_entry = ctk.CTkEntry(entry_row, placeholder_text="Buscar por SKU o descripción...")
        self.product_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.product_entry.bind("<Return>", lambda e: self._search_products())

        ctk.CTkButton(entry_row, text="🔍 Buscar", command=self._search_products, width=100).pack(side="right")

        self.product_results_frame = ctk.CTkFrame(product_frame, fg_color="transparent")
        self.product_results_frame.pack(fill="x", pady=(5, 0))

        # === CARRITO DE COMPRA ===
        self.cart_frame = ctk.CTkScrollableFrame(self)
        self.cart_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # === TOTALES Y BOTÓN COBRAR ===
        totals_frame = ctk.CTkFrame(self)
        totals_frame.pack(fill="x", padx=20, pady=(0, 20))

        self.label_totals = ctk.CTkLabel(
            totals_frame,
            text="Subtotal: $0.00   IVA: $0.00   Total: $0.00",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.label_totals.pack(side="left")

        ctk.CTkButton(
            totals_frame,
            text="💳 Cobrar",
            height=40,
            fg_color="#2CC985",
            command=self._on_pay
        ).pack(side="right")

    def _search_students(self):
        query = self.student_entry.get().strip()
        for w in self.student_results_frame.winfo_children():
            w.destroy()

        if not query:
            return

        students = self.student_repo.search(query)
        if not students:
            ctk.CTkLabel(self.student_results_frame, text="No se encontraron alumnos", text_color="gray70").pack()
            return

        for student in students[:5]:  # Limita los resultados a 5 para no saturar
            text = f"{student.enrollment} - {student.first_name} {student.second_name or ''}"
            ctk.CTkButton(
                self.student_results_frame,
                text=text,
                command=lambda s=student: self._select_student(s),
                fg_color="gray30",
                hover_color="gray20",
                height=35
            ).pack(fill="x", pady=2)

    def _select_student(self, student):
        self.selected_student = student
        self.selected_student_label.configure(            
            text=f"🎓 Alumno seleccionado: ({student.enrollment}) - {student.first_name} {student.second_name or ''}",            
            text_color="white"
        )
        for w in self.student_results_frame.winfo_children():
            w.destroy()

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
                self.product_results_frame,
                text=text,
                command=lambda prod=p: self._add_to_cart(prod),
                fg_color="gray30",
                hover_color="gray20",
                height=35
            ).pack(fill="x", pady=2)

    def _add_to_cart(self, product):
        # Revisar si ya está en carrito
        for item in self.cart:
            if item['sku'] == product.sku:
                item['qty'] += 1
                break
        else:
            self.cart.append({
                'sku': product.sku,
                'description': product.description,
                'price': product.price,
                'tax_rate': product.tax_rate,
                'qty': 1
            })

        # Limpiar búsqueda
        self.product_entry.delete(0, ctk.END)
        for w in self.product_results_frame.winfo_children():
            w.destroy()

        self._refresh_cart()

    def _refresh_cart(self):
        for w in self.cart_frame.winfo_children():
            w.destroy()

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

            # Mostrar producto en carrito
            row = ctk.CTkFrame(self.cart_frame, fg_color="transparent")
            row.pack(fill="x", pady=2)

            ctk.CTkLabel(row, text=f"{item['description']} x{item['qty']}", anchor="w").pack(side="left", fill="x", expand=True)
            ctk.CTkLabel(row, text=f"${total_line:.2f}", anchor="e").pack(side="right")

        # Actualizar totales
        self.label_totals.configure(text=f"Subtotal: ${subtotal:.2f}   IVA: ${tax_total:.2f}   Total: ${total:.2f}")


    def _on_pay(self):
        messagebox.showinfo("POS", "Funcionalidad de cobro aún no implementada")
