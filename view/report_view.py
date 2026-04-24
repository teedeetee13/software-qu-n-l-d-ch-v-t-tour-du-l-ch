import customtkinter as ctk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from db_manager import DBManager

class ReportView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, corner_radius=0, fg_color="#f0f2f5")
        self.db = DBManager()
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
        self.combo_type = ctk.CTkComboBox(filter_frame, values=["Doanh thu theo tháng", "Doanh thu theo Tour"], width=200, height=35, corner_radius=5, fg_color="#f0f2f5", border_color="#e0e0e0", button_color="#bdc3c7", text_color="#2c3e50")
        self.combo_type.place(x=20, y=35)

        # Khoảng thời gian
        ctk.CTkLabel(filter_frame, text="Khoảng thời gian", font=ctk.CTkFont(family="Arial", size=13, weight="bold"), text_color="#34495e").place(x=250, y=10)
        self.combo_time = ctk.CTkComboBox(filter_frame, values=["Năm 2023", "Năm 2024"], width=200, height=35, corner_radius=5, fg_color="#f0f2f5", border_color="#e0e0e0", button_color="#bdc3c7", text_color="#2c3e50")
        self.combo_time.place(x=250, y=35)

        # Nút Tạo báo cáo
        ctk.CTkButton(filter_frame, text="Tạo báo cáo", fg_color="#3498db", hover_color="#2980b9", width=120, height=35, corner_radius=5, font=ctk.CTkFont(family="Arial", size=14, weight="bold"), command=self.update_report).place(x=480, y=35)

    def create_report_content(self):
        content_frame = ctk.CTkFrame(self, fg_color="#ffffff", corner_radius=8, border_width=1, border_color="#e0e0e0")
        content_frame.grid(row=2, column=0, sticky="nsew")
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_rowconfigure(1, weight=1)

        # Tiêu đề biểu đồ
        ctk.CTkLabel(content_frame, text="Biểu đồ Doanh thu (VND)", font=ctk.CTkFont(family="Arial", size=18, weight="bold"), text_color="#2c3e50").grid(row=0, column=0, sticky="w", padx=20, pady=(20, 10))

        # 1. Khu vực vẽ biểu đồ đường (Line Chart)
        self.chart_container = ctk.CTkFrame(content_frame, fg_color="#f8f9fa", corner_radius=5)
        self.chart_container.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))

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

        self.tree = ttk.Treeview(table_bg, show="headings", height=6)
        self.tree.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)
        self.tree.tag_configure('oddrow', background="#ffffff")
        self.tree.tag_configure('evenrow', background="#f8f9fa")

        # Render nội dung lần đầu tiên
        self.update_report()

    def update_report(self):
        selected_time = self.combo_time.get()
        try:
            selected_year = int(selected_time.replace("Năm ", ""))
        except ValueError:
            selected_year = 2023
            
        report_type = self.combo_type.get()

        # 1. Vẽ Biểu đồ (Clear Canvas cũ trước)
        for widget in self.chart_container.winfo_children():
            widget.destroy()
            
        fig, ax = plt.subplots(figsize=(8, 3), dpi=100)
        fig.patch.set_facecolor('#f8f9fa')
        fig.subplots_adjust(left=0.08, right=0.97, top=0.9, bottom=0.15)
        ax.set_facecolor('#f8f9fa')

        # 2. Cập nhật Bảng (Clear dữ liệu cũ trước)
        for row in self.tree.get_children():
            self.tree.delete(row)
            
        if report_type == "Doanh thu theo tháng":
            summary = self.db.get_report_summary(selected_year)
            months = [f"T{i}" for i in range(1, 13)]
            revenue = [summary[i]['revenue'] / 1000000 for i in range(1, 13)]
            
            ax.plot(months, revenue, color='#3498db', marker='o', linewidth=2.5, markersize=6, markerfacecolor='#ffffff', markeredgewidth=2)
            ax.fill_between(months, revenue, alpha=0.1, color='#3498db')
            
            y_max = max(revenue) + 50 if revenue and max(revenue) > 0 else 100
            ax.set_ylim(0, y_max)
            ax.tick_params(colors='#7f8c8d', labelsize=10)
            
            # Bảng cho Doanh thu theo tháng
            columns = ("Tháng", "Doanh thu (VNĐ)", "Số Booking", "Tour phổ biến")
            self.tree.configure(columns=columns)
            for col in columns: self.tree.heading(col, text=col); self.tree.column(col, anchor="center")
            self.tree.column("Doanh thu (VNĐ)", anchor="e")
            
            for i in range(1, 13):
                best_tour = max(summary[i]['tours'], key=summary[i]['tours'].get) if summary[i]['bookings'] > 0 else "-"
                row_data = (f"Tháng {i}", f"{summary[i]['revenue']:,}", summary[i]['bookings'], best_tour)
                tag = 'evenrow' if i % 2 == 0 else 'oddrow'
                self.tree.insert("", "end", values=row_data, tags=(tag,))
                
        elif report_type == "Doanh thu theo Tour":
            summary = self.db.get_revenue_by_tour_report(selected_year)
            tours = list(summary.keys())
            revenue = [summary[t]['revenue'] / 1000000 for t in tours]
            
            if tours:
                ax.bar(tours, revenue, color='#2ecc71', width=0.6, alpha=0.85)
                # Cắt bớt tên tour nếu quá dài và nghiêng 15 độ để không đè lên nhau
                short_tours = [t[:15] + '...' if len(t) > 15 else t for t in tours]
                ax.set_xticks(range(len(tours)))
                ax.set_xticklabels(short_tours, rotation=15, ha='right')
            
            y_max = max(revenue) * 1.2 if revenue and max(revenue) > 0 else 100
            ax.set_ylim(0, y_max)
            ax.tick_params(colors='#7f8c8d', labelsize=9)
            
            # Bảng cho Doanh thu theo Tour
            columns = ("Tên Tour", "Tổng Doanh thu (VNĐ)", "Số Booking", "Tổng Khách")
            self.tree.configure(columns=columns)
            for col in columns: self.tree.heading(col, text=col); self.tree.column(col, anchor="center")
            self.tree.column("Tên Tour", width=250, anchor="w")
            self.tree.column("Tổng Doanh thu (VNĐ)", anchor="e")
            
            for i, tour in enumerate(tours):
                row_data = (tour, f"{summary[tour]['revenue']:,}", summary[tour]['bookings'], summary[tour]['guests'])
                tag = 'evenrow' if i % 2 == 0 else 'oddrow'
                self.tree.insert("", "end", values=row_data, tags=(tag,))

        # Decorate biểu đồ chung
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#e0e0e0')
        ax.spines['bottom'].set_color('#e0e0e0')
        ax.yaxis.grid(True, linestyle='--', alpha=0.5, color='#bdc3c7')

        canvas = FigureCanvasTkAgg(fig, master=self.chart_container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)