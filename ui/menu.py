import customtkinter as ctk

class MainMenu(ctk.CTkFrame):
    def __init__(self, parent, user):
        super().__init__(parent, fg_color="transparent")
        self.parent = parent
        self.user = user
        self.create_widgets()
    
    def create_widgets(self):
        # Header con info de usuario
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(pady=20)
        
        ctk.CTkLabel(
            header,
            text=f"👤 {self.user['first_name']} {self.user['second_name']}",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack()
        
        ctk.CTkLabel(
            header,
            text=f"Rol: {self.user['role'].capitalize()}",
            font=ctk.CTkFont(size=12),
            text_color="gray70"
        ).pack()
        
        # Botones del menú
        menu_frame = ctk.CTkFrame(self, fg_color="transparent")
        menu_frame.pack(expand=True, fill="both", padx=50, pady=30)
        
        buttons = [
            ("👥 Gestión de Alumnos", self.open_students),
            ("📦 Productos/Servicios", self.open_products),
            ("💰 Punto de Venta", self.open_sales),
            ("📊 Reportes", self.open_reports),
            ("⚙️ Configuración", self.open_settings),
            ("🚪 Cerrar Sesión", self.logout)
        ]
        
        for text, command in buttons:
            btn = ctk.CTkButton(
                menu_frame,
                text=text,
                command=command,
                height=50,
                corner_radius=10,
                font=ctk.CTkFont(size=14),
                fg_color=("gray70", "gray30"),
                hover_color=("gray60", "gray40")
            )
            btn.pack(fill="x", pady=5)
    
    def open_students(self):
        from .students import StudentsFrame
        # Limpiar ventana actual
        for widget in self.parent.winfo_children():
            widget.destroy()
        # Mostrar módulo de estudiantes
        students_frame = StudentsFrame(self.parent, self.parent.db.get_connection())
        students_frame.pack(fill="both", expand=True)
    
    def open_products(self):
        print("Abriendo módulo de productos...")
    
    def open_sales(self):
        print("Abriendo punto de venta...")
    
    def open_reports(self):
        print("Abriendo reportes...")
    
    def open_settings(self):
        print("Abriendo configuración...")
    
    def logout(self):
        self.parent.current_user = None
        self.parent.show_login()