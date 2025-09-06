import customtkinter as ctk
from database import Database
from PIL import Image, ImageTk
import os
from pathlib import Path
from ui.menu import MainMenu

# Configurar apariencia global
ctk.set_appearance_mode("dark")  # "dark", "light", "system"
ctk.set_default_color_theme("green")  # "blue", "green", "dark-blue"

deployment = True
user = {'id': 1, 'employee_code': 'ADMIN001', 'first_name': 'Administrador', 'second_name': 'Sistema', 'role': 'admin'}

class LoginFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.parent = parent
        self.create_widgets()
    
    def create_widgets(self):
        # Contenedor principal para centrar todo
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(expand=True, fill="both", padx=50, pady=50)
        
        # Frame interno para limitar el ancho máximo
        inner_container = ctk.CTkFrame(container, fg_color="transparent")
        inner_container.pack(expand=True)
        inner_container.grid_columnconfigure(0, weight=1)  # Centrar el contenido
        
        # Logo/Header
        header_frame = ctk.CTkFrame(inner_container, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 40))
        
        # Cargar imagen del logo desde assets/images/
        try:
            base_dir = Path(__file__).parent
            logo_path = base_dir / "assets" / "images" / "logo.png"
            
            if not logo_path.exists():
                raise FileNotFoundError(f"Logo no encontrado: {logo_path}")
            
            logo_image = ctk.CTkImage(
                light_image=Image.open(logo_path),
                dark_image=Image.open(logo_path),
                size=(80, 80)
            )
            
            logo_label = ctk.CTkLabel(
                header_frame, 
                image=logo_image,
                text=""
            )
            logo_label.image = logo_image
            logo_label.pack(pady=(0, 10))
            
        except Exception as e:
            print(f"Error cargando logo: {e}")
            ctk.CTkLabel(
                header_frame, 
                text="👶",
                font=ctk.CTkFont(size=40)
            ).pack(pady=(0, 10))
        
        ctk.CTkLabel(
            header_frame,
            text=f"Preescolar\nLibertad y Creatividad",
            font=ctk.CTkFont(size=22, weight="bold")
        ).pack()
        
        ctk.CTkLabel(
            header_frame,
            text="Inicio de Sesión",
            font=ctk.CTkFont(size=14),
            text_color="gray70"
        ).pack()
        
        # Formulario de login con ancho máximo
        form_frame = ctk.CTkFrame(inner_container, fg_color="transparent")
        form_frame.grid(row=1, column=0, sticky="nsew", pady=(0, 30))
        
        # Configurar columnas para centrar el contenido
        form_frame.grid_columnconfigure(0, weight=1)
        
        # Campo usuario
        user_label = ctk.CTkLabel(
            form_frame, 
            text="Usuario",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        user_label.grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        self.username = ctk.CTkEntry(
            form_frame,
            placeholder_text="Ingresa tu usuario",
            height=45,
            width=400,  # Ancho fijo
            border_width=2,
            corner_radius=10,
            fg_color=("#FFFFFF", "#2B2B2B"),
            font=ctk.CTkFont(size=14)
        )
        self.username.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        
        # Campo contraseña
        pass_label = ctk.CTkLabel(
            form_frame, 
            text="Contraseña",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        pass_label.grid(row=2, column=0, sticky="w", pady=(0, 5))
        
        self.password = ctk.CTkEntry(
            form_frame,
            placeholder_text="Ingresa tu contraseña",
            show="•",
            height=45,
            width=400,  # Ancho fijo
            border_width=2,
            corner_radius=10,
            fg_color=("#FFFFFF", "#2B2B2B"),
            font=ctk.CTkFont(size=14)
        )
        self.password.grid(row=3, column=0, sticky="ew", pady=(0, 25))
        
        # Botón de login
        self.login_btn = ctk.CTkButton(
            form_frame,
            text="Iniciar Sesión",
            command=self.login,
            height=45,
            width=400,  # Ancho fijo
            border_width=0,
            corner_radius=10,
            fg_color="#2CC985",
            hover_color="#207A4C",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.login_btn.grid(row=4, column=0, sticky="ew")
        
        # Enlace de enter para login
        self.password.bind("<Return>", lambda e: self.login())
        
        # Footer
        footer_frame = ctk.CTkFrame(inner_container, fg_color="transparent")
        footer_frame.grid(row=2, column=0, sticky="ew")
        
        ctk.CTkLabel(
            footer_frame,
            text="© 2024 POS KinGard - v1.0",
            font=ctk.CTkFont(size=10),
            text_color="gray60"
        ).pack(side="right")
    
    def login(self):
        username = self.username.get().strip()
        password = self.password.get().strip()
        
        if (not username or not password):
            self.show_error("Por favor completa todos los campos")
            return
        
        # 🔐 AUTENTICACIÓN REAL contra BD
        user = self.parent.db.authenticate_user(username, password)        
        print(user)

        if user:
            self.show_success(f"¡Bienvenido(a) {user['first_name']}!")
            self.parent.current_user = user  # Guardar usuario actual
            self.parent.show_main_menu()     # Mostrar menú principal
        else:
            self.show_error("Credenciales incorrectas o usuario inactivo")
    
    def show_error(self, message):
        # Cambiar estilo temporal a error
        self.login_btn.configure(
            fg_color="#FF5555",  # Rojo error
            hover_color="#CC4444",
            text="Intenta nuevamente"
        )
        print(message)
    
    def show_success(self, message):
        # Cambiar estilo temporal a éxito
        self.login_btn.configure(
            fg_color="#2CC985",  # Verde éxito
            hover_color="#207A4C",
            text="Accediendo..."
        )
        print(message)

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("POS KinGard")
        self.geometry("400x550")
        self.minsize(400, 550)        
                        
        # Inicializar base de datos
        self.db = Database()
        self.current_user = None
        
        # Mostrar login
        self.show_login()
        self.after(100, self.center_window)
    
    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")
    
    def show_login(self):
        for widget in self.winfo_children():
            widget.destroy()
            
        self.login_frame = LoginFrame(self)
        self.login_frame.pack(expand=True, fill="both")

    def show_main_menu(self):
        """Mostrar menú principal después del login"""
        for widget in self.winfo_children():
            widget.destroy()
            
        self.menu_frame = MainMenu(self, self.current_user)
        self.menu_frame.pack(expand=True, fill="both")  

        self.after(100, self.center_window)      

if __name__ == "__main__":
    app = App()
    app.mainloop()