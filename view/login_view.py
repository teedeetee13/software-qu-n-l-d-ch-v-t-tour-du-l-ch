import customtkinter as ctk
from tkinter import messagebox
from db_manager import DBManager
import auth_session

class LoginView(ctk.CTkFrame):
    def __init__(self, parent, on_login_success):
        super().__init__(parent)
        self.on_login_success = on_login_success
        self.db = DBManager()

        self.configure(fg_color="#F8FAFC")
        self.place(relx=0, rely=0, relwidth=1, relheight=1)

        form_box = ctk.CTkFrame(self, corner_radius=20, width=420, height=480, fg_color="white", border_width=1, border_color="#E2E8F0")
        form_box.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(form_box, text="✈️ TourAdmin", font=ctk.CTkFont(size=32, weight="bold"), text_color="#0F172A").place(relx=0.5, rely=0.18, anchor="center")
        ctk.CTkLabel(form_box, text="Đăng nhập để vào hệ thống", text_color="#64748B", font=ctk.CTkFont(size=14)).place(relx=0.5, rely=0.26, anchor="center")

        self.entry_user = ctk.CTkEntry(form_box, placeholder_text="Tên đăng nhập", width=320, height=50, border_color="#E2E8F0", fg_color="#F8FAFC", font=ctk.CTkFont(size=14))
        self.entry_user.place(relx=0.5, rely=0.4, anchor="center")

        self.entry_pass = ctk.CTkEntry(form_box, placeholder_text="Mật khẩu", show="*", width=320, height=50, border_color="#E2E8F0", fg_color="#F8FAFC", font=ctk.CTkFont(size=14))
        self.entry_pass.place(relx=0.5, rely=0.53, anchor="center")

        ctk.CTkButton(form_box, text="Đăng Nhập", font=ctk.CTkFont(size=16, weight="bold"), width=320, height=50, fg_color="#2563EB", hover_color="#1D4ED8", corner_radius=8, command=self.handle_login).place(relx=0.5, rely=0.72, anchor="center")

    def handle_login(self):
        user, pwd = self.entry_user.get(), self.entry_pass.get()
        role = self.db.check_login(user, pwd)
        
        if role:
            auth_session.login(user, role)
            self.entry_pass.delete(0, 'end')
            self.on_login_success()
        else:
            messagebox.showerror("Lỗi", "Sai tên đăng nhập hoặc mật khẩu!") 