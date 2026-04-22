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
        self.title("TourAdmin - Quản lý Dịch vụ Đặt Tour")
        self.geometry("1280x800")
        self.style_treeview()

        # Hiển thị màn hình Login đầu tiên
        self.current_view = LoginView(self, self.show_main_dashboard)

    def show_main_dashboard(self):
        self.current_view.destroy() # Xóa màn hình login
        
        # --- Bố cục App Chính ---
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # 1. Sidebar (Menu)
        self.sidebar = ctk.CTkFrame(self, width=260, corner_radius=0, fg_color="#0F172A")
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(7, weight=1)

        # Logo & User
        ctk.CTkLabel(self.sidebar, text="✈️ TourAdmin", font=ctk.CTkFont(size=26, weight="bold"), text_color="white").pack(pady=(40, 10))
        ctk.CTkLabel(self.sidebar, text=f"Hi, {auth_session.current_user} ({auth_session.current_role})", text_color="#94A3B8", font=ctk.CTkFont(size=14)).pack(pady=(0,30))

        # Nút chuyển trang
        btn_font = ctk.CTkFont(size=15, weight="bold")
        self.btn_dashboard = ctk.CTkButton(self.sidebar, text="📊 Tổng quan", font=btn_font, anchor="w", height=45, fg_color="#2563EB", hover_color="#1E293B", command=lambda: self.switch_view(DashboardView, self.btn_dashboard))
        self.btn_dashboard.pack(fill="x", padx=15, pady=8)

        self.btn_tour = ctk.CTkButton(self.sidebar, text="📌 Quản lý Tour", font=btn_font, anchor="w", height=45, fg_color="transparent", text_color="#CBD5E1", hover_color="#1E293B", command=lambda: self.switch_view(TourView, self.btn_tour))
        self.btn_tour.pack(fill="x", padx=15, pady=8)

        self.btn_customer = ctk.CTkButton(self.sidebar, text="👥 Quản lý Khách hàng", font=btn_font, anchor="w", height=45, fg_color="transparent", text_color="#CBD5E1", hover_color="#1E293B", command=lambda: self.switch_view(CustomerView, self.btn_customer))
        self.btn_customer.pack(fill="x", padx=15, pady=8)

        self.btn_booking = ctk.CTkButton(self.sidebar, text="🎫 Quản lý Đặt chỗ", font=btn_font, anchor="w", height=45, fg_color="transparent", text_color="#CBD5E1", hover_color="#1E293B", command=lambda: self.switch_view(BookingView, self.btn_booking))
        self.btn_booking.pack(fill="x", padx=15, pady=8)
        
        # Nút đăng xuất
        ctk.CTkButton(self.sidebar, text="Đăng xuất", font=btn_font, height=45, fg_color="#EF4444", hover_color="#DC2626", command=self.logout).pack(side="bottom", fill="x", padx=20, pady=30)

        # 2. Khu vực hiển thị nội dung
        self.content_area = ctk.CTkFrame(self, fg_color="#F8FAFC")
        self.content_area.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        self.content_area.grid_rowconfigure(0, weight=1)
        self.content_area.grid_columnconfigure(0, weight=1)
        
        self.current_content = None
        self.switch_view(DashboardView, self.btn_dashboard)

    def switch_view(self, view_class, active_btn):
        if self.current_content:
            self.current_content.destroy()
        
        # Reset màu tất cả nút
        for btn in [self.btn_dashboard, self.btn_tour, self.btn_customer, self.btn_booking]:
            btn.configure(fg_color="transparent", text_color="#CBD5E1")
            
        # Đặt màu cho nút active
        active_btn.configure(fg_color="#2563EB", text_color="white")

        self.current_content = view_class(self.content_area)
        self.current_content.grid(row=0, column=0, sticky="nsew")

    def logout(self):
        auth_session.logout()
        for widget in self.winfo_children(): widget.destroy() # Xóa sạch giao diện hiện tại
        self.current_view = LoginView(self, self.show_main_dashboard) # Bật lại Login

    def style_treeview(self):
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", rowheight=45, font=('Segoe UI', 11), borderwidth=0, fieldbackground="#FFFFFF", background="#FFFFFF")
        style.configure("Treeview.Heading", background="#F1F5F9", foreground="#475569", font=('Segoe UI', 12, 'bold'), borderwidth=0, padding=10)
        style.map("Treeview.Heading", background=[('active', '#E2E8F0')])
        style.map("Treeview", background=[("selected", "#EFF6FF")], foreground=[("selected", "#1E3A8A")])

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()