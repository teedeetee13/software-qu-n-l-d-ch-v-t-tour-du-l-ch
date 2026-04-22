import customtkinter as ctk
from tkinter import messagebox
from db_manager import DBManager
import auth_session

class LoginView(ctk.CTkFrame):
    def __init__(self, parent, on_login_success):
        super().__init__(parent)
        self.on_login_success = on_login_success
        self.db = DBManager()

        self.place(relx=0, rely=0, relwidth=1, relheight=1)

        form_box = ctk.CTkFrame(self, corner_radius=15, width=400, height=450, fg_color="white")
        form_box.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(form_box, text="TOUR ADMIN PRO", font=ctk.CTkFont(size=28, weight="bold"), text_color="#2c3e50").place(relx=0.5, rely=0.15, anchor="center")
        ctk.CTkLabel(form_box, text="Đăng nhập để tiếp tục", text_color="gray").place(relx=0.5, rely=0.23, anchor="center")

        self.entry_user = ctk.CTkEntry(form_box, placeholder_text="Tên đăng nhập", width=280, height=45)
        self.entry_user.place(relx=0.5, rely=0.4, anchor="center")

        self.entry_pass = ctk.CTkEntry(form_box, placeholder_text="Mật khẩu", show="*", width=280, height=45)
        self.entry_pass.place(relx=0.5, rely=0.55, anchor="center")

        ctk.CTkButton(form_box, text="Đăng Nhập", font=ctk.CTkFont(size=16, weight="bold"), width=280, height=50, command=self.handle_login).place(relx=0.5, rely=0.75, anchor="center")

    def handle_login(self):
        user, pwd = self.entry_user.get(), self.entry_pass.get()
        role = self.db.check_login(user, pwd)
        
        if role:
            auth_session.login(user, role)
            self.entry_pass.delete(0, 'end')
            self.on_login_success()
        else:
            messagebox.showerror("Lỗi", "Sai tên đăng nhập hoặc mật khẩu!") 