import customtkinter as ctk
from tkinter import ttk
import auth_session
from view.login_view import LoginView
from view.tour_view import TourView
from view.customer_view import CustomerView
from view.booking_view import BookingView
from view.dashboard_view import DashboardView

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

class MainApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("TourAdmin - Hệ thống Quản lý Tour")
        self.geometry("1200x750")
        self.style_treeview()

        # Hiển thị màn hình Login đầu tiên
        self.current_view = LoginView(self, self.show_main_dashboard)

    def show_main_dashboard(self):
        self.current_view.destroy() # Xóa màn hình login
        
        # --- Bố cục App Chính ---
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # 1. Sidebar (Menu)
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color="#2c3e50")
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(7, weight=1)

        ctk.CTkLabel(self.sidebar, text="TourAdmin", font=ctk.CTkFont(size=24, weight="bold"), text_color="white").pack(pady=30)
        ctk.CTkLabel(self.sidebar, text=f"👤 {auth_session.current_user} ({auth_session.current_role})", text_color="#f1c40f").pack(pady=(0,20))

        # Nút chuyển trang
        self.btn_dashboard = ctk.CTkButton(self.sidebar, text="📊 Tổng quan (Dashboard)", anchor="w", fg_color="#3498db", command=lambda: self.switch_view(DashboardView, self.btn_dashboard))
        self.btn_dashboard.pack(fill="x", padx=10, pady=5)

        self.btn_tour = ctk.CTkButton(self.sidebar, text="📌 Quản lý Tour", anchor="w", fg_color="transparent", command=lambda: self.switch_view(TourView, self.btn_tour))
        self.btn_tour.pack(fill="x", padx=10, pady=5)

        self.btn_customer = ctk.CTkButton(self.sidebar, text="👥 Quản lý Khách hàng", anchor="w", fg_color="transparent", command=lambda: self.switch_view(CustomerView, self.btn_customer))
        self.btn_customer.pack(fill="x", padx=10, pady=5)

        self.btn_booking = ctk.CTkButton(self.sidebar, text="🎫 Quản lý Đặt chỗ", anchor="w", fg_color="transparent", command=lambda: self.switch_view(BookingView, self.btn_booking))
        self.btn_booking.pack(fill="x", padx=10, pady=5)
        
        # Nút đăng xuất
        ctk.CTkButton(self.sidebar, text="Đăng xuất", fg_color="#e74c3c", command=self.logout).pack(side="bottom", fill="x", padx=20, pady=20)

        # 2. Khu vực hiển thị nội dung
        self.content_area = ctk.CTkFrame(self, fg_color="transparent")
        self.content_area.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.content_area.grid_rowconfigure(0, weight=1)
        self.content_area.grid_columnconfigure(0, weight=1)
        
        self.current_content = None
        self.switch_view(DashboardView, self.btn_dashboard)

    def switch_view(self, view_class, active_btn):
        if self.current_content:
            self.current_content.destroy()
        
        # Reset màu tất cả nút
        for btn in [self.btn_dashboard, self.btn_tour, self.btn_customer, self.btn_booking]:
            btn.configure(fg_color="transparent")
            
        # Đặt màu cho nút active
        active_btn.configure(fg_color="#3498db")

        self.current_content = view_class(self.content_area)
        self.current_content.grid(row=0, column=0, sticky="nsew")

    def logout(self):
        auth_session.logout()
        for widget in self.winfo_children(): widget.destroy() # Xóa sạch giao diện hiện tại
        self.current_view = LoginView(self, self.show_main_dashboard) # Bật lại Login

    def style_treeview(self):
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", rowheight=35, font=('Arial', 11), borderwidth=0)
        style.configure("Treeview.Heading", background="#e1e8ed", font=('Arial', 12, 'bold'), borderwidth=0)
        style.map("Treeview", background=[("selected", "#3498db")])

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()