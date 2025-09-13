# ui/menu.py
import customtkinter as ctk

class MainMenu(ctk.CTkFrame):
    def __init__(self, parent, user):
        super().__init__(parent, fg_color="transparent")
        self.parent = parent
        self.user = user
        self.create_widgets()

    def create_widgets(self):
        # Cabecera con usuario
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(pady=(20, 10))

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

        # Contenedor centrado para limitar ancho
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(expand=True)

        wrapper = ctk.CTkFrame(content, fg_color="transparent", width=700)
        wrapper.pack(pady=10)
        wrapper.grid_columnconfigure((0, 1), weight=1)
        wrapper.grid_rowconfigure((0, 1, 2), weight=1)

        # Altura de botón adaptativa
        screen_h = self.winfo_screenheight()
        button_height = 120 if screen_h < 800 else 100
        
        # Botones del menú
        buttons = [
            ("👥", "Gestión de Alumnos", self.parent.show_students, 0, 0),
            ("📦", "Productos/Servicios", self.parent.show_products, 0, 1),
            ("💰", "Punto de Venta", self.parent.show_pos, 1, 0),
            ("📊", "Reportes", self.parent.show_reports, 1, 1),
            ("⚙️", "Configuración", self.parent.show_settings, 2, 0),
            ("🚪", "Cerrar Sesión", self.parent.logout, 2, 1)
        ]

        for icon, text, command, row, col in buttons:
            btn_frame = ctk.CTkFrame(wrapper, fg_color="transparent")
            btn_frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

            ctk.CTkButton(
                btn_frame,
                text=f"{icon}\n{text}",
                command=command,
                height=button_height,
                corner_radius=12,
                font=ctk.CTkFont(size=14, weight="bold"),
                fg_color=("gray70", "gray30"),
                hover_color=("gray60", "gray40"),
                text_color="white"
            ).pack(expand=True, fill="both")
