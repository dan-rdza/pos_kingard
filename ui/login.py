# ui/login.py

import customtkinter as ctk
from PIL import Image
from pathlib import Path

ALLOW_SUPERUSER = True
class LoginFrame(ctk.CTkFrame):
        

    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.parent = parent
        self.create_widgets()
    
    def create_widgets(self):        
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(expand=True, fill="both", padx=50, pady=50)
        inner_container = ctk.CTkFrame(container, fg_color="transparent")
        inner_container.pack(expand=True)
        inner_container.grid_columnconfigure(0, weight=1)
        
        header_frame = ctk.CTkFrame(inner_container, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 40))

        try:
            root_dir = Path(__file__).resolve().parent.parent  # sube un nivel desde ui/
            logo_path = root_dir / "assets" / "images" / "logo.png"

            if not logo_path.exists():
                raise FileNotFoundError(f"Logo no encontrado: {logo_path}")
            
            logo_image = ctk.CTkImage(
                light_image=Image.open(logo_path),
                dark_image=Image.open(logo_path),
                size=(80, 80)
            )
            ctk.CTkLabel(header_frame, image=logo_image, text="").pack(pady=(0, 10))
        except Exception as e:
            print(f"Error cargando logo: {e}")
            ctk.CTkLabel(header_frame, text="👶", font=ctk.CTkFont(size=40)).pack(pady=(0, 10))

        ctk.CTkLabel(header_frame, text="Preescolar\nLibertad y Creatividad", font=ctk.CTkFont(size=22, weight="bold")).pack()
        ctk.CTkLabel(header_frame, text="Inicio de Sesión", font=ctk.CTkFont(size=14), text_color="gray70").pack()

        form_frame = ctk.CTkFrame(inner_container, fg_color="transparent")
        form_frame.grid(row=1, column=0, sticky="nsew", pady=(0, 30))
        form_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(form_frame, text="Usuario", font=ctk.CTkFont(size=12, weight="bold")).grid(row=0, column=0, sticky="w", pady=(0, 5))
        self.username = ctk.CTkEntry(form_frame, placeholder_text="Ingresa tu usuario", height=45, width=400, border_width=2, corner_radius=10, fg_color=("#FFFFFF", "#2B2B2B"), font=ctk.CTkFont(size=14))
        self.username.grid(row=1, column=0, sticky="ew", pady=(0, 20))

        ctk.CTkLabel(form_frame, text="Contraseña", font=ctk.CTkFont(size=12, weight="bold")).grid(row=2, column=0, sticky="w", pady=(0, 5))
        self.password = ctk.CTkEntry(form_frame, placeholder_text="Ingresa tu contraseña", show="•", height=45, width=400, border_width=2, corner_radius=10, fg_color=("#FFFFFF", "#2B2B2B"), font=ctk.CTkFont(size=14))
        self.password.grid(row=3, column=0, sticky="ew", pady=(0, 25))

        self.login_btn = ctk.CTkButton(form_frame, text="Iniciar Sesión", command=self.login, height=45, width=400, border_width=0, corner_radius=10, fg_color="#2CC985", hover_color="#207A4C", font=ctk.CTkFont(size=14, weight="bold"))
        self.login_btn.grid(row=4, column=0, sticky="ew")
        self.password.bind("<Return>", lambda e: self.login())

        footer_frame = ctk.CTkFrame(inner_container, fg_color="transparent")
        footer_frame.grid(row=2, column=0, sticky="ew")
        ctk.CTkLabel(footer_frame, text="© 2025 POS KinGard - v1.0", font=ctk.CTkFont(size=10), text_color="gray60").pack(side="right")
        self.parent.bind("<Control-Shift-S>", self._superuser_shortcut)


    def login(self):
        username = self.username.get().strip()
        password = self.password.get().strip()

        # 🛡️ Modo superusuario sin BD
        if ALLOW_SUPERUSER and username == "root" and password == "soyDios":
            print("⚠️ Superusuario accedió sin base de datos")
            user = {
                "id": 0,
                "employee_code": "SUPERUSER",
                "first_name": "Super",
                "second_name": "Usuario",
                "role": "admin",
                "job_title": "ADMINISTRADOR DEL SISTEMA",
            }
            self.parent.current_user = user
            self.parent.show_main_menu()
            return

        # 🔐 Autenticación normal
        user = self.parent.db.authenticate_user(username, password)
        if user:
            self.parent.current_user = user
            self.parent.show_main_menu()
        else:
            self.show_error("Credenciales incorrectas o usuario inactivo")

    def _superuser_shortcut(self, event=None):
        if ALLOW_SUPERUSER:
            print("⚠️ Atajo de superusuario activado")
            user = {
                "id": 0,
                "employee_code": "SUPERUSER",
                "first_name": "Super",
                "second_name": "Usuario",
                "role": "admin",
                "job_title": "ADMINISTRADOR DEL SISTEMA"
            }
            self.parent.current_user = user
            self.parent.show_main_menu()


    def show_error(self, message):
        self.login_btn.configure(fg_color="#FF5555", hover_color="#CC4444", text="Intenta nuevamente")
        print(message)

    def show_success(self, message):
        self.login_btn.configure(fg_color="#2CC985", hover_color="#207A4C", text="Accediendo...")
        print(message)
