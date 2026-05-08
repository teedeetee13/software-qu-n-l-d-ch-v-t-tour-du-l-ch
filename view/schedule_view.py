import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
from db_manager import DBManager
import auth_session

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

    def create_header(self):
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        
        lbl = ctk.CTkLabel(header_frame, text="Quản lý Lịch Khởi Hành", font=ctk.CTkFont(family="Arial", size=28, weight="bold"), text_color="#2c3e50")
        lbl.pack(side="left")

        if auth_session.current_role == "Admin":
            ctk.CTkButton(header_frame, text="+ Thêm Lịch Khởi Hành", font=ctk.CTkFont(family="Arial", size=14, weight="bold"), fg_color="#3498db", hover_color="#2980b9", height=40, width=180, corner_radius=5, command=self.add_schedule).pack(side="right")
 
    def create_toolbar(self):
        toolbar = ctk.CTkFrame(self, fg_color="#ffffff", corner_radius=8, border_width=1, border_color="#e0e0e0", height=60)
        toolbar.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        toolbar.grid_propagate(False)

        self.entry_search = ctk.CTkEntry(toolbar, placeholder_text="Tìm theo mã, tên tour...", width=300, height=30, corner_radius=5, fg_color="#f0f2f5", border_color="#e0e0e0", text_color="#2c3e50")
        self.entry_search.pack(side="left", padx=(20, 10), pady=15)
        
        ctk.CTkButton(toolbar, text="Tìm kiếm", width=80, height=30, corner_radius=5, fg_color="#2ecc71", hover_color="#27ae60", font=ctk.CTkFont(family="Arial", size=14), command=self.load_data).pack(side="left", padx=10, pady=15)

        if auth_session.current_role == "Admin":
            ctk.CTkButton(toolbar, text="Xóa", fg_color="#e74c3c", hover_color="#c0392b", width=80, height=30, corner_radius=5, command=self.delete_schedule).pack(side="right", padx=(5, 20), pady=15)
            ctk.CTkButton(toolbar, text="Sửa", fg_color="#f39c12", hover_color="#d35400", width=80, height=30, corner_radius=5, command=self.edit_schedule).pack(side="right", padx=5, pady=15)
 
    def create_table(self):
        table_bg = ctk.CTkFrame(self, fg_color="#ffffff", corner_radius=8, border_width=1, border_color="#e0e0e0")
        table_bg.grid(row=2, column=0, sticky="nsew")
        table_bg.grid_rowconfigure(0, weight=1)
        table_bg.grid_columnconfigure(0, weight=1)

        columns = ("ID Lịch", "Tên Tour", "Ngày Đi", "Ngày Về", "Giá Người Lớn (VNĐ)", "Tối đa", "Đã đặt", "Trạng Thái")
        self.tree = ttk.Treeview(table_bg, columns=columns, show="headings", height=15)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center")
        self.tree.column("Tên Tour", width=250, anchor="w")
        self.tree.column("Giá Người Lớn (VNĐ)", anchor="e", width=150)

        self.tree.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)
        
        self.tree.tag_configure('oddrow', background="#ffffff")
        self.tree.tag_configure('evenrow', background="#f8f9fa")
        self.tree.tag_configure('Còn chỗ',       foreground="#27ae60")
        self.tree.tag_configure('Sắp khởi hành', foreground="#e67e22")
        self.tree.tag_configure('Hết chỗ',        foreground="#e74c3c")
        self.tree.tag_configure('Đã kết thúc',    foreground="#95a5a6")

    def load_data(self):
        for row in self.tree.get_children(): self.tree.delete(row)
        search_kw = self.entry_search.get()
        
        rows = self.db.get_all_schedules(search_kw)
        for i, row in enumerate(rows):
            # row = (s.id, s.tour_id, t.name, s.departure_date, s.return_date, s.price, s.max_slots, s.booked_slots, s.status)
            # Hiển thị: (s.id, t.name, s.departure_date, s.return_date, adult_price, s.max_slots, s.booked_slots, s.status)
            price_display = f"{row[5]:,.0f}" if row[5] is not None else "Chưa set"
            display_row = (row[0], row[2], row[3], row[4], price_display, row[6], row[7], row[8])
            row_tag    = 'evenrow' if i % 2 == 0 else 'oddrow'
            status_tag = row[8]
            self.tree.insert("", "end", values=display_row, iid=row[0], tags=(row_tag, status_tag))

    def add_schedule(self):
        self.open_form()

    def edit_schedule(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Lỗi", "Chọn Lịch trình để sửa!")
            return
        
        s_id = selected[0]
        # Lấy dữ liệu gốc từ DB để sửa cho chính xác
        schedule_data = next((row for row in self.db.get_all_schedules() if row[0] == s_id), None)
        if schedule_data:
            price_data = self.db.get_prices_for_schedule(s_id)
            self.open_form(schedule_data, price_data)

    def delete_schedule(self):
        if auth_session.current_role != "Admin":
            messagebox.showwarning("Từ chối", "Chỉ Admin được Xóa!")
            return
        selected = self.tree.selection()
        if not selected: return
        s_id = self.tree.item(selected[0])['values'][0]
        if messagebox.askyesno("Xác nhận", "Xóa Lịch trình này?"):
            self.db.delete_schedule(s_id)
            self.load_data()

    def open_form(self, data=None, prices=None):
        if auth_session.current_role != "Admin":
            messagebox.showwarning("Từ chối", "Chỉ Admin được Thêm/Sửa!")
            return

        top = ctk.CTkToplevel(self)
        top.title("Thông tin Lịch Khởi Hành")
        top.geometry("420x700")
        top.grab_set()

        entries = {}
        fields = [("ID", "Mã Lịch trình:"), 
                  ("DepDate", "Ngày khởi hành (YYYY-MM-DD):"), ("RetDate", "Ngày về (YYYY-MM-DD):"),
                  ("Max", "Số chỗ tối đa:"), ("Booked", "Số chỗ đã đặt:")]

        # ComboBox for Tour
        ctk.CTkLabel(top, text="Tour gốc:").pack(pady=(10,0), padx=20, anchor="w")
        tours_data = self.db.get_all_tours()
        tour_map = {f"{t[1]} (ID: {t[0]})": t[0] for t in tours_data}
        cb_tour = ctk.CTkComboBox(top, values=list(tour_map.keys()), width=380)
        cb_tour.pack(pady=2, padx=20)

        for key, label in fields:
            ctk.CTkLabel(top, text=label).pack(pady=(5,0), padx=20, anchor="w")
            ent = ctk.CTkEntry(top, width=380)
            ent.pack(pady=2, padx=20)
            entries[key] = ent

        # --- Price Policies ---
        price_frame = ctk.CTkFrame(top, fg_color="transparent")
        price_frame.pack(pady=(10,0), padx=20, fill="x")
        ctk.CTkLabel(price_frame, text="Chính sách giá (VNĐ)", font=ctk.CTkFont(weight="bold")).pack(anchor="w")

        price_entries = {}
        price_fields = [("adult", "Giá Người lớn:", "Người lớn"), 
                        ("child", "Giá Trẻ em:", "Trẻ em"), 
                        ("infant", "Giá Em bé:", "Em bé")]
        
        for key, label, p_type in price_fields:
            ctk.CTkLabel(top, text=label).pack(pady=(5,0), padx=20, anchor="w")
            ent = ctk.CTkEntry(top, width=380, placeholder_text="Bỏ trống nếu không áp dụng")
            ent.pack(pady=2, padx=20)
            price_entries[p_type] = ent
        # --- End Price Policies ---
        
        if data:
            # data = (s.id, s.tour_id, t.name, s.departure_date, s.return_date, s.price, s.max_slots, s.booked_slots, s.status)
            entries["ID"].insert(0, data[0]); entries["ID"].configure(state="disabled")
            cb_tour.set(f"{data[2]} (ID: {data[1]})")
            entries["DepDate"].insert(0, data[3])
            entries["RetDate"].insert(0, data[4] if data[4] else "")
            entries["Max"].insert(0, str(data[6]))
            entries["Booked"].insert(0, str(data[7]))
            if prices:
                price_entries["Người lớn"].insert(0, prices.get("Người lớn", ""))
                price_entries["Trẻ em"].insert(0, prices.get("Trẻ em", ""))
                price_entries["Em bé"].insert(0, prices.get("Em bé", ""))
        else:
            # Tự động điền ID, ngày hôm nay, số chỗ đã đặt = 0
            import datetime
            entries["ID"].insert(0, self.db.next_id("Schedules", "id", "SCH"))
            entries["ID"].configure(state="disabled")
            entries["Booked"].insert(0, "0")
            entries["DepDate"].insert(0, datetime.date.today().strftime("%Y-%m-%d"))

        # Trạng thái tự động tính từ ngày + số chỗ — không cần chọn tay

        def save():
            s_id         = entries["ID"].get()
            dep_date     = entries["DepDate"].get()
            ret_date     = entries["RetDate"].get()
            max_slots    = entries["Max"].get()
            booked_slots = entries["Booked"].get()
            tour_id      = tour_map.get(cb_tour.get())
            if not all([s_id, dep_date, max_slots, booked_slots]) or not tour_id:
                messagebox.showwarning("Lỗi", "Nhập đủ thông tin!"); return
            try:
                prices_dict = {}
                for p_type, ent in price_entries.items():
                    price_str = ent.get()
                    if price_str:
                        prices_dict[p_type] = int(price_str)
                if not prices_dict.get("Người lớn"):
                    messagebox.showwarning("Bắt buộc", "Giá Người lớn không được để trống!"); return
            except ValueError:
                messagebox.showerror("Lỗi", "Giá và Số chỗ phải là số nguyên!"); return

            if data:
                self.db.update_schedule(s_id, tour_id, dep_date, ret_date, int(max_slots), int(booked_slots), prices_dict)
            else:
                success, msg = self.db.add_schedule(s_id, tour_id, dep_date, ret_date, int(max_slots), int(booked_slots), prices_dict)
                if not success:
                    messagebox.showerror("Lỗi", msg); return

            top.destroy()
            self.load_data()

        ctk.CTkButton(top, text="LƯU", height=40, command=save).pack(pady=20)