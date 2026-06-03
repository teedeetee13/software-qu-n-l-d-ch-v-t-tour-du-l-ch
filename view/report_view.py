import customtkinter as ctk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from db_manager import DBManager
import datetime

class ReportView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, corner_radius=0, fg_color="#f0f2f5")
        self.db = DBManager()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        self.create_header()
        self.create_filters()
        self.create_summary_cards()
        self.create_main_content()
        self.update_report()

    # ------------------------------------------------------------------ #
    #  Header
    # ------------------------------------------------------------------ #
    def create_header(self):
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=30, pady=(20, 10))

        ctk.CTkLabel(
            header_frame,
            text="Báo cáo & Thống kê hệ thống",
            font=ctk.CTkFont(family="Arial", size=26, weight="bold"),
            text_color="#2c3e50"
        ).pack(side="left")

    # ------------------------------------------------------------------ #
    #  Filters
    # ------------------------------------------------------------------ #
    def create_filters(self):
        filter_frame = ctk.CTkFrame(
            self, fg_color="#ffffff", corner_radius=12,
            border_width=1, border_color="#e0e0e0"
        )
        filter_frame.grid(row=1, column=0, sticky="ew", padx=30, pady=10)

        container = ctk.CTkFrame(filter_frame, fg_color="transparent")
        container.pack(padx=20, pady=15, fill="x")

        # --- Loại báo cáo ---
        group1 = ctk.CTkFrame(container, fg_color="transparent")
        group1.pack(side="left", padx=(0, 20))
        ctk.CTkLabel(group1, text="Loại báo cáo",
                     font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w")
        self.combo_type = ctk.CTkComboBox(
            group1,
            values=["Doanh thu theo năm", "Doanh thu theo tháng", "Doanh thu theo Tour"],
            width=210,
            command=self.on_type_change
        )
        self.combo_type.set("Doanh thu theo tháng")
        self.combo_type.pack(pady=(5, 0))

        # --- Năm ---
        group2 = ctk.CTkFrame(container, fg_color="transparent")
        group2.pack(side="left", padx=20)
        ctk.CTkLabel(group2, text="Năm",
                     font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w")
        current_year = datetime.datetime.now().year
        # Chỉ liệt kê từ 5 năm trước đến năm hiện tại (không liệt kê năm tương lai)
        years = [f"Năm {y}" for y in range(current_year - 5, current_year + 1)]
        self.combo_year = ctk.CTkComboBox(
            group2, values=years, width=120,
            command=lambda _: self.update_report()
        )
        self.combo_year.set(f"Năm {current_year}")
        self.combo_year.pack(pady=(5, 0))

        # --- Tháng ---
        group3 = ctk.CTkFrame(container, fg_color="transparent")
        group3.pack(side="left", padx=20)
        ctk.CTkLabel(group3, text="Tháng",
                     font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w")
        self.months_all   = ["Cả năm"] + [f"Tháng {i}" for i in range(1, 13)]
        self.combo_month = ctk.CTkComboBox(
            group3, values=self.months_all, width=120,
            command=lambda _: self.update_report()
        )
        self.combo_month.set("Cả năm")
        # Mặc định ban đầu: loại "Doanh thu theo tháng" → cho chọn tháng
        self.combo_month.configure(state="normal")
        self.combo_month.pack(pady=(5, 0))

        # --- Nút cập nhật ---
        self.btn_refresh = ctk.CTkButton(
            container, text="Cập nhật dữ liệu",
            fg_color="#27ae60", hover_color="#219150",
            width=140, height=35,
            font=ctk.CTkFont(weight="bold"),
            command=self.update_report
        )
        self.btn_refresh.pack(side="right", pady=(15, 0))

    # ------------------------------------------------------------------ #
    #  Summary cards
    # ------------------------------------------------------------------ #
    def create_summary_cards(self):
        self.cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.cards_frame.grid(row=2, column=0, sticky="ew", padx=30, pady=10)
        self.cards_frame.grid_columnconfigure((0, 1, 2), weight=1, pad=20)

        self.card_revenue  = self._draw_card(0, "TỔNG DOANH THU",       "0 VNĐ", "#3498db")
        self.card_bookings = self._draw_card(1, "SỐ ĐƠN ĐẶT CHỖ",       "0",     "#e67e22")
        self.card_growth   = self._draw_card(2, "TOUR BÁN CHẠY NHẤT",   "-",     "#2ecc71")

    def _draw_card(self, col, title, value, accent_color):
        card = ctk.CTkFrame(
            self.cards_frame, fg_color="#ffffff", corner_radius=12,
            border_width=1, border_color="#e0e0e0", height=100
        )
        card.grid(row=0, column=col, sticky="nsew")
        card.grid_propagate(False)

        accent = ctk.CTkFrame(card, width=5, fg_color=accent_color, corner_radius=0)
        accent.pack(side="left", fill="y")

        ctk.CTkLabel(card, text=title,
                     font=ctk.CTkFont(size=11, weight="bold"),
                     text_color="#7f8c8d").pack(anchor="w", padx=15, pady=(15, 0))

        lbl_value = ctk.CTkLabel(card, text=value,
                                 font=ctk.CTkFont(size=20, weight="bold"),
                                 text_color="#2c3e50")
        lbl_value.pack(anchor="w", padx=15, pady=(5, 0))
        return lbl_value

    # ------------------------------------------------------------------ #
    #  Main content (chart + table)
    # ------------------------------------------------------------------ #
    def create_main_content(self):
        self.main_content = ctk.CTkFrame(self, fg_color="transparent")
        self.main_content.grid(row=3, column=0, sticky="nsew", padx=30, pady=(10, 30))
        self.main_content.grid_columnconfigure(0, weight=3)
        self.main_content.grid_columnconfigure(1, weight=2)
        self.main_content.grid_rowconfigure(0, weight=1)

        # Biểu đồ
        chart_box = ctk.CTkFrame(
            self.main_content, fg_color="#ffffff",
            corner_radius=12, border_width=1, border_color="#e0e0e0"
        )
        chart_box.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        ctk.CTkLabel(chart_box, text="Xu hướng tăng trưởng",
                     font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=20, pady=15)

        self.chart_container = ctk.CTkFrame(chart_box, fg_color="transparent")
        self.chart_container.pack(fill="both", expand=True, padx=10, pady=(0, 15))

        # Bảng dữ liệu
        table_box = ctk.CTkFrame(
            self.main_content, fg_color="#ffffff",
            corner_radius=12, border_width=1, border_color="#e0e0e0"
        )
        table_box.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        ctk.CTkLabel(table_box, text="Chi tiết dữ liệu",
                     font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=20, pady=15)

        self.tree = ttk.Treeview(table_box, show="headings", selectmode="browse")
        self.tree.pack(fill="both", expand=True, padx=15, pady=(0, 15))

    # ------------------------------------------------------------------ #
    #  Logic điều khiển bộ lọc
    # ------------------------------------------------------------------ #
    def on_type_change(self, report_type):
        if report_type == "Doanh thu theo năm":
            # Chọn năm để xem tổng quan 12 tháng; không cần chọn tháng
            self.combo_year.configure(state="normal")
            self.combo_month.set("Cả năm")
            self.combo_month.configure(state="disabled")

        elif report_type == "Doanh thu theo tháng":
            self.combo_year.configure(state="normal")
            self.combo_month.set("Cả năm")
            self.combo_month.configure(state="normal")

        else:  # Doanh thu theo Tour
            self.combo_year.configure(state="normal")
            self.combo_month.set("Cả năm")
            self.combo_month.configure(state="normal")

        self.update_report()

    # ------------------------------------------------------------------ #
    #  Cập nhật báo cáo
    # ------------------------------------------------------------------ #
    def update_report(self):
        report_type = self.combo_type.get()

        year_str  = self.combo_year.get()
        year_val  = int(year_str.replace("Năm ", "")) if year_str else datetime.datetime.now().year

        month_str = self.combo_month.get()
        month_val = None if month_str == "Cả năm" else int(month_str.replace("Tháng ", ""))

        # Xóa biểu đồ cũ
        for widget in self.chart_container.winfo_children():
            widget.destroy()

        # Xóa bảng cũ
        for row in self.tree.get_children():
            self.tree.delete(row)

        if report_type == "Doanh thu theo năm":
            # Hiển thị bar chart 12 tháng của năm được chọn
            data = self.db.get_report_summary(year_val)
            self._render_monthly(data, year_val, chart_type="Cột")

        elif report_type == "Doanh thu theo tháng":
            if month_val is None:
                # Hiển thị tất cả 12 tháng của năm được chọn
                data = self.db.get_report_summary(year_val)
                self._render_monthly(data, year_val)
            else:
                # Hiển thị chi tiết 1 tháng cụ thể (theo ngày trong tháng)
                data = self.db.get_daily_revenue_report(year_val, month_val)
                self._render_daily(data, year_val, month_val)

        else:  # Doanh thu theo Tour
            data = self.db.get_revenue_by_tour_report(year_val, month_val)
            self._render_tour_based(data)

    # ------------------------------------------------------------------ #
    #  Render: theo năm (tất cả các năm)
    # ------------------------------------------------------------------ #
    def _render_yearly(self, data):
        years    = sorted(data.keys())
        revenues = [data[y]['revenue'] for y in years]
        bookings = sum(data[y]['bookings'] for y in years)
        total_rev = sum(revenues)

        self.card_revenue.configure(text=f"{total_rev:,} VNĐ")
        self.card_bookings.configure(text=str(bookings))
        self.card_growth.configure(text="Tất cả các năm")

        self._plot_data(
            [str(y) for y in years],
            [r / 1_000_000 for r in revenues],
            "Cột", "Doanh thu (Triệu VNĐ)", "#3498db"
        )

        self._setup_tree(("Năm", "Doanh thu", "Đơn hàng"))
        for y in years:
            self.tree.insert("", "end", values=(
                f"Năm {y}",
                f"{data[y]['revenue']:,}",
                data[y]['bookings']
            ))

    # ------------------------------------------------------------------ #
    #  Render: theo tháng trong một năm
    # ------------------------------------------------------------------ #
    def _render_monthly(self, data, year, chart_type="Đường"):
        months    = [f"T{i}" for i in range(1, 13)]
        revenues  = [data[i]['revenue'] for i in range(1, 13)]
        total_rev = sum(revenues)
        total_bk  = sum(data[i]['bookings'] for i in range(1, 13))

        self.card_revenue.configure(text=f"{total_rev:,} VNĐ")
        self.card_bookings.configure(text=str(total_bk))

        all_tours = {}
        for i in range(1, 13):
            for t, count in data[i]['tours'].items():
                all_tours[t] = all_tours.get(t, 0) + count
        best_tour = max(all_tours, key=all_tours.get) if all_tours else "N/A"
        label = (best_tour[:20] + "...") if len(best_tour) > 20 else best_tour
        self.card_growth.configure(text=label)

        color = "#3498db" if chart_type == "Cột" else "#e67e22"
        self._plot_data(
            months, [r / 1_000_000 for r in revenues],
            chart_type, f"Doanh thu năm {year} (Triệu VNĐ)", color
        )

        self._setup_tree(("Tháng", "Doanh thu", "Đơn"))
        for i in range(1, 13):
            self.tree.insert("", "end", values=(
                f"Tháng {i}",
                f"{data[i]['revenue']:,}",
                data[i]['bookings']
            ))

    # ------------------------------------------------------------------ #
    #  Render: theo ngày trong một tháng cụ thể
    # ------------------------------------------------------------------ #
    def _render_daily(self, data, year, month):
        """Hiển thị doanh thu theo từng ngày trong tháng được chọn."""
        import calendar
        num_days  = calendar.monthrange(year, month)[1]
        days      = list(range(1, num_days + 1))
        revenues  = [data.get(d, {}).get('revenue', 0) for d in days]
        bookings  = [data.get(d, {}).get('bookings', 0) for d in days]
        total_rev = sum(revenues)
        total_bk  = sum(bookings)

        self.card_revenue.configure(text=f"{total_rev:,} VNĐ")
        self.card_bookings.configure(text=str(total_bk))

        all_tours = {}
        for d in days:
            for t, count in data.get(d, {}).get('tours', {}).items():
                all_tours[t] = all_tours.get(t, 0) + count
        best_tour = max(all_tours, key=all_tours.get) if all_tours else "N/A"
        label = (best_tour[:20] + "...") if len(best_tour) > 20 else best_tour
        self.card_growth.configure(text=label)

        x_labels = [str(d) for d in days]
        self._plot_data(
            x_labels, [r / 1_000_000 for r in revenues],
            "Đường", f"Doanh thu tháng {month}/{year} (Triệu VNĐ)", "#9b59b6"
        )

        self._setup_tree(("Ngày", "Doanh thu", "Đơn"))
        for d in days:
            rev = data.get(d, {}).get('revenue', 0)
            bk  = data.get(d, {}).get('bookings', 0)
            self.tree.insert("", "end", values=(
                f"Ngày {d}/{month}",
                f"{rev:,}",
                bk
            ))

    # ------------------------------------------------------------------ #
    #  Render: theo Tour
    # ------------------------------------------------------------------ #
    def _render_tour_based(self, data):
        tours     = sorted(data.keys(), key=lambda x: data[x]['revenue'], reverse=True)[:10]
        revenues  = [data[t]['revenue'] for t in tours]
        total_rev = sum(revenues)
        total_bk  = sum(data[t]['bookings'] for t in tours)

        self.card_revenue.configure(text=f"{total_rev:,} VNĐ")
        self.card_bookings.configure(text=str(total_bk))
        self.card_growth.configure(text="Top 10 Tour")

        short_names = [t[:12] + ".." for t in tours]
        self._plot_data(
            short_names, [r / 1_000_000 for r in revenues],
            "Cột Ngang", "Doanh thu (Triệu VNĐ)", "#2ecc71"
        )

        self._setup_tree(("Tên Tour", "Doanh thu", "Khách"))
        for t in tours:
            self.tree.insert("", "end", values=(
                t,
                f"{data[t]['revenue']:,}",
                data[t]['guests']
            ))

    # ------------------------------------------------------------------ #
    #  Vẽ biểu đồ
    # ------------------------------------------------------------------ #
    def _plot_data(self, labels, values, chart_type, ylabel, color):
        fig, ax = plt.subplots(figsize=(5, 3), dpi=100)
        fig.patch.set_facecolor('#ffffff')
        ax.set_facecolor('#ffffff')

        if chart_type == "Cột":
            ax.bar(labels, values, color=color, alpha=0.7)
        elif chart_type == "Cột Ngang":
            ax.barh(labels, values, color=color, alpha=0.7)
        else:  # Đường
            ax.plot(labels, values, marker='o', color=color,
                    linewidth=2, markerfacecolor='white')
            ax.fill_between(range(len(labels)), values, alpha=0.1, color=color)
            ax.set_xticks(range(len(labels)))
            ax.set_xticklabels(labels)

        ax.set_ylabel(ylabel, fontsize=9, color="#7f8c8d")
        ax.tick_params(axis='both', which='major', labelsize=8, labelcolor="#2c3e50")

        for spine in ax.spines.values():
            spine.set_visible(False)
        ax.yaxis.grid(True, linestyle='--', alpha=0.3)

        plt.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=self.chart_container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    # ------------------------------------------------------------------ #
    #  Tiện ích bảng
    # ------------------------------------------------------------------ #
    def _setup_tree(self, columns):
        width_map = {
            "Năm":       90,  "Tháng":     90,  "Ngày":      110,
            "Doanh thu": 155, "Đơn hàng":  80,  "Đơn":       55,
            "Khách":     65,  "Tên Tour":  185,
        }
        self.tree.configure(columns=columns)
        for col in columns:
            w = width_map.get(col, 80)
            anchor = "w" if col == "Tên Tour" else ("e" if col == "Doanh thu" else "center")
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w, anchor=anchor)