import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.animation as animation
from db_manager import DBManager
import datetime

class DashboardView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, corner_radius=0, fg_color="#f0f2f5")
        self.db = DBManager()
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.create_header()
        self.create_summary_cards()
        self.create_charts_section()

    def create_header(self):
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        
        lbl = ctk.CTkLabel(header_frame, text="Tổng quan Thống kê", font=ctk.CTkFont(family="Arial", size=28, weight="bold"), text_color="#2c3e50")
        lbl.pack(side="left")

    def create_summary_cards(self):
        # Khu vực chứa các thẻ thống kê nhanh
        cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        cards_frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        cards_frame.grid_columnconfigure((0, 1, 2), weight=1)

        def create_card(parent, title, value, color, col):
            card = ctk.CTkFrame(parent, fg_color="#ffffff", corner_radius=8, border_width=1, border_color="#e0e0e0", height=100)
            card.grid(row=0, column=col, sticky="ew", padx=(0 if col==0 else 10, 0 if col==2 else 10))
            card.grid_propagate(False)
            
            ctk.CTkLabel(card, text=title, font=ctk.CTkFont(family="Arial", size=14), text_color="#7f8c8d").pack(anchor="w", padx=20, pady=(15, 5))
            ctk.CTkLabel(card, text=value, font=ctk.CTkFont(family="Arial", size=26, weight="bold"), text_color=color).pack(anchor="w", padx=20)

        revenue, bookings, customers, tours = self.db.get_dashboard_stats()
        create_card(cards_frame, "Tổng Doanh Thu", f"{revenue:,} ₫", "#2ecc71", 0)
        create_card(cards_frame, "Tour Đang Chạy", f"{tours} Tour", "#3498db", 1)
        create_card(cards_frame, "Khách Hàng", f"{customers} Khách", "#9b59b6", 2)

    def create_charts_section(self):
        charts_container = ctk.CTkFrame(self, fg_color="transparent")
        charts_container.grid(row=2, column=0, sticky="nsew")
        charts_container.grid_columnconfigure((0, 1), weight=1, uniform="chart_group")
        charts_container.grid_rowconfigure(0, weight=1)

        # --- BIỂU ĐỒ 1: DOANH THU (Cột) ---
        bar_chart_frame = ctk.CTkFrame(charts_container, fg_color="#ffffff", corner_radius=8, border_width=1, border_color="#e0e0e0")
        bar_chart_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        ctk.CTkLabel(bar_chart_frame, text="Doanh thu (6 tháng gần nhất)", font=ctk.CTkFont(family="Arial", size=16, weight="bold"), text_color="#2c3e50").pack(anchor="w", padx=20, pady=(20, 0))

        self.fig1, self.ax1 = plt.subplots(figsize=(5, 4), dpi=100)
        self.fig1.patch.set_facecolor('#ffffff') 
        self.fig1.subplots_adjust(left=0.15, right=0.95, top=0.9, bottom=0.15)
        self.ax1.set_facecolor('#ffffff')        
        
        # Lấy dữ liệu 6 tháng gần nhất từ DB
        current_month = datetime.datetime.now().month
        rev_data = self.db.get_monthly_revenue()
        
        self.months = []
        self.target_values = []
        for i in range(5, -1, -1):
            m = current_month - i
            if m <= 0: m += 12
            self.months.append(f"T{m}")
            self.target_values.append(rev_data.get(m, 0) / 1000000) # Triệu VNĐ

        self.current_values = [0] * len(self.months)        # Bắt đầu từ 0 để tạo animation
        
        # Vẽ các cột (Ban đầu chiều cao là 0)
        self.bars = self.ax1.bar(self.months, self.current_values, color='#3498db', width=0.55, edgecolor='none', alpha=0.85, zorder=3)
        max_target = max(self.target_values) if self.target_values and max(self.target_values) > 0 else 100
        self.ax1.set_ylim(0, max_target * 1.2)
        self.ax1.set_ylabel("Triệu VNĐ", color="#7f8c8d", fontsize=10)
        self.ax1.tick_params(colors='#34495e', labelsize=9)
        
        # Làm đẹp cho biểu đồ (Phẳng, hiện đại)
        self.ax1.spines['top'].set_visible(False)
        self.ax1.spines['right'].set_visible(False)
        self.ax1.spines['left'].set_color('#e0e0e0')
        self.ax1.spines['bottom'].set_color('#e0e0e0')
        self.ax1.yaxis.grid(True, linestyle='--', alpha=0.5, color='#bdc3c7', zorder=0)
        
        self.canvas1 = FigureCanvasTkAgg(self.fig1, master=bar_chart_frame)
        self.canvas1.draw()
        self.canvas1.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=(10, 20))
        
        # --- BIỂU ĐỒ 2: ĐẶT CHỖ THEO TOUR (Tròn) ---
        pie_chart_frame = ctk.CTkFrame(charts_container, fg_color="#ffffff", corner_radius=8, border_width=1, border_color="#e0e0e0")
        pie_chart_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        
        ctk.CTkLabel(pie_chart_frame, text="Tỷ lệ Đặt chỗ theo Tour", font=ctk.CTkFont(family="Arial", size=16, weight="bold"), text_color="#2c3e50").pack(anchor="w", padx=20, pady=(20, 0))

        self.fig2, self.ax2 = plt.subplots(figsize=(5, 4), dpi=100)
        self.fig2.patch.set_facecolor('#ffffff')
        self.fig2.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.05)
        self.ax2.set_facecolor('#ffffff')

        tour_ratio = self.db.get_tour_booking_ratio()
        if tour_ratio:
            pie_labels = [row[0] for row in tour_ratio]
            pie_sizes = [row[1] for row in tour_ratio]
            explode = [0.05 if i == 0 else 0 for i in range(len(pie_sizes))]
        else:
            pie_labels = ['Chưa có dữ liệu']
            pie_sizes = [100]
            explode = (0,)
            
        pie_colors = (['#3498db', '#2ecc71', '#e67e22', '#9b59b6', '#f1c40f', '#e74c3c'] * 5)[:len(pie_sizes)]

        wedges, texts, autotexts = self.ax2.pie(pie_sizes, explode=explode, labels=pie_labels, colors=pie_colors, autopct='%1.1f%%', shadow=False, startangle=140, textprops={'color': "#2c3e50", 'fontsize': 10}, wedgeprops={'edgecolor': 'white', 'linewidth': 1.5, 'antialiased': True})
        for autotext in autotexts: autotext.set_color('white'); autotext.set_weight('bold')

        self.canvas2 = FigureCanvasTkAgg(self.fig2, master=pie_chart_frame)
        self.canvas2.draw()
        self.canvas2.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=(10, 20))

        # --- Kích hoạt Animation ---
        self.ani = animation.FuncAnimation(self.fig1, self.animate_bars, frames=40, interval=25, repeat=False)

    def animate_bars(self, frame):
        # Thuật toán Ease-out (Làm cột chạy nhanh lúc đầu và chậm lại khi đến đích)
        progress = (frame + 1) / 40
        ease_out = 1 - (1 - progress) ** 3
        
        # Cập nhật chiều cao của từng cột theo frame hiện tại
        for bar, target in zip(self.bars, self.target_values):
            current_height = target * ease_out
            bar.set_height(current_height)
        
        return self.bars

    def destroy(self):
        # Dừng hiệu ứng chuyển động và xóa biểu đồ để tránh lỗi TclError khi chuyển trang
        if hasattr(self, 'ani') and getattr(self.ani, 'event_source', None):
            self.ani.event_source.stop()
        if hasattr(self, 'fig1'):
            plt.close(self.fig1)
        if hasattr(self, 'fig2'):
            plt.close(self.fig2)
        super().destroy()
