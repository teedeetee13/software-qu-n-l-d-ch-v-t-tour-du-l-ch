import customtkinter as ctk
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.animation as animation
from db_manager import DBManager
import datetime

# Bảng màu hiện đại, tương phản tốt
CHART_COLORS = ['#3498db', '#2ecc71', '#e67e22', '#9b59b6', '#e74c3c', '#1abc9c', '#f39c12']
COLOR_OTHER  = '#bdc3c7'   # Màu cho nhóm "Khác"

class DashboardView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, corner_radius=0, fg_color="#f0f2f5")
        self.db = DBManager()
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.create_header()
        self.create_summary_cards()
        self.create_charts_section()

    # ------------------------------------------------------------------ #
    def create_header(self):
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        ctk.CTkLabel(
            header_frame,
            text="Tổng quan Thống kê",
            font=ctk.CTkFont(family="Arial", size=28, weight="bold"),
            text_color="#2c3e50"
        ).pack(side="left")

    # ------------------------------------------------------------------ #
    def create_summary_cards(self):
        cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        cards_frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        cards_frame.grid_columnconfigure((0, 1, 2), weight=1)

        def create_card(parent, title, value, color, col):
            card = ctk.CTkFrame(
                parent, fg_color="#ffffff", corner_radius=8,
                border_width=1, border_color="#e0e0e0", height=100
            )
            card.grid(row=0, column=col, sticky="ew",
                      padx=(0 if col == 0 else 10, 0 if col == 2 else 10))
            card.grid_propagate(False)
            ctk.CTkLabel(card, text=title,
                         font=ctk.CTkFont(family="Arial", size=14),
                         text_color="#7f8c8d").pack(anchor="w", padx=20, pady=(15, 5))
            ctk.CTkLabel(card, text=value,
                         font=ctk.CTkFont(family="Arial", size=26, weight="bold"),
                         text_color=color).pack(anchor="w", padx=20)

        revenue, bookings, customers, tours = self.db.get_dashboard_stats()
        create_card(cards_frame, "Tổng Doanh Thu", f"{revenue:,} ₫", "#2ecc71", 0)
        create_card(cards_frame, "Tour Đang Chạy", f"{tours} Tour",  "#3498db", 1)
        create_card(cards_frame, "Khách Hàng",     f"{customers} Khách", "#9b59b6", 2)

    # ------------------------------------------------------------------ #
    def create_charts_section(self):
        charts_container = ctk.CTkFrame(self, fg_color="transparent")
        charts_container.grid(row=2, column=0, sticky="nsew")
        charts_container.grid_columnconfigure((0, 1), weight=1, uniform="chart_group")
        charts_container.grid_rowconfigure(0, weight=1)

        self._build_bar_chart(charts_container)
        self._build_donut_chart(charts_container)

        # Kích hoạt animation cho biểu đồ cột
        self.ani = animation.FuncAnimation(
            self.fig1, self.animate_bars,
            frames=40, interval=25, repeat=False
        )

    # ------------------------------------------------------------------ #
    #  BIỂU ĐỒ CỘT — Doanh thu 6 tháng gần nhất
    # ------------------------------------------------------------------ #
    def _build_bar_chart(self, parent):
        frame = ctk.CTkFrame(
            parent, fg_color="#ffffff", corner_radius=8,
            border_width=1, border_color="#e0e0e0"
        )
        frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        ctk.CTkLabel(
            frame, text="Doanh thu (6 tháng gần nhất)",
            font=ctk.CTkFont(family="Arial", size=16, weight="bold"),
            text_color="#2c3e50"
        ).pack(anchor="w", padx=20, pady=(20, 0))

        self.fig1, self.ax1 = plt.subplots(figsize=(5, 4), dpi=100)
        self.fig1.patch.set_facecolor('#ffffff')
        self.fig1.subplots_adjust(left=0.15, right=0.95, top=0.9, bottom=0.15)
        self.ax1.set_facecolor('#ffffff')

        current_month = datetime.datetime.now().month
        rev_data = self.db.get_monthly_revenue()

        self.months        = []
        self.target_values = []
        for i in range(5, -1, -1):
            m = current_month - i
            if m <= 0:
                m += 12
            self.months.append(f"T{m}")
            self.target_values.append(rev_data.get(m, 0) / 1_000_000)

        self.current_values = [0] * len(self.months)
        self.bars = self.ax1.bar(
            self.months, self.current_values,
            color='#3498db', width=0.55,
            edgecolor='none', alpha=0.85, zorder=3
        )
        max_target = max(self.target_values) if max(self.target_values, default=0) > 0 else 100
        self.ax1.set_ylim(0, max_target * 1.2)
        self.ax1.set_ylabel("Triệu VNĐ", color="#7f8c8d", fontsize=10)
        self.ax1.tick_params(colors='#34495e', labelsize=9)
        self.ax1.spines['top'].set_visible(False)
        self.ax1.spines['right'].set_visible(False)
        self.ax1.spines['left'].set_color('#e0e0e0')
        self.ax1.spines['bottom'].set_color('#e0e0e0')
        self.ax1.yaxis.grid(True, linestyle='--', alpha=0.5, color='#bdc3c7', zorder=0)

        self.canvas1 = FigureCanvasTkAgg(self.fig1, master=frame)
        self.canvas1.draw()
        self.canvas1.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=(10, 20))

    # ------------------------------------------------------------------ #
    #  DONUT CHART — Tỷ lệ đặt chỗ theo Tour  (cải tiến)
    # ------------------------------------------------------------------ #
    def _build_donut_chart(self, parent):
        frame = ctk.CTkFrame(
            parent, fg_color="#ffffff", corner_radius=8,
            border_width=1, border_color="#e0e0e0"
        )
        frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        ctk.CTkLabel(
            frame, text="Tỷ lệ Đặt chỗ theo Tour",
            font=ctk.CTkFont(family="Arial", size=16, weight="bold"),
            text_color="#2c3e50"
        ).pack(anchor="w", padx=20, pady=(20, 0))

        # ----- Xử lý dữ liệu: chỉ lấy Top 6, phần còn lại → "Khác" -----
        raw = self.db.get_tour_booking_ratio()   # [(tên, số lượng), ...]

        if raw:
            raw_sorted = sorted(raw, key=lambda x: x[1], reverse=True)
            TOP_N      = 6
            top_items  = raw_sorted[:TOP_N]
            other_sum  = sum(r[1] for r in raw_sorted[TOP_N:])

            labels = [r[0] for r in top_items]
            sizes  = [r[1] for r in top_items]
            colors = CHART_COLORS[:len(top_items)]

            if other_sum > 0:
                labels.append(f"Khác ({len(raw_sorted) - TOP_N} tour)")
                sizes.append(other_sum)
                colors.append(COLOR_OTHER)
        else:
            labels = ['Chưa có dữ liệu']
            sizes  = [100]
            colors = [COLOR_OTHER]

        # ----- Vẽ Donut chart -----
        self.fig2, self.ax2 = plt.subplots(figsize=(5, 4), dpi=100)
        self.fig2.patch.set_facecolor('#ffffff')
        # Dành vùng bên phải cho legend
        self.fig2.subplots_adjust(left=0.0, right=0.55, top=0.95, bottom=0.05)
        self.ax2.set_facecolor('#ffffff')

        total = sum(sizes)
        wedge_props = {
            'linewidth' : 2,
            'edgecolor' : '#ffffff',
            'antialiased': True,
        }
        wedges, texts, autotexts = self.ax2.pie(
            sizes,
            labels      = None,          # Tắt label trên biểu đồ
            colors      = colors,
            autopct     = lambda pct: f'{pct:.1f}%' if pct >= 5 else '',
            startangle  = 90,
            counterclock= False,
            wedgeprops  = wedge_props,
            pctdistance = 0.78,
            shadow      = False,
        )

        for at in autotexts:
            at.set_color('white')
            at.set_fontsize(9)
            at.set_fontweight('bold')

        # Khoét lỗ giữa → Donut
        centre_circle = plt.Circle((0, 0), 0.52, fc='white')
        self.ax2.add_patch(centre_circle)

        # Số tổng ở giữa donut
        self.ax2.text(
            0, 0, f'{total}\nđơn',
            ha='center', va='center',
            fontsize=13, fontweight='bold',
            color='#2c3e50'
        )

        # ----- Legend bên phải, gọn gàng -----
        # Rút ngắn tên tour cho legend
        short_labels = []
        for lb in labels:
            short_labels.append(lb if len(lb) <= 22 else lb[:20] + '…')

        legend_patches = [
            mpatches.Patch(color=colors[i], label=short_labels[i])
            for i in range(len(labels))
        ]
        legend = self.fig2.legend(
            handles    = legend_patches,
            loc        = 'center right',
            bbox_to_anchor = (1.0, 0.5),
            fontsize   = 8,
            frameon    = False,
            handlelength = 1.2,
            handleheight = 1.2,
            borderpad  = 0.5,
            labelspacing = 0.7,
        )
        for text in legend.get_texts():
            text.set_color('#2c3e50')

        # ----- Tooltip khi hover -----
        self._annot = self.ax2.annotate(
            '', xy=(0, 0),
            xytext=(20, 20), textcoords='offset points',
            bbox=dict(boxstyle='round,pad=0.4', fc='#2c3e50', alpha=0.85),
            arrowprops=dict(arrowstyle='->', color='#2c3e50'),
            fontsize=9, color='white',
            visible=False
        )
        self._wedges      = wedges
        self._pie_labels  = labels
        self._pie_sizes   = sizes
        self._pie_total   = total

        self.canvas2 = FigureCanvasTkAgg(self.fig2, master=frame)
        self.canvas2.draw()
        self.canvas2.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=(10, 20))

        # Kết nối sự kiện hover
        self.canvas2.mpl_connect('motion_notify_event', self._on_hover)

    # ------------------------------------------------------------------ #
    #  Hover tooltip cho donut
    # ------------------------------------------------------------------ #
    def _on_hover(self, event):
        if event.inaxes != self.ax2:
            self._annot.set_visible(False)
            self.canvas2.draw_idle()
            return

        hit_any = False
        for i, wedge in enumerate(self._wedges):
            cont, _ = wedge.contains(event)
            if cont:
                count = self._pie_sizes[i]
                pct   = count / self._pie_total * 100
                name  = self._pie_labels[i]
                # Rút ngắn tên nếu quá dài
                display = name if len(name) <= 28 else name[:26] + '…'
                self._annot.set_text(f'{display}\n{count} đơn  ({pct:.1f}%)')
                self._annot.xy = (event.xdata, event.ydata)
                self._annot.set_visible(True)
                # Làm nổi bật miếng được hover
                for j, w in enumerate(self._wedges):
                    w.set_alpha(1.0 if j == i else 0.55)
                hit_any = True
                break

        if not hit_any:
            self._annot.set_visible(False)
            for w in self._wedges:
                w.set_alpha(1.0)

        self.canvas2.draw_idle()

    # ------------------------------------------------------------------ #
    #  Animation biểu đồ cột
    # ------------------------------------------------------------------ #
    def animate_bars(self, frame):
        progress = (frame + 1) / 40
        ease_out = 1 - (1 - progress) ** 3
        for bar, target in zip(self.bars, self.target_values):
            bar.set_height(target * ease_out)
        return self.bars

    # ------------------------------------------------------------------ #
    #  Dọn dẹp khi chuyển trang
    # ------------------------------------------------------------------ #
    def destroy(self):
        if hasattr(self, 'ani') and getattr(self.ani, 'event_source', None):
            self.ani.event_source.stop()
        if hasattr(self, 'fig1'):
            plt.close(self.fig1)
        if hasattr(self, 'fig2'):
            plt.close(self.fig2)
        super().destroy()