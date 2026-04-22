import customtkinter as ctk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class ReportView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, corner_radius=0, fg_color="#f0f2f5")
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.create_header()
        self.create_filters()
        self.create_report_content()

    def create_header(self):
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        
        lbl = ctk.CTkLabel(header_frame, text="Báo cáo & Thống kê", font=ctk.CTkFont(family="Arial", size=28, weight="bold"), text_color="#2c3e50")
        lbl.pack(side="left")

    def create_filters(self):
        filter_frame = ctk.CTkFrame(self, fg_color="#ffffff", corner_radius=8, border_width=1, border_color="#e0e0e0", height=80)
        filter_frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        filter_frame.grid_propagate(False)

        # Loại báo cáo
        ctk.CTkLabel(filter_frame, text="Loại báo cáo", font=ctk.CTkFont(family="Arial", size=13, weight="bold"), text_color="#34495e").pack(side="left", padx=(20, 10), pady=(10, 30))
        combo_type = ctk.CTkComboBox(filter_frame, values=["Doanh thu theo tháng", "Doanh thu theo Tour", "Khách hàng mới"], width=200, height=35, corner_radius=5, fg_color="#f0f2f5", border_color="#e0e0e0", button_color="#bdc3c7", text_color="#2c3e50")
        combo_type.place(x=20, y=35)

        # Khoảng thời gian (giả lập UI)
        ctk.CTkLabel(filter_frame, text="Khoảng thời gian", font=ctk.CTkFont(family="Arial", size=13, weight="bold"), text_color="#34495e").place(x=250, y=10)
        combo_time = ctk.CTkComboBox(filter_frame, values=["Năm 2023", "Năm 2024", "Tháng này"], width=200, height=35, corner_radius=5, fg_color="#f0f2f5", border_color="#e0e0e0", button_color="#bdc3c7", text_color="#2c3e50")
        combo_time.place(x=250, y=35)

        # Nút Tạo báo cáo
        ctk.CTkButton(filter_frame, text="Tạo báo cáo", fg_color="#3498db", hover_color="#2980b9", width=120, height=35, corner_radius=5, font=ctk.CTkFont(family="Arial", size=14, weight="bold")).place(x=480, y=35)

    def create_report_content(self):
        content_frame = ctk.CTkFrame(self, fg_color="#ffffff", corner_radius=8, border_width=1, border_color="#e0e0e0")
        content_frame.grid(row=2, column=0, sticky="nsew")
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_rowconfigure(1, weight=1)

        # Tiêu đề biểu đồ
        ctk.CTkLabel(content_frame, text="Biểu đồ Doanh thu (VND)", font=ctk.CTkFont(family="Arial", size=18, weight="bold"), text_color="#2c3e50").grid(row=0, column=0, sticky="w", padx=20, pady=(20, 10))

        # 1. Khu vực vẽ biểu đồ đường (Line Chart)
        chart_container = ctk.CTkFrame(content_frame, fg_color="#f8f9fa", corner_radius=5)
        chart_container.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))

        fig, ax = plt.subplots(figsize=(8, 3), dpi=100)
        fig.patch.set_facecolor('#f8f9fa')
        fig.subplots_adjust(left=0.08, right=0.97, top=0.9, bottom=0.15)
        ax.set_facecolor('#f8f9fa')

        # Dữ liệu mẫu báo cáo 12 tháng
        months = ['T1', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'T8', 'T9', 'T10', 'T11', 'T12']
        revenue = [80, 110, 95, 140, 180, 160, 210, 250, 230, 280, 310, 350] # Triệu VND

        # Vẽ Line Chart
        ax.plot(months, revenue, color='#3498db', marker='o', linewidth=2.5, markersize=6, markerfacecolor='#ffffff', markeredgewidth=2)
        ax.fill_between(months, revenue, alpha=0.1, color='#3498db') # Hiệu ứng bóng gradient dưới đường
        
        ax.set_ylim(0, max(revenue) + 50)
        ax.tick_params(colors='#7f8c8d', labelsize=10)
        
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#e0e0e0')
        ax.spines['bottom'].set_color('#e0e0e0')
        ax.yaxis.grid(True, linestyle='--', alpha=0.5, color='#bdc3c7')

        canvas = FigureCanvasTkAgg(fig, master=chart_container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

        # 2. Bảng Tổng hợp dữ liệu
        table_container = ctk.CTkFrame(content_frame, fg_color="transparent")
        table_container.grid(row=2, column=0, sticky="nsew", padx=20, pady=(0, 20))
        table_container.grid_rowconfigure(1, weight=1)
        table_container.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(table_container, text="Bảng Tổng hợp", font=ctk.CTkFont(family="Arial", size=16, weight="bold"), text_color="#2c3e50").grid(row=0, column=0, sticky="w", pady=(0, 10))

        table_bg = ctk.CTkFrame(table_container, fg_color="#ffffff", corner_radius=5, border_width=1, border_color="#e0e0e0")
        table_bg.grid(row=1, column=0, sticky="nsew")
        table_bg.grid_rowconfigure(0, weight=1)
        table_bg.grid_columnconfigure(0, weight=1)

        columns = ("Tháng", "Doanh thu (VNĐ)", "Số Booking", "Tour phổ biến")
        self.tree = ttk.Treeview(table_bg, columns=columns, show="headings", height=6)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center")
        self.tree.column("Doanh thu (VNĐ)", anchor="e") # Căn phải cho số tiền
        
        self.tree.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)
        self.tree.tag_configure('oddrow', background="#ffffff")
        self.tree.tag_configure('evenrow', background="#f8f9fa")

        # Thêm dữ liệu mẫu vào bảng
        mock_data = [
            ("Tháng 1", "80,000,000", "50", "Vịnh Hạ Long"),
            ("Tháng 2", "110,000,000", "65", "Miền Trung"),
            ("Tháng 3", "95,000,000", "55", "Sapa"),
            ("Tháng 4", "140,000,000", "80", "Vịnh Hạ Long")
        ]
        for i, row in enumerate(mock_data):
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            self.tree.insert("", "end", values=row, tags=(tag,))