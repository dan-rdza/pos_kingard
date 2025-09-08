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
        
        # Frame principal para la cuadrícula
        grid_frame = ctk.CTkFrame(self, fg_color="transparent")
        grid_frame.pack(expand=True, fill="both", padx=30, pady=20)
        
        # Configurar grid 3x2
        for i in range(3):
            grid_frame.grid_rowconfigure(i, weight=1)
        for i in range(2):
            grid_frame.grid_columnconfigure(i, weight=1)
        
        buttons = [
            ("👥", "Gestión de Alumnos", self.open_students, 0, 0),
            ("📦", "Productos/Servicios", self.open_products, 0, 1),
            ("💰", "Punto de Venta", self.open_sales, 1, 0),
            ("📊", "Reportes", self.open_reports, 1, 1),
            ("⚙️", "Configuración", self.open_settings, 2, 0),
            ("🚪", "Cerrar Sesión", self.logout, 2, 1)
        ]
        
        for icon, text, command, row, col in buttons:
            btn_frame = ctk.CTkFrame(grid_frame, fg_color="transparent")
            btn_frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            
            btn = ctk.CTkButton(
                btn_frame,
                text=f"{icon}\n{text}",
                command=command,
                height=100,
                corner_radius=12,
                font=ctk.CTkFont(size=16, weight="bold"),
                fg_color=("gray70", "gray30"),
                hover_color=("gray60", "gray40"),
                text_color="white"
            )
            btn.pack(expand=True, fill="both")
    
    def open_students(self):
        # Limpiar ventana actual
        for widget in self.parent.winfo_children():
            widget.destroy()
                
        # Acceder a la ventana principal (App) correctamente
        main_app = self.parent.master if hasattr(self.parent, 'master') else self.parent
        if hasattr(main_app, 'set_window_size'):
            main_app.set_window_size("students")
        
        # Importar después de configurar tamaño
        from ui.students import StudentsFrame
        
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
        print("=== DEBUG LOGOUT ===")
        print(f"self type: {type(self)}")
        print(f"self.parent type: {type(self.parent)}")
        
        # Verificar si parent tiene los métodos necesarios
        has_set_size = hasattr(self.parent, 'set_window_size')
        has_show_login = hasattr(self.parent, 'show_login')
        has_current_user = hasattr(self.parent, 'current_user')
        
        print(f"Parent has set_window_size: {has_set_size}")
        print(f"Parent has show_login: {has_show_login}")
        print(f"Parent has current_user: {has_current_user}")
        
        if has_set_size and has_show_login and has_current_user:
            print("Parent parece ser la instancia de App")
            self.parent.current_user = None
            self.parent.set_window_size("login")
            self.parent.show_login()
        else:
            print("Parent NO es App, buscando en la jerarquía...")
            # Buscar la verdadera instancia de App
            current = self.parent
            while current and not hasattr(current, 'set_window_size'):
                if hasattr(current, 'master'):
                    current = current.master
                    print(f"Moving to master: {type(current)}")
                else:
                    break
            
            if current and hasattr(current, 'set_window_size'):
                print(f"Found App instance: {type(current)}")
                current.current_user = None
                current.set_window_size("login")
                current.show_login()
            else:
                print("ERROR: No se pudo encontrar la instancia de App")