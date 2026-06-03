import customtkinter as ctk
from tkinter import ttk, messagebox
import calendar
import datetime
from db_manager import DBManager
import auth_session


# ─────────────────────────────────────────────────────────────
#  Widget chọn ngày dạng popup (mini calendar)
# ─────────────────────────────────────────────────────────────
class DatePickerWidget(ctk.CTkFrame):
    """Một hàng gồm Entry hiển thị ngày + nút lịch mở popup."""

    def __init__(self, parent, width=260, initial_date=None, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)

        self._date = initial_date or datetime.date.today()

        self._entry = ctk.CTkEntry(self, width=width - 50, height=34,
                                   fg_color="#f0f2f5", border_color="#e0e0e0",
                                   text_color="#2c3e50")
        self._entry.pack(side="left", padx=(0, 4))
        self._entry.insert(0, self._date.strftime("%Y-%m-%d"))

        ctk.CTkButton(self, text="📅", width=42, height=34,
                      fg_color="#3498db", hover_color="#2980b9",
                      command=self._open_popup).pack(side="left")

    # ── public API ──────────────────────────────────────────
    def get(self) -> str:
        return self._entry.get().strip()

    def set(self, date_str: str):
        try:
            self._date = datetime.date.fromisoformat(str(date_str))
        except (ValueError, TypeError):
            self._date = datetime.date.today()
        self._entry.delete(0, "end")
        self._entry.insert(0, self._date.strftime("%Y-%m-%d"))

    # ── popup calendar ───────────────────────────────────────
    def _open_popup(self):
        popup = ctk.CTkToplevel(self)
        popup.title("Chọn ngày")
        popup.resizable(False, False)
        popup.grab_set()

        self.update_idletasks()
        x = self.winfo_rootx()
        y = self.winfo_rooty() + self.winfo_height() + 4
        popup.geometry(f"+{x}+{y}")

        state = {"year": self._date.year, "month": self._date.month}

        header = ctk.CTkFrame(popup, fg_color="transparent")
        header.pack(fill="x", padx=10, pady=(10, 0))

        lbl_month = ctk.CTkLabel(header, text="",
                                 font=ctk.CTkFont(weight="bold", size=14),
                                 text_color="#2c3e50", width=180)
        lbl_month.pack(side="left", expand=True)

        grid_frame = ctk.CTkFrame(popup, fg_color="transparent")
        grid_frame.pack(padx=10, pady=8)

        def render():
            for w in grid_frame.winfo_children():
                w.destroy()
            y2, m2 = state["year"], state["month"]
            lbl_month.configure(text=f"Tháng {m2:02d} / {y2}")

            for col, dn in enumerate(["T2", "T3", "T4", "T5", "T6", "T7", "CN"]):
                ctk.CTkLabel(grid_frame, text=dn, width=36, height=28,
                             font=ctk.CTkFont(size=11, weight="bold"),
                             text_color="#7f8c8d").grid(row=0, column=col, padx=1, pady=1)

            first_wd = calendar.monthrange(y2, m2)[0]
            num_days = calendar.monthrange(y2, m2)[1]

            for d in range(1, num_days + 1):
                col = (first_wd + d - 1) % 7
                row = (first_wd + d - 1) // 7 + 1
                is_sel = (d == self._date.day
                          and m2 == self._date.month
                          and y2 == self._date.year)
                btn = ctk.CTkButton(
                    grid_frame, text=str(d), width=36, height=32,
                    fg_color="#3498db" if is_sel else "transparent",
                    text_color="white" if is_sel else "#2c3e50",
                    hover_color="#2980b9",
                    font=ctk.CTkFont(size=12),
                    command=lambda _d=d: pick(_d)
                )
                btn.grid(row=row, column=col, padx=1, pady=1)

        def pick(d):
            self._date = datetime.date(state["year"], state["month"], d)
            self._entry.delete(0, "end")
            self._entry.insert(0, self._date.strftime("%Y-%m-%d"))
            popup.destroy()

        def prev_month():
            if state["month"] == 1:
                state["month"] = 12; state["year"] -= 1
            else:
                state["month"] -= 1
            render()

        def next_month():
            if state["month"] == 12:
                state["month"] = 1; state["year"] += 1
            else:
                state["month"] += 1
            render()

        ctk.CTkButton(header, text="◀", width=30, height=28,
                      fg_color="transparent", text_color="#2c3e50",
                      hover_color="#e0e0e0", command=prev_month).pack(side="left")
        ctk.CTkButton(header, text="▶", width=30, height=28,
                      fg_color="transparent", text_color="#2c3e50",
                      hover_color="#e0e0e0", command=next_month).pack(side="right")

        render()


# ─────────────────────────────────────────────────────────────
#  ScheduleView
# ─────────────────────────────────────────────────────────────
class ScheduleView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, corner_radius=0, fg_color="#f0f2f5")
        self.db = DBManager()
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.create_header()
        self.create_toolbar()
        self.create_table()
        self.load_data()

    # ── Header ───────────────────────────────────────────────
    def create_header(self):
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))

        ctk.CTkLabel(header_frame, text="Quản lý Lịch Khởi Hành",
                     font=ctk.CTkFont(family="Arial", size=28, weight="bold"),
                     text_color="#2c3e50").pack(side="left")

        if auth_session.current_role == "Admin":
            ctk.CTkButton(header_frame, text="+ Thêm Lịch Khởi Hành",
                          font=ctk.CTkFont(family="Arial", size=14, weight="bold"),
                          fg_color="#3498db", hover_color="#2980b9",
                          height=40, width=200, corner_radius=5,
                          command=self.add_schedule).pack(side="right")

    # ── Toolbar ──────────────────────────────────────────────
    def create_toolbar(self):
        toolbar = ctk.CTkFrame(self, fg_color="#ffffff", corner_radius=8,
                               border_width=1, border_color="#e0e0e0", height=60)
        toolbar.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        toolbar.grid_propagate(False)

        self.entry_search = ctk.CTkEntry(
            toolbar, placeholder_text="Tìm theo mã, tên tour...",
            width=300, height=30, corner_radius=5,
            fg_color="#f0f2f5", border_color="#e0e0e0", text_color="#2c3e50")
        self.entry_search.pack(side="left", padx=(20, 10), pady=15)

        ctk.CTkButton(toolbar, text="Tìm kiếm", width=80, height=30,
                      corner_radius=5, fg_color="#2ecc71", hover_color="#27ae60",
                      font=ctk.CTkFont(family="Arial", size=14),
                      command=self.load_data).pack(side="left", padx=10, pady=15)

        if auth_session.current_role == "Admin":
            ctk.CTkButton(toolbar, text="Xóa", fg_color="#e74c3c",
                          hover_color="#c0392b", width=80, height=30,
                          corner_radius=5,
                          command=self.delete_schedule).pack(side="right", padx=(5, 20), pady=15)
            ctk.CTkButton(toolbar, text="Sửa", fg_color="#f39c12",
                          hover_color="#d35400", width=80, height=30,
                          corner_radius=5,
                          command=self.edit_schedule).pack(side="right", padx=5, pady=15)

    # ── Table ────────────────────────────────────────────────
    def create_table(self):
        table_bg = ctk.CTkFrame(self, fg_color="#ffffff", corner_radius=8,
                                border_width=1, border_color="#e0e0e0")
        table_bg.grid(row=2, column=0, sticky="nsew")
        table_bg.grid_rowconfigure(0, weight=1)
        table_bg.grid_columnconfigure(0, weight=1)

        columns = ("ID Lịch", "Tên Tour", "Ngày Đi", "Ngày Về",
                   "Giá NL (VNĐ)", "Hướng dẫn viên", "Chỗ đã đặt / Tổng", "Trạng Thái")
        self.tree = ttk.Treeview(table_bg, columns=columns,
                                 show="headings", height=15)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center")
        self.tree.column("Tên Tour", width=220, anchor="w")
        self.tree.column("Giá NL (VNĐ)", anchor="e", width=135)
        self.tree.column("Hướng dẫn viên", width=155, anchor="w")
        self.tree.column("Chỗ đã đặt / Tổng", width=130)
        self.tree.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)

        self.tree.tag_configure('oddrow',  background="#ffffff")
        self.tree.tag_configure('evenrow', background="#f8f9fa")
        self.tree.tag_configure('Còn chỗ',       foreground="#27ae60")
        self.tree.tag_configure('Hết chỗ',       foreground="#e74c3c")
        self.tree.tag_configure('Sắp khởi hành', foreground="#f39c12")
        self.tree.tag_configure('Đã kết thúc',   foreground="#95a5a6")
        self.tree.tag_configure('Đã hủy',        foreground="#c0392b")

    # ── Load ─────────────────────────────────────────────────
    def load_data(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        search_kw = self.entry_search.get()
        rows = self.db.get_all_schedules(search_kw)
        for i, row in enumerate(rows):
            # (id, tour_id, t.name, dep, ret, price, max_slots, booked, status, guide_name)
            price_display = f"{row[5]:,.0f}" if row[5] is not None else "Chưa set"
            status  = row[8]
            guide   = row[9] or ""
            booked  = row[7]
            max_sl  = row[6]
            slots_display = f"{booked} / {max_sl}"
            display_row = (row[0], row[2], row[3], row[4],
                           price_display, guide, slots_display, status)
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            self.tree.insert("", "end", values=display_row,
                             iid=row[0], tags=(tag, status))

    # ── Actions ──────────────────────────────────────────────
    def add_schedule(self):
        self.open_form()

    def edit_schedule(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Lỗi", "Chọn Lịch trình để sửa!")
            return
        s_id = selected[0]
        schedule_data = next(
            (r for r in self.db.get_all_schedules() if r[0] == s_id), None)
        if schedule_data:
            price_data = self.db.get_prices_for_schedule(s_id)
            self.open_form(schedule_data, price_data)

    def delete_schedule(self):
        if auth_session.current_role != "Admin":
            messagebox.showwarning("Từ chối", "Chỉ Admin được Xóa!")
            return
        selected = self.tree.selection()
        if not selected:
            return
        s_id = selected[0]
        if messagebox.askyesno("Xác nhận", "Xóa Lịch trình này?"):
            self.db.delete_schedule(s_id)
            self.load_data()

    # ── Form ─────────────────────────────────────────────────
    def open_form(self, data=None, prices=None):
        if auth_session.current_role != "Admin":
            messagebox.showwarning("Từ chối", "Chỉ Admin được Thêm/Sửa!")
            return

        top = ctk.CTkToplevel(self)
        top.title("Thông tin Lịch Khởi Hành")
        top.geometry("480x580")
        top.resizable(False, False)
        top.grab_set()

        scroll = ctk.CTkScrollableFrame(top, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=16, pady=12)

        def lbl(text):
            ctk.CTkLabel(scroll, text=text, anchor="w",
                         text_color="#34495e",
                         font=ctk.CTkFont(size=13)).pack(anchor="w", pady=(8, 1))

        # Mã lịch trình
        lbl("Mã Lịch trình:")
        entry_id = ctk.CTkEntry(scroll, width=430, height=34,
                                fg_color="#f0f2f5", border_color="#e0e0e0",
                                text_color="#2c3e50")
        entry_id.pack(anchor="w")

        # Tour gốc
        lbl("Tour gốc:")
        tours_data = self.db.get_all_tours()
        tour_map = {f"{t[1]} (ID: {t[0]})": t[0] for t in tours_data}
        cb_tour = ctk.CTkComboBox(scroll, values=list(tour_map.keys()),
                                  width=430, height=34,
                                  fg_color="#f0f2f5", border_color="#e0e0e0",
                                  button_color="#bdc3c7", text_color="#2c3e50")
        cb_tour.pack(anchor="w")

        # Ngày khởi hành
        lbl("Ngày khởi hành:")
        dp_dep = DatePickerWidget(scroll, width=430)
        dp_dep.pack(anchor="w")

        # Ngày về
        lbl("Ngày về:")
        tomorrow = datetime.date.today() + datetime.timedelta(days=1)
        dp_ret = DatePickerWidget(scroll, width=430,
                                  initial_date=tomorrow)
        dp_ret.pack(anchor="w")

        # Số chỗ đã đặt
        lbl("Số chỗ đã đặt:")
        entry_booked = ctk.CTkEntry(scroll, width=430, height=34,
                                    fg_color="#f0f2f5", border_color="#e0e0e0",
                                    text_color="#2c3e50")
        entry_booked.pack(anchor="w")

        # Hướng dẫn viên phụ trách
        lbl("Hướng dẫn viên phụ trách:")
        guide_names = self.db.get_all_guides_for_form()
        cb_guide = ctk.CTkComboBox(scroll, values=guide_names,
                                   width=430, height=34,
                                   fg_color="#f0f2f5", border_color="#e0e0e0",
                                   button_color="#bdc3c7", text_color="#2c3e50")
        cb_guide.set("-- Chọn hướng dẫn viên --")
        cb_guide.pack(anchor="w")

        # ── Chính sách giá (chỉ Người lớn + Trẻ em) ──
        ctk.CTkLabel(scroll, text="Chính sách giá (VNĐ)",
                     font=ctk.CTkFont(weight="bold", size=13),
                     text_color="#2c3e50").pack(anchor="w", pady=(14, 2))

        price_entries = {}
        for p_type, placeholder in [
            ("Người lớn", "Bắt buộc"),
            ("Trẻ em",    "Bỏ trống nếu không áp dụng"),
        ]:
            lbl(f"Giá {p_type}:")
            ent = ctk.CTkEntry(scroll, width=430, height=34,
                               placeholder_text=placeholder,
                               fg_color="#f0f2f5", border_color="#e0e0e0",
                               text_color="#2c3e50")
            ent.pack(anchor="w")
            price_entries[p_type] = ent

        # Ghi chú trạng thái
        ctk.CTkLabel(scroll,
                     text="ℹ  Trạng thái được tính tự động theo ngày khởi hành",
                     text_color="#95a5a6",
                     font=ctk.CTkFont(size=11, slant="italic")).pack(
            anchor="w", pady=(10, 0))

        # ── Điền dữ liệu khi SỬA ──
        if data:
            entry_id.insert(0, data[0])
            entry_id.configure(state="disabled")
            cb_tour.set(f"{data[2]} (ID: {data[1]})")
            dp_dep.set(data[3] or "")
            dp_ret.set(data[4] or "")
            entry_booked.insert(0, str(data[7]))
            if data[9]:
                cb_guide.set(data[9])
            if prices:
                for p_type in ("Người lớn", "Trẻ em"):
                    val = prices.get(p_type, "")
                    if val:
                        price_entries[p_type].insert(0, str(val))
        else:
            entry_id.insert(0, self.db.next_id("Schedules", "id", "SCH"))
            entry_id.configure(state="disabled")
            entry_booked.insert(0, "0")

        # ── Lưu ──
        def save():
            s_id      = entry_id.get()
            dep_date  = dp_dep.get()
            ret_date  = dp_ret.get()
            booked    = entry_booked.get()
            tour_id   = tour_map.get(cb_tour.get())
            guide_name = cb_guide.get().strip()
            if guide_name == "-- Chọn hướng dẫn viên --":
                guide_name = ""

            if not all([s_id, dep_date, booked]) or not tour_id:
                messagebox.showwarning("Lỗi", "Nhập đủ thông tin và chọn Tour!")
                return

            try:
                dep_d = datetime.date.fromisoformat(dep_date)
                ret_d = datetime.date.fromisoformat(ret_date) if ret_date else None
                if ret_d and ret_d < dep_d:
                    messagebox.showwarning("Lỗi",
                        "Ngày về không thể trước ngày khởi hành!")
                    return
            except ValueError:
                messagebox.showerror("Lỗi", "Ngày không hợp lệ (YYYY-MM-DD)!")
                return

            try:
                booked_int = int(booked)
            except ValueError:
                messagebox.showerror("Lỗi", "Số chỗ phải là số nguyên!")
                return

            try:
                prices_dict = {}
                for p_type, ent in price_entries.items():
                    val_str = ent.get().strip().replace(",", "")
                    if val_str:
                        prices_dict[p_type] = int(val_str)
                if not prices_dict.get("Người lớn"):
                    messagebox.showwarning("Bắt buộc",
                        "Giá Người lớn không được để trống!")
                    return
            except ValueError:
                messagebox.showerror("Lỗi", "Giá phải là số nguyên!")
                return

            if data:
                self.db.update_schedule(
                    s_id, tour_id, dep_date,
                    ret_date or None, booked_int, prices_dict, guide_name)
            else:
                success, msg = self.db.add_schedule(
                    s_id, tour_id, dep_date,
                    ret_date or None, booked_int, prices_dict, guide_name)
                if not success:
                    messagebox.showerror("Lỗi", msg)
                    return

            top.destroy()
            self.load_data()

        ctk.CTkButton(scroll, text="💾  LƯU LỊCH TRÌNH", height=44,
                      fg_color="#3498db", hover_color="#2980b9",
                      font=ctk.CTkFont(family="Arial", size=15, weight="bold"),
                      command=save).pack(pady=(20, 8), fill="x")