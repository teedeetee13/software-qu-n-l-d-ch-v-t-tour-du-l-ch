import customtkinter as ctk
import os
import signal
from tkinter import ttk
from PIL import Image, ImageDraw, ImageFont
import auth_session
from view.login_view import LoginView
from view.tour_view import TourView
from view.customer_view import CustomerView
from view.booking_view import BookingView
from view.schedule_view import ScheduleView
from view.payment_view import PaymentView
from view.dashboard_view import DashboardView
from view.report_view import ReportView
from view.user_view import UserView
from view.guide_view import GuideView

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")


def _make_avatar(name: str, role: str, size: int = 42) -> ctk.CTkImage:
    """Tạo ảnh avatar tròn với chữ tắt tên người dùng."""
    parts = [p for p in name.split() if p]
    initials = parts[0][0].upper() if parts else "U"
    if len(parts) > 1:
        initials += parts[-1][0].upper()

    bg = "#3498db" if role == "Admin" else "#27ae60"

    scale = 4
    s = size * scale
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse([0, 0, s - 1, s - 1], fill=bg)

    font = None
    font_size = int(s * 0.38)
    for path in [
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "arial.ttf",
    ]:
        try:
            font = ImageFont.truetype(path, font_size)
            break
        except OSError:
            pass
    if font is None:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), initials, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(
        ((s - tw) / 2 - bbox[0], (s - th) / 2 - bbox[1]),
        initials, fill="white", font=font,
    )

    img = img.resize((size, size), Image.LANCZOS)
    return ctk.CTkImage(light_image=img, dark_image=img, size=(size, size))


class MainApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("TourAdmin - Quản lý Dịch vụ Đặt Tour")
        self.geometry("1280x800")
        self.style_treeview()
        
        # Bắt sự kiện khi tắt ứng dụng (nhấn nút X góc phải)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Hiển thị màn hình Login đầu tiên
        self.current_view = LoginView(self, self.show_main_dashboard)

    def show_main_dashboard(self):
        self.current_view.destroy() # Xóa màn hình login
        
        # --- Bố cục App Chính ---
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # 1. Sidebar (Menu)
        self.sidebar = ctk.CTkFrame(self, width=240, corner_radius=0, fg_color="#2c3e50")
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(7, weight=1)

        # Logo
        ctk.CTkLabel(self.sidebar, text="TourAdmin", font=ctk.CTkFont(family="Arial", size=24, weight="bold"), text_color="#ecf0f1").pack(pady=(40, 30))
        
        # Divider
        divider = ctk.CTkFrame(self.sidebar, height=1, fg_color="#34495e")
        divider.pack(fill="x", padx=20, pady=(0, 20))

        # Reset btn_user để tránh tham chiếu cũ từ phiên Admin trước
        self.btn_user = None

        # Nút chuyển trang
        self.btn_dashboard = self.create_sidebar_btn("Dashboard", DashboardView)
        self.btn_tour      = self.create_sidebar_btn("Quản lý Tour", TourView)
        self.btn_schedule  = self.create_sidebar_btn("Lịch Khởi Hành", ScheduleView)
        self.btn_guide     = self.create_sidebar_btn("Hướng Dẫn Viên", GuideView)
        self.btn_booking   = self.create_sidebar_btn("Quản lý Đặt chỗ", BookingView)
        self.btn_payment   = self.create_sidebar_btn("Thanh Toán", PaymentView)
        self.btn_customer  = self.create_sidebar_btn("Khách hàng", CustomerView)
        self.btn_report    = self.create_sidebar_btn("Báo cáo", ReportView)

        if auth_session.current_role == "Admin":
            self.btn_user = self.create_sidebar_btn("Quản lý User", UserView)

        # Nút đăng xuất
        ctk.CTkButton(self.sidebar, text="Đăng xuất", font=ctk.CTkFont(family="Arial", size=16), height=50, corner_radius=0, fg_color="transparent", text_color="#bdc3c7", hover_color="#e74c3c", anchor="w", command=self.logout).pack(side="bottom", fill="x", pady=20)

        # 2. Main Container
        self.main_container = ctk.CTkFrame(self, fg_color="#f0f2f5", corner_radius=0)
        self.main_container.grid(row=0, column=1, sticky="nsew")
        self.main_container.grid_rowconfigure(1, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)

        # Top Header
        self.top_header = ctk.CTkFrame(self.main_container, height=60, fg_color="#ffffff", corner_radius=0)
        self.top_header.grid(row=0, column=0, sticky="ew")
        self.top_header.grid_propagate(False)
        
        # Search in top header
        self.top_search = ctk.CTkEntry(self.top_header, placeholder_text="Tìm kiếm...", width=300, height=30, corner_radius=15, fg_color="#f0f2f5", border_color="#e0e0e0", text_color="#95a5a6")
        self.top_search.pack(side="left", padx=30, pady=15)

        # User Profile — avatar tròn + tên + badge role
        from db_manager import DBManager
        _db = DBManager()
        _users = _db.get_all_users()
        full_name = next(
            (u[2] for u in _users if u[1] == auth_session.current_user),
            auth_session.current_user or "Admin",
        )
        role = auth_session.current_role or "Staff"

        profile_frame = ctk.CTkFrame(self.top_header, fg_color="transparent")
        profile_frame.pack(side="right", padx=(8, 24), pady=8)

        avatar_img = _make_avatar(full_name, role, size=42)
        ctk.CTkLabel(profile_frame, image=avatar_img, text="").pack(side="left", padx=(0, 10))

        info_frame = ctk.CTkFrame(profile_frame, fg_color="transparent")
        info_frame.pack(side="left")

        ctk.CTkLabel(
            info_frame, text=full_name,
            font=ctk.CTkFont(family="Arial", size=13, weight="bold"),
            text_color="#2c3e50",
        ).pack(anchor="w")

        badge_color = "#3498db" if role == "Admin" else "#27ae60"
        badge = ctk.CTkFrame(info_frame, fg_color=badge_color, corner_radius=8)
        badge.pack(anchor="w", pady=(2, 0))
        ctk.CTkLabel(
            badge, text=role,
            font=ctk.CTkFont(family="Arial", size=10, weight="bold"),
            text_color="white",
        ).pack(padx=8, pady=1)

        header_separator = ctk.CTkFrame(self.main_container, height=1, fg_color="#e0e0e0", corner_radius=0)
        header_separator.grid(row=0, column=0, sticky="sew")

        # Content Area
        self.content_area = ctk.CTkFrame(self.main_container, fg_color="#f0f2f5", corner_radius=0)
        self.content_area.grid(row=1, column=0, sticky="nsew", padx=30, pady=20)
        self.content_area.grid_rowconfigure(0, weight=1)
        self.content_area.grid_columnconfigure(0, weight=1)
        
        self.current_content = None
        self.switch_view(DashboardView, self.btn_dashboard)

    def create_sidebar_btn(self, text, view_class):
        btn = ctk.CTkButton(self.sidebar, text=f"   {text}", font=ctk.CTkFont(family="Arial", size=16), anchor="w", height=50, corner_radius=0, fg_color="transparent", text_color="#bdc3c7", hover_color="#34495e")
        btn.configure(command=lambda: self.switch_view(view_class, btn))
        btn.pack(fill="x", pady=0)
        return btn

    def switch_view(self, view_class, active_btn):
        if self.current_content:
            self.current_content.destroy()
        
        all_btns = [self.btn_dashboard, self.btn_tour, self.btn_schedule, self.btn_guide,
                    self.btn_customer, self.btn_booking, self.btn_payment, self.btn_report]
        if getattr(self, 'btn_user', None) is not None:
            all_btns.append(self.btn_user)
        for btn in all_btns:
            btn.configure(fg_color="transparent", text_color="#bdc3c7", font=ctk.CTkFont(family="Arial", size=16, weight="normal"))
        active_btn.configure(fg_color="#3498db", text_color="#ffffff", font=ctk.CTkFont(family="Arial", size=16, weight="bold"))

        self.current_content = view_class(self.content_area)
        self.current_content.grid(row=0, column=0, sticky="nsew")

    def logout(self):
        auth_session.logout()
        
        # Xóa tuần tự các widget thay vì dùng winfo_children() để tránh lỗi ngầm
        if hasattr(self, 'current_content') and self.current_content:
            self.current_content.destroy() # Kích hoạt hàm tắt animation trong Dashboard
            self.current_content = None
        if hasattr(self, 'sidebar'):
            self.sidebar.destroy()
        if hasattr(self, 'main_container'):
            self.main_container.destroy()
            
        self.current_view = LoginView(self, self.show_main_dashboard) # Bật lại Login

    def style_treeview(self):
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", rowheight=50, font=('Arial', 13), borderwidth=0, fieldbackground="#ffffff", background="#ffffff", foreground="#2c3e50")
        style.configure("Treeview.Heading", background="#f8f9fa", foreground="#34495e", font=('Arial', 13, 'bold'), borderwidth=0, padding=10)
        style.map("Treeview.Heading", background=[('active', '#e0e0e0')])
        style.map("Treeview", background=[("selected", "#e8f5e9")], foreground=[("selected", "#2c3e50")])
        style.layout("Treeview", [('Treeview.treearea', {'sticky': 'nswe'})]) 

    def on_closing(self):
        # Đảm bảo tắt biểu đồ / animation hiện hành trước khi thoát
        if hasattr(self, 'current_content') and self.current_content:
            self.current_content.destroy()
        
        # Chỉ ngắt mainloop ở đây, KHÔNG gọi lệnh exit bên trong callback của Tkinter   
        self.quit()

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.SIG_IGN)

    from database import init_db
    init_db()

    app = MainApp()
    app.mainloop()
    
    # Dùng os._exit(0) để tắt nóng và hủy triệt để mọi tác vụ ngầm của Matplotlib/Tkinter
    os._exit(0)