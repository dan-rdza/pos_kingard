# main.py
import customtkinter as ctk
from database.database import DatabaseManager
from ui.menu import MainMenu
from ui.login import LoginFrame
from ui.students import StudentsFrame
from ui.products import ProductsFrame
from ui.educational_catalogs import EducationalCatalogsFrame
from ui.pos import POSFrame

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("POS KinGard")
        self.after(100, lambda: self.wm_state("zoomed"))

        self.db = DatabaseManager()
        self.current_user = None

        self.show_login()

    def clear_view(self):
        for widget in self.winfo_children():
            widget.destroy()

    def show_login(self):
        self.clear_view()
        self.login_frame = LoginFrame(self)
        self.login_frame.pack(expand=True, fill="both")

    def show_main_menu(self):
        self.clear_view()
        self.menu_frame = MainMenu(self, self.current_user)
        self.menu_frame.pack(expand=True, fill="both")

    def show_students(self):
        self.clear_view()
        frame = StudentsFrame(self, self.db.get_connection())
        frame.pack(fill="both", expand=True)

    def show_products(self):
        self.clear_view()
        frame = ProductsFrame(self, self.db.get_connection())
        frame.pack(fill="both", expand=True)

    def show_pos(self):        
        self.clear_view()
        POSFrame(self, self.db.get_connection()).pack(fill="both", expand=True)

    def show_catalogs(self):
        self.clear_view()
        frame = EducationalCatalogsFrame(self, self.db.get_connection())
        frame.pack(fill="both", expand=True)        

    def show_settings(self):
        print("Abriendo configuración...")

    def logout(self):
        self.current_user = None
        self.show_login()


if __name__ == "__main__":
    app = App()
    app.mainloop()
